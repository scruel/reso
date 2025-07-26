"""
Simple Intent Refiner Agent
简单的意图精化代理

功能：
- 接收原有的intent信息和历史对话
- 保持原有intent title不变
- 基于历史对话生成优化的attrs和可选message
- 输出标准格式的精化结果

设计理念：简单能用，不依赖复杂编排
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# 尝试导入CAMEL，如果没有则使用简单实现
try:
    from camel.agents import ChatAgent
    from camel.messages import BaseMessage
    from camel.models import ModelFactory
    from camel.types import ModelType, ModelPlatformType, RoleType
    from camel.configs import ChatGPTConfig
    CAMEL_AVAILABLE = True
except ImportError:
    CAMEL_AVAILABLE = False
    print("CAMEL framework not available, using simple implementation")

logger = logging.getLogger(__name__)

@dataclass
class IntentInfo:
    """意图信息数据结构"""
    title: str
    attrs: List[str]

@dataclass
class RefinedResult:
    """精化结果数据结构"""
    intent: IntentInfo
    message: str
    confidence: float = 0.8
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class SimpleIntentRefiner:
    """简单的意图精化代理"""
    
    def __init__(self, use_ai: bool = True, model_type: str = "kimi-k2-0711-preview"):
        """
        初始化意图精化代理
        
        Args:
            use_ai: 是否使用AI模型，False则使用规则方法
            model_type: AI模型类型
        """
        self.use_ai = use_ai
        self.model_type = model_type
        self.agent = None
        
        if use_ai and CAMEL_AVAILABLE:
            self._init_camel_agent()
        
        logger.info(f"SimpleIntentRefiner initialized, use_ai={use_ai}")
    
    def _init_camel_agent(self):
        """初始化CAMEL代理（使用Kimi API）"""
        try:
            # 使用Kimi Moonshot API
            model = ModelFactory.create(
                model_platform=ModelPlatformType.MOONSHOT,
                model_type=self.model_type,  # 使用指定的Kimi模型
            )
            
            system_message = BaseMessage.make_assistant_message(
                role_name="Intent Refiner",
                content=self._get_system_prompt()
            )
            
            self.agent = ChatAgent(
                system_message=system_message,
                model=model,
                message_window_size=10
            )
            
            logger.info("CAMEL agent with Kimi API initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize CAMEL agent with Kimi: {e}, falling back to simple mode")
            self.use_ai = False
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个意图精化专家。你的任务是：

1. 接收原有的intent信息（title和attrs）和历史对话
2. 保持原有的intent title完全不变
3. 基于历史对话内容，优化attrs属性列表
4. 如果需要，生成一个简短的辅助message

规则：
- 绝对不能修改intent title
- attrs应该是具体的、有用的属性关键词
- message应该简短、有帮助，可以为空
- 输出必须是标准JSON格式

输出格式：
{
  "intent": {
    "title": "原title不变",
    "attrs": ["优化后的属性1", "属性2", "属性3"]
  },
  "message": "可选的辅助信息"
}"""

    async def refine_intent(
        self,
        original_intent: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None
    ) -> RefinedResult:
        """
        精化意图信息
        
        Args:
            original_intent: 原始意图信息，包含title和attrs
            conversation_history: 历史对话，格式：[{"role": "user/assistant", "content": "..."}]
            context: 额外上下文信息
            
        Returns:
            RefinedResult: 精化后的意图结果
        """
        try:
            if self.use_ai and self.agent:
                return await self._ai_refine(original_intent, conversation_history, context)
            else:
                return self._rule_based_refine(original_intent, conversation_history, context)
                
        except Exception as e:
            logger.error(f"Intent refinement failed: {e}")
            # 出错时返回原始意图
            return RefinedResult(
                intent=IntentInfo(
                    title=original_intent.get("title", ""),
                    attrs=original_intent.get("attrs", [])
                ),
                message="",
                confidence=0.5
            )
    
    async def _ai_refine(
        self,
        original_intent: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None
    ) -> RefinedResult:
        """使用AI模型进行意图精化"""
        
        # 构建输入消息
        input_data = {
            "original_intent": original_intent,
            "conversation_history": conversation_history[-5:],  # 只取最近5轮对话
            "context": context or {}
        }
        
        prompt = f"""请精化以下意图信息：

原始意图：
{json.dumps(original_intent, ensure_ascii=False, indent=2)}

最近的对话历史：
{self._format_conversation(conversation_history[-5:])}

请优化attrs属性，生成可选message，但保持title不变。
输出标准JSON格式。"""

        try:
            user_message = BaseMessage.make_user_message(
                role_name="User",
                content=prompt
            )
            
            response = await self.agent.step(user_message)
            result_text = response.msg.content
            
            # 解析AI响应
            return self._parse_ai_response(result_text, original_intent)
            
        except Exception as e:
            logger.error(f"AI refinement failed: {e}")
            raise
    
    def _rule_based_refine(
        self,
        original_intent: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None
    ) -> RefinedResult:
        """基于规则的意图精化"""
        
        original_title = original_intent.get("title", "")
        original_attrs = original_intent.get("attrs", [])
        
        # 从对话历史中提取关键词
        conversation_text = " ".join([
            msg.get("content", "") 
            for msg in conversation_history[-3:]  # 最近3轮对话
        ])
        
        # 简单的关键词提取和属性优化
        refined_attrs = self._extract_keywords(conversation_text, original_attrs)
        
        # 生成简单的message
        message = self._generate_simple_message(original_title, refined_attrs, conversation_history)
        
        return RefinedResult(
            intent=IntentInfo(
                title=original_title,  # 保持不变
                attrs=refined_attrs
            ),
            message=message,
            confidence=0.7
        )
    
    def _extract_keywords(self, text: str, original_attrs: List[str]) -> List[str]:
        """从文本中提取关键词，优化属性列表"""
        text_lower = text.lower()
        
        # 常见的产品属性关键词
        common_attrs = [
            "价格", "品牌", "型号", "颜色", "尺寸", "材质", "功能", "性能",
            "质量", "评价", "销量", "折扣", "配送", "售后", "参数", "规格"
        ]
        
        # 保留原有属性
        refined_attrs = list(original_attrs)
        
        # 从对话中发现新属性
        for attr in common_attrs:
            if attr in text_lower and attr not in refined_attrs:
                refined_attrs.append(attr)
        
        # 限制属性数量
        return refined_attrs[:8]
    
    def _generate_simple_message(
        self,
        title: str,
        attrs: List[str],
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """生成简单的辅助消息"""
        
        if len(conversation_history) == 0:
            return ""
        
        # 如果对话中提到了具体需求，生成相应message
        latest_user_msg = ""
        for msg in reversed(conversation_history):
            if msg.get("role") == "user":
                latest_user_msg = msg.get("content", "")
                break
        
        if "推荐" in latest_user_msg or "介绍" in latest_user_msg:
            return f"基于您的{title}需求，我为您精选了相关产品"
        elif "对比" in latest_user_msg or "比较" in latest_user_msg:
            return f"我来为您对比分析{title}相关产品"
        elif "价格" in latest_user_msg or "多少钱" in latest_user_msg:
            return f"为您查找{title}的价格信息"
        else:
            return ""
    
    def _format_conversation(self, conversation_history: List[Dict[str, str]]) -> str:
        """格式化对话历史"""
        formatted = []
        for i, msg in enumerate(conversation_history):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)
    
    def _parse_ai_response(self, response_text: str, original_intent: Dict[str, Any]) -> RefinedResult:
        """解析AI响应"""
        try:
            # 尝试直接解析JSON
            if response_text.strip().startswith("{"):
                result_data = json.loads(response_text)
            else:
                # 尝试提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result_data = json.loads(json_match.group())
                else:
                    raise ValueError("No JSON found in response")
            
            # 确保title保持不变
            intent_data = result_data.get("intent", {})
            intent_data["title"] = original_intent.get("title", "")
            
            return RefinedResult(
                intent=IntentInfo(
                    title=intent_data.get("title", ""),
                    attrs=intent_data.get("attrs", [])
                ),
                message=result_data.get("message", ""),
                confidence=0.9
            )
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            # 解析失败时返回原始意图
            return RefinedResult(
                intent=IntentInfo(
                    title=original_intent.get("title", ""),
                    attrs=original_intent.get("attrs", [])
                ),
                message="",
                confidence=0.6
            )
    
    def format_output(self, result: RefinedResult) -> str:
        """格式化输出为指定格式"""
        output_data = {
            "intent": {
                "title": result.intent.title,
                "attrs": result.intent.attrs
            },
            "message": result.message
        }
        
        return f"====agent gen intent info\n{json.dumps(output_data, ensure_ascii=False, indent=2)}"

# 便捷函数
async def refine_intent_simple(
    original_intent: Dict[str, Any],
    conversation_history: List[Dict[str, str]],
    use_ai: bool = True
) -> str:
    """
    简单的意图精化函数
    
    Args:
        original_intent: 原始意图信息
        conversation_history: 对话历史
        use_ai: 是否使用AI
        
    Returns:
        str: 格式化的输出结果
    """
    refiner = SimpleIntentRefiner(use_ai=use_ai)
    result = await refiner.refine_intent(original_intent, conversation_history)
    return refiner.format_output(result)

# 同步版本
def refine_intent_sync(
    original_intent: Dict[str, Any],
    conversation_history: List[Dict[str, str]],
    use_ai: bool = False  # 同步版本默认不使用AI
) -> str:
    """
    同步版本的意图精化函数
    
    Args:
        original_intent: 原始意图信息
        conversation_history: 对话历史
        use_ai: 是否使用AI
        
    Returns:
        str: 格式化的输出结果
    """
    refiner = SimpleIntentRefiner(use_ai=use_ai)
    result = refiner._rule_based_refine(original_intent, conversation_history)
    return refiner.format_output(result) 