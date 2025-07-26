#!/usr/bin/env python3
"""
AI Agents系统的FastAPI后端接口
适配前端数据结构：items、dchain、message
使用增强版AI Agents系统
"""

import asyncio
import json
import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from tools.psql.dialog_crud import DialogCRUD
from tools.weaviate import weaviate_query
from tools.weaviate.weaviate_query import query_good

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from tools.rag.qwen_embedding import KimiGPTService, QwenEmbeddingService
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("DASHSCOPE_API_KEY")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入增强版系统
from agents.orchestrator.enhanced_multi_agent_orchestrator import (
    EnhancedMultiAgentOrchestrator, 
    create_enhanced_orchestrator
)
from agents.recorder_agent.camel_behavior_recorder import BehaviorRecorderAgent

kimi = KimiGPTService()
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

@app.get("/api/vibe")
async def vibe(query: Optional[str] = None):
    crud = DialogCRUD()
    try:
      # agent
      pass
    except:
      pass
    try:
        prompt = """
你是一位专业的商品导购，你需要识别用户的选购意图以帮助用户决策，用户会给你提供原有意图识别结果和历史对话信息。无非必要，请绝对不能更改原有的意图标题。你还需要生成一句 message，用于提示用户一些挑选中的关键缺失信息，不多于 200 字。最后用户会给出最新的文本消息。

## 输出示例及格式
```
{
        "intent": {
            "title": "充电宝",
            "attrs": ["安全", "可靠", "白色"],
            "stop_words": ["黑色"]
        },
        "message": f"结合近期的新闻信息，建议需要进一步确定充电宝是否有 3C 标识，有需要你可以直接告诉我！",
}
```

## 注意事项
- 请严格按照输出示例的格式输出，不能有任何额外的内容。
- 保持意图的连贯性和一致性。
""".strip()
        all_messages = '\n'.join(crud.get_all_messages())
        if all_messages:
            prompt += "\n\n## 历史对话信息" + all_messages
        intent_info = crud.get_last_intent_info()
        if intent_info:
            prompt += "\n\n## 原有意图识别结果\n子类目：" + intent_info['intend_title']
            prompt += '\n属性：' + ','.join(intent_info['intend_attrs'])
            prompt += '\停用词：' + ','.join(intent_info['intend_stop_words'])
        prompt += '\n\n===' + query
        res = kimi.generate(prompt)
        res = json.loads(res)
        # check if format good
        if 'intent' not in res or 'message' not in res:
            raise Exception('生成格式错误...')
        if 'title' not in res['intent']:
            raise Exception('生成格式错误...')
        if 'attrs' not in res['intent']:
            raise Exception('生成格式错误...')
        crud.insert_dialog(
            message=query,
            intend_title=res['intent']['title'],
            intend_attrs=res['intent']['attrs'],
            intend_stop_words=res['intent']['stop_words'],
            reply=res['message']
        )
        res['status'] = 0
        return res
    except Exception as e:
      print(e)
      return {'status': 500, 'message': "vibe 不了一点，请再试试吧！"}

@app.post("/api/clear")
async def clear():
    return {
    "status": 0
    }

@app.get("/api/thread")
async def thread(tid: int):
    try:
        prompt  = """
        ===
        请你担任一名专业的商品导购，商场提出两点和场景点，我会给你商品的详细描述，请根据描述生成一个商品的简要概述，其中请考虑用户会如何做决策，不多于 50 字。
""".strip()
        print(tid)
        good = query_good(tid)
        desc = kimi.generate(good['detail'] + prompt)
        
        return {
          "title": good['name'],
          "pic_url": good['picUrl'],
          "price": good['price'],
          "dchain": {
              "id": tid,
              "description": desc
          },
          "reference_links": [],
          "status": 0
      }
    except Exception as e:
        print(e)
        return {'status': 500, 'message': "商品不存在"}

@app.get("/api/products")
async def products():
    crud = DialogCRUD()
    try:
      # agent
      pass
    except:
      pass
    try:
        prompt = """
你是一位 weaviate 专家，正在辅助一位电商导购筛选和获取商品列表。weaviate 中存储的是商品的详细描述信息，导购会将用户的历史对话信息提供给你，其中包含短关键词及长句。导购也可能会为你提供当前用户的子类目，你需要理解并识别用户的主要选购意图，并且拆解出用于执行 weaviate 的 query，并且解析出一些关键词，用于过滤用户不想要的商品。

## 输出示例及格式
```
{
  "query": "小米充电宝白色"
  "stop_words": ["黑色"]
}
```

## 注意事项
请严格按照输出示例的格式输出，不能有任何额外的内容。
""".strip()
        all_messages = '\n'.join(crud.get_all_messages())
        if all_messages:
            prompt += "\n\n## 历史对话信息" + all_messages
        intent_info = crud.get_last_intent_info()
        if intent_info:
            prompt += "\n\n## 原有意图识别结果\n子类目：" + intent_info['intend_title']
            prompt += '\n属性：' + ','.join(intent_info['intend_attrs'])
            prompt += '\停用词：' + ','.join(intent_info['intend_stop_words'])
        res = kimi.generate(prompt)
        res = json.loads(res)
        # check if format good
        if 'query' not in res or 'stop_words' not in res:
            raise Exception('生成格式错误...')
        res_list = weaviate_query.query(res['query'])
        res["threas"] = []
        for item in res_list:
            item = item.properties
            res["threas"].append(
                {
                    "id": item['goodId'],
                    "good": {
                        "id": 0,
                        "title": item['name'],
                        "pic_url": item['picUrl'],
                        "brand": item['brandName'],
                        "category": item['catagory'],
                        "categoryColor": item['subCatagory'],
                        "price": item['price']
                    },
                    "dchain": {
                        "tbn_url": "",
                        "user_nick": "test_user",
                        "user_pic_url": ""
                    }
                }
            )
        res['status'] = 0
        return res
    except Exception as e:
      print(e)
      return {'status': 500, 'message': "vibe 不了一点，请再试试吧！"}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
