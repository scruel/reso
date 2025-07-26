#!/usr/bin/env python3
"""
AI Agents系统的FastAPI后端接口
适配前端数据结构：items、dchain、message
使用增强版AI Agents系统
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

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入增强版系统
from agents.orchestrator.enhanced_multi_agent_orchestrator import (
    EnhancedMultiAgentOrchestrator, 
    create_enhanced_orchestrator
)
from agents.recorder_agent.camel_behavior_recorder import BehaviorRecorderAgent

# Pydantic模型定义
class ItemInfo(BaseModel):
    title: str = Field(..., description="产品标题")
    pic_url: str = Field(..., description="产品图片URL")
    price: Optional[str] = Field(None, description="产品价格")
    sales: Optional[str] = Field(None, description="销量信息")

class DecisionChain(BaseModel):
    topic: str = Field(..., description="决策主题")
    content: str = Field(..., description="决策内容")

class ChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")
    session_id: Optional[str] = Field(None, description="会话ID")

class ChatResponse(BaseModel):
    items: ItemInfo = Field(..., description="推荐的产品信息")
    dchain: List[DecisionChain] = Field(..., description="决策链")
    message: str = Field(..., description="AI回复消息")

# Mock产品数据
MOCK_PRODUCTS = [
    {
        "name": "iPhone 15 Pro",
        "image_url": "https://example.com/iphone15pro.jpg",
        "price": "¥7999",
        "sales": "10万+",
        "category": "手机"
    },
    {
        "name": "MacBook Air M3",
        "image_url": "https://example.com/macbook-air-m3.jpg",
        "price": "¥8999",
        "sales": "5万+",
        "category": "笔记本电脑"
    },
    {
        "name": "AirPods Pro 2",
        "image_url": "https://example.com/airpods-pro-2.jpg",
        "price": "¥1899",
        "sales": "20万+",
        "category": "耳机"
    },
    {
        "name": "iPad Pro M4",
        "image_url": "https://example.com/ipad-pro-m4.jpg",
        "price": "¥6799",
        "sales": "3万+",
        "category": "平板电脑"
    }
]

# 全局变量
orchestrator: Optional[EnhancedMultiAgentOrchestrator] = None
behavior_recorder: Optional[BehaviorRecorderAgent] = None

# FastAPI应用初始化
app = FastAPI(
    title="AI Agents系统API",
    description="基于增强版多智能体系统的产品推荐API",
    version="2.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化函数
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化AI Agents系统"""
    global orchestrator, behavior_recorder

    try:
        logger.info("正在初始化增强版AI Agents系统...")

        # 创建增强版协调器
        orchestrator = await create_enhanced_orchestrator(mode="enhanced")
        behavior_recorder = BehaviorRecorderAgent()

        # 记录新Agent状态
        if hasattr(orchestrator, 'new_agents'):
            logger.info(f"已注册的新Agent: {list(orchestrator.new_agents.keys())}")

        logger.info("增强版AI Agents系统初始化完成")

    except Exception as e:
        logger.error(f"AI Agents系统初始化失败: {e}")
        logger.warning("系统将以降级模式运行，使用mock数据")

# 辅助函数

def format_response_for_frontend(ai_result: Dict, user_message: str) -> ChatResponse:
    """格式化AI结果为标准响应格式"""
    try:
        if ai_result.get("success") and ai_result.get("product"):
            product = ai_result["product"]
            return ChatResponse(
                items=ItemInfo(
                    title=product.get("name", "推荐产品"),
                    pic_url=product.get("image_url", "https://via.placeholder.com/300"),
                    price=product.get("price", "价格待定"),
                    sales=product.get("sales", "新品")
                ),
                dchain=[
                    DecisionChain(topic="意图理解", content=ai_result.get("intent", "理解用户需求")),
                    DecisionChain(topic="产品推荐", content=f"基于您的需求推荐: {product.get('name', '产品')}")
                ],
                message=ai_result.get("message", "为您推荐这款产品")
            )
        else:
            import random
            product = random.choice(MOCK_PRODUCTS)
            return ChatResponse(
                items=ItemInfo(
                    title=product["name"],
                    pic_url=product["image_url"],
                    price=product["price"],
                    sales=product["sales"]
                ),
                dchain=[
                    DecisionChain(topic="系统提示", content="AI系统暂时不可用，为您推荐热门产品"),
                    DecisionChain(topic="产品选择", content=f"推荐{product['category']}: {product['name']}")
                ],
                message=f"为您推荐这款{product['category']}: {product['name']}"
            )
    except Exception as e:
        logger.error(f"格式化响应失败: {e}")
        default_product = MOCK_PRODUCTS[0]
        return ChatResponse(
            items=ItemInfo(
                title=default_product["name"],
                pic_url=default_product["image_url"],
                price=default_product["price"],
                sales=default_product["sales"]
            ),
            dchain=[
                DecisionChain(topic="系统提示", content="处理过程中出现错误"),
                DecisionChain(topic="默认推荐", content="使用默认推荐")
            ],
            message="抱歉处理过程中出现问题，为您推荐这款热门产品。"
        )

# 路由定义
@app.get("/")
async def root():
    return {"message": "AI Agents系统运行正常", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ai_system_ready": orchestrator is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/products")
async def get_products():
    return {"products": MOCK_PRODUCTS}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        logger.info(f"收到聊天请求: {request.message}")
        session_id = request.session_id or f"api_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

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

        response = format_response_for_frontend(ai_result, request.message)

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

        return response

    except Exception as e:
        logger.error(f"聊天接口处理失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = f"ws_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")

            if not message:
                continue

            logger.info(f"WebSocket收到消息: {message}")
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

            await websocket.send_json({
                "items": response.items.model_dump(),
                "dchain": [dc.model_dump() for dc in response.dchain],
                "message": response.message
            })

    except WebSocketDisconnect:
        logger.info(f"WebSocket连接断开: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket处理失败: {e}")
        await websocket.send_json({"error": f"处理失败: {str(e)}"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )