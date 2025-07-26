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

# Mock产品数据
MOCK_PRODUCTS = [
    {
        "name": "美的CXW-200-DJ560R侧吸式油烟机",
        "price": 2899,
        "image_url": "https://example.com/images/meide_dj560r.jpg",
        "features": ["侧吸式", "20m³/min大吸力", "静音设计", "易清洁"],
        "suitable_for": ["8-15平米厨房", "预算3000以下", "追求静音"]
    },
    {
        "name": "老板CXW-200-67A7欧式油烟机",
        "price": 3299,
        "image_url": "https://example.com/images/robam_67a7.jpg", 
        "features": ["欧式设计", "22m³/min强劲吸力", "自动清洗", "触控面板"],
        "suitable_for": ["现代厨房", "预算3500以下", "追求品质"]
    },
    {
        "name": "方太CXW-200-EMC2T顶吸式油烟机",
        "price": 2699,
        "image_url": "https://example.com/images/fotile_emc2t.jpg",
        "features": ["顶吸式", "18m³/min吸力", "LED照明", "不锈钢机身"],
        "suitable_for": ["传统厨房", "预算2500-3000", "实用主义"]
    },
    {
        "name": "华帝CXW-238-i11083近吸式油烟机",
        "price": 2199,
        "image_url": "https://example.com/images/vatti_i11083.jpg",
        "features": ["近吸式", "16m³/min吸力", "超薄设计", "性价比高"],
        "suitable_for": ["小户型", "预算2500以下", "空间受限"]
    },
    {
        "name": "海尔CXW-200-C900T6U1智能油烟机",
        "price": 3599,
        "image_url": "https://example.com/images/haier_c900t6u1.jpg",
        "features": ["智能控制", "24m³/min超强吸力", "APP远程", "自动巡航"],
        "suitable_for": ["智能家居", "预算4000以下", "科技爱好者"]
    }
]

