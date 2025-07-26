#!/usr/bin/env python3
"""
AI Agents系统的FastAPI后端接口
适配前端数据结构：items、dchain、message
使用mock产品数据
"""

import asyncio
import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.agent_util import initialize_agents

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from agents.orchestrator.multi_agent_orchestrator import MultiAgentOrchestrator
from agents.recorder_agent.camel_behavior_recorder import BehaviorRecorderAgent

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="Reso",
    description="基于多 Agent 协作智能导购助手",
    version="1.0.0"
)

# 添加跨域支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请设置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
orchestrator: Optional[MultiAgentOrchestrator] = None
behavior_recorder: Optional[BehaviorRecorderAgent] = None

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    logger.info("正在启动AI Agents后端服务...")
    success = await initialize_agents()
    if success:
        logger.info("AI Agents系统初始化成功")
    else:
        logger.warning("AI Agents系统初始化失败，将使用fallback模式")












@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "service": "Reso",
        "version": "1.0.0",
        "status": "running",
        "agents_ready": orchestrator is not None,
        "mock_products_count": len(MOCK_PRODUCTS)
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents_initialized": orchestrator is not None,
        "behavior_recorder_ready": behavior_recorder is not None,
        "mock_data_ready": True
    }



@app.get("/products")
async def get_products():
    """获取所有mock产品数据"""
    return {
        "products": MOCK_PRODUCTS,
        "count": len(MOCK_PRODUCTS)
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """主要的聊天接口"""
    try:
        logger.info(f"收到聊天请求: {request.message}")
        
        # 生成会话ID
        session_id = request.session_id or f"api_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 记录用户输入
        if behavior_recorder:
            try:
                await behavior_recorder.record_interaction({
                    "type": "user_input",
                    "session_id": session_id,
                    "user_id": "api_user",
                    "content": {"text": request.message},
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.warning(f"行为记录失败: {e}")
        
        # 尝试使用AI系统处理
        ai_result = {"success": False}
        if orchestrator:
            try:
                user_request = {
                    "content": request.message,
                    "type": "text",
                    "session_id": session_id
                }
                ai_result = await orchestrator.process_user_request(user_request)
                logger.info("AI系统处理成功")
            except Exception as e:
                logger.warning(f"AI系统处理失败，使用fallback: {e}")
        
        # 格式化为前端需要的格式
        response = format_response_for_frontend(ai_result, request.message)
        
        # 记录推荐结果
        if behavior_recorder:
            try:
                await behavior_recorder.record_purchase_journey({
                    "session_id": session_id,
                    "user_id": "api_user", 
                    "user_input": request.message,
                    "recommendations": [{"name": response.items.title}],
                    "selected_product": {"name": response.items.title},
                    "purchase_result": {"status": "api_recommended"}
                })
            except Exception as e:
                logger.warning(f"推荐记录失败: {e}")
        
        logger.info(f"成功处理聊天请求，返回: {response.items.title}")
        return response
        
    except Exception as e:
        logger.error(f"聊天接口处理失败: {e}")
        # 返回默认错误响应
        default_product = MOCK_PRODUCTS[0]
        return ChatResponse(
            items=ItemInfo(
                title=default_product["name"],
                pic_url=default_product["image_url"]
            ),
            dchain=[
                DecisionChain(topic="系统提示", content="处理过程中出现错误，使用默认推荐"),
                DecisionChain(topic="错误处理", content="系统正在自动恢复")
            ],
            message="抱歉处理过程中出现问题，为您推荐这款热门产品。"
        )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket实时聊天接口"""
    await websocket.accept()
    session_id = f"ws_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_json()
            message = data.get("message", "")
            
            if not message:
                continue
                
            logger.info(f"WebSocket收到消息: {message}")
            
            # 处理请求
            ai_result = {"success": False}
            if orchestrator:
                try:
                    user_request = {
                        "content": message,
                        "type": "text", 
                        "session_id": session_id
                    }
                    ai_result = await orchestrator.process_user_request(user_request)
                except Exception as e:
                    logger.warning(f"WebSocket AI处理失败: {e}")
            
            response = format_response_for_frontend(ai_result, message)
            
            # 发送响应
            await websocket.send_json({
                "items": response.items.model_dump(),
                "dchain": [dc.model_dump() for dc in response.dchain],
                "message": response.message
            })
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket连接断开: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket处理失败: {e}")
        await websocket.send_json({
            "error": f"处理失败: {str(e)}"
        })

if __name__ == "__main__":
    import uvicorn
    
    # 开发环境启动
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
