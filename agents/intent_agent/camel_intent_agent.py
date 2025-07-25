"""
基于CAMEL框架的理解用户意图Agent
负责解析用户输入（文本/语音/文档/链接），提取购买意图和需求
"""

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelType, ModelPlatformType, RoleType
from camel.configs import ChatGPTConfig
import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)

class IntentType(Enum):
    PRODUCT_SEARCH = "product_search"
    COMPARISON = "comparison"
    CONSULTATION = "consultation"
    COMPLAINT = "complaint"
    UNKNOWN = "unknown"

@dataclass
class UserIntent:
    intent_type: IntentType
    confidence: float
    entities: Dict[str, Any]
    user_requirements: Dict[str, Any]
    context: Dict[str, Any]

class IntentUnderstandingAgent:
    """基于CAMEL框架的用户意图理解Agent"""
    
    def __init__(self, agent_id: str = "intent_agent"):
        self.agent_id = agent_id
        
        # 设置Kimi API环境变量（CAMEL框架通过环境变量读取）
        kimi_key = os.getenv("KIMI_API_KEY", "")
        if kimi_key:
            os.environ['MOONSHOT_API_KEY'] = kimi_key  # CAMEL框架需要MOONSHOT_API_KEY
        
        # 配置模型参数
        model_config_dict = {
            'temperature': 0.3,
            'max_tokens': 1500
        }
        
        # 创建CAMEL Agent，使用Kimi模型
        self.camel_agent = ChatAgent(
            system_message=self._create_system_message(),
            model=ModelFactory.create(
                model_platform=ModelPlatformType.MOONSHOT,  # 使用Moonshot/Kimi
                model_type="kimi-k2-0711-preview",                   # 使用kimi-k2-0711-preview模型
                model_config_dict=model_config_dict
            ),
            message_window_size=10
        )
        
        logger.info(f"IntentUnderstandingAgent {agent_id} initialized with CAMEL framework")
    
    def _create_system_message(self) -> BaseMessage:
        """创建系统消息"""
        system_prompt = """
        你是一个专业的电商购物意图理解专家，专门分析用户的购买意图和需求。

        你的任务：
        1. 识别用户意图类型（商品搜索、比较、咨询、投诉等）
        2. 提取关键实体信息（品牌、价格、功能需求等）
        3. 理解用户的具体需求和偏好
        4. 分析用户的购买紧迫程度和决策阶段

        输出格式：
        {
            "intent_type": "product_search|comparison|consultation|complaint|unknown",
            "confidence": 0.0-1.0,
            "entities": {
                "product_category": "油烟机",
                "brand_preference": ["方太", "老板"],
                "price_range": {"min": 2000, "max": 4000},
                "features": ["大吸力", "静音", "易清洁"],
                "kitchen_size": "8平米",
                "style": "现代简约"
            },
            "user_requirements": {
                "priority_features": ["静音", "大吸力"],
                "must_have": ["预算3000以内"],
                "nice_to_have": ["智能控制", "自清洁"]
            },
            "context": {
                "urgency": "medium",
                "decision_stage": "research",
                "user_expertise": "beginner"
            }
        }

        特别注意：
        - 对于语音输入，要理解口语化表达
        - 对于文档内容，要提取装修相关的隐含需求
        - 对于链接内容，要分析页面信息推断用户意图
        """
        
        return BaseMessage(
            role_name="intent_understanding_expert",
            role_type=RoleType.ASSISTANT,
            meta_dict={},
            content=system_prompt
        )
    
    async def understand_intent(self, user_input: Dict) -> UserIntent:
        """理解用户意图的主方法"""
        try:
            # 构造用户消息
            user_message = self._construct_user_message(user_input)
            
            # 使用CAMEL Agent处理
            response = self.camel_agent.step(user_message)
            
            # 解析响应
            intent_data = self._parse_response(response.msg.content)
            
            return UserIntent(
                intent_type=IntentType(intent_data.get("intent_type", "unknown")),
                confidence=intent_data.get("confidence", 0.0),
                entities=intent_data.get("entities", {}),
                user_requirements=intent_data.get("user_requirements", {}),
                context=intent_data.get("context", {})
            )
            
        except Exception as e:
            logger.error(f"Intent understanding failed: {e}")
            return UserIntent(
                intent_type=IntentType.UNKNOWN,
                confidence=0.0,
                entities={},
                user_requirements={},
                context={"error": str(e)}
            )
    
    def _construct_user_message(self, user_input: Dict) -> BaseMessage:
        """构造用户消息"""
        content_type = user_input.get("type", "text")
        content = user_input.get("content", "")
        metadata = user_input.get("metadata", {})
        
        message_content = f"""
        用户输入类型: {content_type}
        
        内容: {content}
        
        附加信息: {json.dumps(metadata, ensure_ascii=False) if metadata else "无"}
        
        请分析用户的购买意图和需求，返回结构化的JSON格式结果。
        """
        
        return BaseMessage.make_user_message(
            role_name="user",
            content=message_content.strip()
        )
    
    def _parse_response(self, response_content: str) -> Dict:
        """解析CAMEL Agent的响应"""
        try:
            # 尝试直接解析JSON
            if response_content.strip().startswith('{'):
                return json.loads(response_content)
            
            # 如果不是纯JSON，尝试提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # 如果无法解析，返回默认结构
            return {
                "intent_type": "unknown",
                "confidence": 0.5,
                "entities": {},
                "user_requirements": {},
                "context": {"raw_response": response_content}
            }
            
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON response: {response_content}")
            return {
                "intent_type": "unknown", 
                "confidence": 0.3,
                "entities": {},
                "user_requirements": {},
                "context": {"parse_error": True}
            }
    
    async def refine_intent(self, initial_intent: UserIntent, additional_info: Dict) -> UserIntent:
        """根据额外信息精化意图理解"""
        refinement_message = BaseMessage.make_user_message(
            role_name="user",
            content=f"""
            基于之前的分析结果：
            {json.dumps(initial_intent.__dict__, ensure_ascii=False, default=str)}
            
            现在有额外信息：
            {json.dumps(additional_info, ensure_ascii=False)}
            
            请更新和精化用户意图分析，返回更准确的结果。
            """
        )
        
        response = self.camel_agent.step(refinement_message)
        refined_data = self._parse_response(response.msg.content)
        
        return UserIntent(
            intent_type=IntentType(refined_data.get("intent_type", initial_intent.intent_type.value)),
            confidence=refined_data.get("confidence", initial_intent.confidence),
            entities=refined_data.get("entities", initial_intent.entities),
            user_requirements=refined_data.get("user_requirements", initial_intent.user_requirements),
            context=refined_data.get("context", initial_intent.context)
        )
    
    def get_conversation_context(self) -> Dict:
        """获取对话上下文"""
        return {
            "agent_id": self.agent_id,
            "message_history": len(self.camel_agent.memory.messages),
            "last_response": self.camel_agent.memory.messages[-1].content if self.camel_agent.memory.messages else None
        }