# 创建FastAPI应用
app = FastAPI(
    title="AI Agents油烟机推荐系统",
    description="基于多Agent协作的智能推荐系统",
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

# 请求和响应模型
class ChatRequest(BaseModel):
    message: str = Field(..., description="用户输入消息")
    session_id: Optional[str] = Field(None, description="会话ID，可选")

class ItemInfo(BaseModel):
    title: str = Field("", description="推荐产品标题")
    pic_url: str = Field("", description="产品图片URL")

class DecisionChain(BaseModel):
    topic: str = Field("", description="决策点主题")
    content: str = Field("", description="决策内容")

class ChatResponse(BaseModel):
    items: ItemInfo = Field(default_factory=ItemInfo, description="推荐产品信息")
    dchain: List[DecisionChain] = Field(default_factory=list, description="决策链")
    message: str = Field("", description="回复消息")

# 全局变量
orchestrator: Optional[MultiAgentOrchestrator] = None
behavior_recorder: Optional[BehaviorRecorderAgent] = None

async def initialize_agents():
    """初始化所有AI Agents"""
    global orchestrator, behavior_recorder
    
    try:
        logger.info("正在初始化AI Agents系统...")
        
        # 创建协调器
        orchestrator = MultiAgentOrchestrator()
        
        # 创建并注册所有Agent
        from agents.intent_agent.camel_intent_agent import create_intent_agent
        from agents.orchestrator.multi_agent_orchestrator import AgentType
        from agents.docas_agent.agent_core import create_docas_agent
        from agents.execution_agent.camel_execution_agent import ExecutionAgent
        from agents.check_agent.requirement_check_agent import RequirementCheckAgent
        
        # 注册各个Agent
        intent_agent = await create_intent_agent()
        orchestrator.register_agent(AgentType.INTENT_AGENT, intent_agent)
        
        docas_agent = await create_docas_agent()
        orchestrator.register_agent(AgentType.DOCAS_AGENT, docas_agent)
        
        execution_agent = ExecutionAgent()
        orchestrator.register_agent(AgentType.EXECUTION_AGENT, execution_agent)
        
        check_agent = RequirementCheckAgent()
        orchestrator.register_agent(AgentType.CHECK_AGENT, check_agent)
        
        # 创建行为记录器
        behavior_recorder = BehaviorRecorderAgent()
        
        logger.info("AI Agents系统初始化完成")
        return True
        
    except Exception as e:
        logger.error(f"AI Agents系统初始化失败: {e}")
        return False

def get_mock_recommendation(user_input: str) -> Dict:
    """基于用户输入返回mock推荐"""
    # 简单的关键词匹配逻辑
    user_lower = user_input.lower()
    
    if "预算" in user_input and ("2000" in user_input or "2500" in user_input):
        return MOCK_PRODUCTS[3]  # 华帝性价比款
    elif "静音" in user_input or "噪音" in user_input:
        return MOCK_PRODUCTS[0]  # 美的静音款
    elif "智能" in user_input or "app" in user_lower:
        return MOCK_PRODUCTS[4]  # 海尔智能款
    elif "3000" in user_input or "高端" in user_input:
        return MOCK_PRODUCTS[1]  # 老板高端款
    else:
        return MOCK_PRODUCTS[2]  # 方太中端款

def format_response_for_frontend(ai_result: Dict, user_input: str) -> ChatResponse:
    """将AI结果格式化为前端需要的格式"""
    try:
        # 如果AI处理成功，使用AI结果
        if ai_result.get("success"):
            result_data = ai_result.get("result", {})
            recommendation = result_data.get("recommendation", "")
            execution_status = result_data.get("execution_status", {})
            execution_history = execution_status.get("execution_history", [])
            user_intent = result_data.get("user_intent_summary", {})
            
            # 构建items（从AI结果或mock数据）
            items = ItemInfo()
            
            # 尝试从execution_history中提取产品信息
            selected_product = None
            if execution_history:
                last_execution = execution_history[-1].get("execution_result", {})
                if last_execution.get("success") and "recommendations" in last_execution:
                    recommendations = last_execution["recommendations"]
                    if recommendations:
                        selected_product = recommendations[0]
            
            # 如果AI没有返回具体产品，使用mock数据
            if not selected_product:
                selected_product = get_mock_recommendation(user_input)
            
            items.title = selected_product.get("name", "智能推荐油烟机")
            items.pic_url = selected_product.get("image_url", "")
            
            # 构建dchain（决策链）
            dchain = []
            
            # 添加需求理解
            if user_intent.get("intent_type"):
                dchain.append(DecisionChain(
                    topic="需求分析",
                    content=f"识别您的{user_intent['intent_type']}需求，AI理解置信度{user_intent.get('confidence', 0.8):.1f}"
                ))
            
            # 添加产品匹配分析
            price = selected_product.get("price", 0)
            features = selected_product.get("features", [])
            dchain.append(DecisionChain(
                topic="产品匹配",
                content=f"价格{price}元，主要特点：{', '.join(features[:3])}"
            ))
            
            # 添加执行历史中的关键决策点
            for i, history in enumerate(execution_history, 1):
                check_result = history.get("check_result", {})
                satisfaction_score = check_result.get("satisfaction_score", 0.8)
                
                dchain.append(DecisionChain(
                    topic=f"AI评估{i}",
                    content=f"满足度评分: {satisfaction_score:.1f}/1.0"
                ))
                
                # 添加改进建议
                suggestions = check_result.get("improvement_suggestions", [])
                if suggestions:
                    dchain.append(DecisionChain(
                        topic="优化建议", 
                        content="; ".join(suggestions[:2])
                    ))
                    break  # 只显示第一轮建议
            
            # 添加最终推荐理由
            suitable_for = selected_product.get("suitable_for", [])
            if suitable_for:
                dchain.append(DecisionChain(
                    topic="推荐理由",
                    content=f"适合：{', '.join(suitable_for)}"
                ))
            
            # 构建message
            if recommendation:
                message = recommendation
            else:
                message = f"基于您的需求分析，我推荐{selected_product['name']}。这款产品{', '.join(features[:2])}，售价{price}元，性价比很高。"
        
        else:
            # AI处理失败，使用fallback逻辑
            logger.warning("AI处理失败，使用fallback逻辑")
            selected_product = get_mock_recommendation(user_input)
            
            items = ItemInfo(
                title=selected_product["name"],
                pic_url=selected_product["image_url"]
            )
            
            dchain = [
                DecisionChain(topic="快速匹配", content="基于关键词快速匹配"),
                DecisionChain(topic="产品特点", content=f"主要特点：{', '.join(selected_product['features'][:2])}"),
                DecisionChain(topic="价格区间", content=f"售价{selected_product['price']}元")
            ]
            
            message = f"为您推荐{selected_product['name']}，售价{selected_product['price']}元。主要特点：{', '.join(selected_product['features'][:3])}。"
        
        # 确保dchain不为空
        if not dchain:
            dchain = [
                DecisionChain(topic="AI分析", content="正在智能分析您的需求"),
                DecisionChain(topic="产品匹配", content="基于多维度算法推荐最适合的产品")
            ]
        
        return ChatResponse(
            items=items,
            dchain=dchain,
            message=message
        )
        
    except Exception as e:
        logger.error(f"格式化响应失败: {e}")
        # 返回默认响应
        default_product = MOCK_PRODUCTS[0]
        return ChatResponse(
            items=ItemInfo(
                title=default_product["name"],
                pic_url=default_product["image_url"]
            ),
            dchain=[
                DecisionChain(topic="系统提示", content="使用默认推荐算法"),
                DecisionChain(topic="产品信息", content=f"推荐{default_product['name']}")
            ],
            message=f"系统为您推荐{default_product['name']}，这是一款性能稳定的产品。"
        )

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
        "service": "AI Agents油烟机推荐系统",
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