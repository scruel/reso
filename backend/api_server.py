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

# 全局变量
orchestrator: Optional[EnhancedMultiAgentOrchestrator] = None
behavior_recorder: Optional[BehaviorRecorderAgent] = None

# FastAPI应用初始化
app = FastAPI(
    title="AI Agents系统API",
    description="基于增强版多智能体系统的智能导购API",
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

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ai_system_ready": orchestrator is not None,
        "timestamp": datetime.now().isoformat()
    }
    
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