# 对外接口
async def create_intent_agent(agent_id: str = "intent_agent") -> IntentUnderstandingAgent:
    """创建意图理解Agent实例"""
    return IntentUnderstandingAgent(agent_id)

if __name__ == "__main__":
    # 测试代码
    async def test_intent_agent():
        agent = await create_intent_agent()
        
        # 测试用例1：文本输入
        test_input = {
            "type": "text",
            "content": "我家新房装修，厨房8平米，预算3000元左右，希望噪音小一些，想买个油烟机",
            "metadata": {"source": "chat"}
        }
        
        intent = await agent.understand_intent(test_input)
        print("意图理解结果:")
        print(f"Intent Type: {intent.intent_type}")
        print(f"Confidence: {intent.confidence}")
        print(f"Entities: {json.dumps(intent.entities, ensure_ascii=False, indent=2)}")
        print(f"Requirements: {json.dumps(intent.user_requirements, ensure_ascii=False, indent=2)}")
        
        # 测试用例2：语音输入
        voice_input = {
            "type": "voice",
            "content": "嗯...那个...我想买个抽油烟机，家里厨房不大，大概六七平米吧，不要太吵的",
            "metadata": {"source": "voice", "duration": 8.5}
        }
        
        voice_intent = await agent.understand_intent(voice_input)
        print("\\n语音意图理解结果:")
        print(f"Intent Type: {voice_intent.intent_type}")
        print(f"Confidence: {voice_intent.confidence}")
    
  