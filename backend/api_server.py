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

# @app.on_event("startup")
# async def startup_event():
#     """应用启动时初始化"""
#     logger.info("正在启动AI Agents后端服务...")
#     success = await initialize_agents()
#     if success:
#         logger.info("AI Agents系统初始化成功")
#     else:
#         logger.warning("AI Agents系统初始化失败，将使用fallback模式")


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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
