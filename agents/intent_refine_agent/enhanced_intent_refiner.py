"""
Enhanced Intent Refiner Agent
增强版意图精化代理

核心功能：
1. 状态管理 - 接收existing_intent + conversation_history
2. 增量更新 - 只从最新对话提取新属性
3. 标题稳定性 - 保持title不变
4. 精确的属性分类 - 区分正面/负面新增属性
5. 逻辑整合 - 合并新旧属性

"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

# 尝试导入CAMEL框架
try:
    from camel.agents import ChatAgent
    from camel.messages import BaseMessage
    from camel.models import ModelFactory
    from camel.types import ModelType, ModelPlatformType, RoleType
    CAMEL_AVAILABLE = True
except ImportError:
    CAMEL_AVAILABLE = False
    print("CAMEL framework not available, using simple implementation")

logger = logging.getLogger(__name__)

@dataclass
class IncrementalAnalysis:
    """增量分析结果"""
    new_positive_attrs: List[str]
    new_negative_attrs: List[str]
    clarification_needed: bool = False
    response_message: str = ""
    confidence: float = 0.8

@dataclass
class FinalIntentResult:
    """最终意图结果"""
    intent: Dict[str, Any]
    message: str
    analysis: IncrementalAnalysis
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class EnhancedIntentRefiner:
    """增强版意图精化代理"""
    
    def __init__(self, use_ai: bool = True, model_type: str = "kimi-k2-0711-preview"):
        """
        初始化增强版意图精化代理
        
        Args:
            use_ai: 是否使用AI模型
            model_type: AI模型类型
        """
        self.use_ai = use_ai
        self.model_type = model_type
        self.agent = None
        
        if use_ai and CAMEL_AVAILABLE:
            self._init_camel_agent()
        
        logger.info(f"EnhancedIntentRefiner initialized, use_ai={use_ai}")
    
    def _init_camel_agent(self):
        """初始化CAMEL代理（使用Kimi API）"""
        try:
            model = ModelFactory.create(
                model_platform=ModelPlatformType.MOONSHOT,
                model_type=self.model_type,
            )
            
            system_message = BaseMessage.make_assistant_message(
                role_name="E-commerce Intent Analyst",
                content=self._get_enhanced_system_prompt()
            )
            
            self.agent = ChatAgent(
                system_message=system_message,
                model=model,
                message_window_size=10
            )
            
            logger.info("Enhanced CAMEL agent with Kimi API initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize CAMEL agent: {e}, falling back to simple mode")
            self.use_ai = False
    
    def _get_enhanced_system_prompt(self) -> str:
        """获取增强版系统提示词"""
        return """你是一个电商意图分析专家。你的任务是分析用户的最新对话，并根据【已有意图】和【完整对话历史】来更新用户的购买需求。

核心规则：
1. **保持标题稳定**：不要更改【已有意图】中的 `title` 字段，除非用户明确表示要买完全不同的东西（例如从"买电脑"变成"买手机"）。
2. **提取新属性**：只从【最新的用户对话】中提取新增的正面和负面需求。
3. **精确分类**：将新需求严格分为 new_positive_attrs（想要的特征）和 new_negative_attrs（不想要的特征）。
4. **输出为JSON**：严格按照指定的JSON格式返回你提取出的【新属性】。

分析思路：
- 对比【已有意图】中的 attrs，找出【最新对话】中的新增信息
- 正面需求：用户明确想要的特征（品牌、配置、功能等）
- 负面需求：用户明确不想要的特征（通常以"不要"、"别"、"不喜欢"等词开头）

输出格式（严格遵循）：
{
  "new_positive_attrs": ["具体的正面属性1", "正面属性2"],
  "new_negative_attrs": ["负面属性1", "负面属性2"],
  "clarification_needed": false,
  "response_message": "针对用户新增需求的回复消息"
}"""

    async def refine_intent_incremental(
        self,
        session_id: str,
        existing_intent: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        latest_message: Optional[str] = None
    ) -> FinalIntentResult:
        """
        增量式意图精化
        
        Args:
            session_id: 会话ID
            existing_intent: 现有意图信息
            conversation_history: 完整对话历史
            latest_message: 最新的用户消息（可选，从conversation_history自动提取）
            
        Returns:
            FinalIntentResult: 最终意图结果
        """
        try:
            # 自动提取最新用户消息
            if latest_message is None:
                latest_message = self._extract_latest_user_message(conversation_history)
            
            # 第2步：调用LLM进行增量分析
            if self.use_ai and self.agent:
                analysis = await self._ai_incremental_analysis(
                    existing_intent, conversation_history, latest_message
                )
            else:
                analysis = self._rule_based_incremental_analysis(
                    existing_intent, conversation_history, latest_message
                )
            
            # 第3步：逻辑整合 - 合并新旧属性
            final_intent = self._merge_intent_attributes(existing_intent, analysis)
            
            # 第4步：生成最终输出
            result = FinalIntentResult(
                intent=final_intent,
                message=analysis.response_message,
                analysis=analysis
            )
            
            logger.info(f"Intent refined for session {session_id}: "
                       f"+{len(analysis.new_positive_attrs)} positive, "
                       f"+{len(analysis.new_negative_attrs)} negative attrs")
            
            return result
            
        except Exception as e:
            logger.error(f"Enhanced intent refinement failed: {e}")
            # 出错时返回原始意图
            return FinalIntentResult(
                intent=existing_intent,
                message="抱歉，处理您的需求时出现了问题，请重新描述。",
                analysis=IncrementalAnalysis([], [], True, ""),
            )
    
    async def _ai_incremental_analysis(
        self,
        existing_intent: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        latest_message: str
    ) -> IncrementalAnalysis:
        """使用AI进行增量分析"""
        
        # 构建精确的Prompt
        prompt = f"""【已有意图】:
{json.dumps(existing_intent, ensure_ascii=False, indent=2)}

【完整对话历史】:
{json.dumps(conversation_history, ensure_ascii=False, indent=2)}

【最新的用户对话】:
"{latest_message}"

请根据【最新的用户对话】分析并输出新增的需求。严格按照JSON格式输出。"""

        try:
            user_message = BaseMessage.make_user_message(
                role_name="User",
                content=prompt
            )
            
            response = await self.agent.step(user_message)
            result_text = response.msg.content
            
            return self._parse_incremental_response(result_text)
            
        except Exception as e:
            logger.error(f"AI incremental analysis failed: {e}")
            raise
    
    def _rule_based_incremental_analysis(
        self,
        existing_intent: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        latest_message: str
    ) -> IncrementalAnalysis:
        """基于规则的增量分析"""
        
        existing_attrs = set(existing_intent.get("attrs", []))
        
        # 简单的关键词提取
        positive_keywords = self._extract_positive_keywords(latest_message)
        negative_keywords = self._extract_negative_keywords(latest_message)
        
        # 过滤掉已有的属性
        new_positive = [kw for kw in positive_keywords if kw not in existing_attrs]
        new_negative = [kw for kw in negative_keywords if f"NOT:{kw}" not in existing_attrs]
        
        # 生成回复消息
        message_parts = []
        if new_positive:
            message_parts.append(f"已为您添加{', '.join(new_positive)}的要求")
        if new_negative:
            message_parts.append(f"会为您排除{', '.join(new_negative)}的机型")
        
        response_message = "好的，" + "，".join(message_parts) + "。" if message_parts else "收到您的信息。"
        
        return IncrementalAnalysis(
            new_positive_attrs=new_positive,
            new_negative_attrs=new_negative,
            clarification_needed=False,
            response_message=response_message,
            confidence=0.7
        )
    
    def _merge_intent_attributes(
        self,
        existing_intent: Dict[str, Any],
        analysis: IncrementalAnalysis
    ) -> Dict[str, Any]:
        """第3步：逻辑整合 - 合并新旧属性"""
        
        # 创建最终的intent对象
        final_intent = {
            "title": existing_intent["title"],  # 直接使用旧的title
            "attrs": existing_intent.get("attrs", []).copy()  # 拷贝旧的attrs列表
        }
        
        # 添加新的正面属性
        final_intent["attrs"].extend(analysis.new_positive_attrs)
        
        # 添加新的负面属性（加上"NOT:"前缀）
        for neg_attr in analysis.new_negative_attrs:
            final_intent["attrs"].append(f"NOT:{neg_attr}")
        
        return final_intent
    
    def _extract_latest_user_message(self, conversation_history: List[Dict[str, str]]) -> str:
        """提取最新的用户消息"""
        for msg in reversed(conversation_history):
            if msg.get("sender") == "user" or msg.get("role") == "user":
                return msg.get("text", msg.get("content", ""))
        return ""
    
    def _extract_positive_keywords(self, text: str) -> List[str]:
        """提取正面关键词"""
        keywords = []
        text_lower = text.lower()
        
        # 品牌识别
        brands = ["苹果", "华为", "小米", "联想", "戴尔", "惠普", "华硕"]
        for brand in brands:
            if brand in text_lower:
                keywords.append(brand)
        
        # 配置识别
        import re
        memory_match = re.search(r'(\d+)g', text_lower)
        if memory_match:
            keywords.append(f"{memory_match.group(1)}G内存")
        
        # 其他特征词
        features = ["轻薄", "便携", "游戏", "办公", "学习", "商务", "高性能"]
        for feature in features:
            if feature in text:
                keywords.append(feature)
        
        return keywords
    
    def _extract_negative_keywords(self, text: str) -> List[str]:
        """提取负面关键词"""
        import re
        negative_keywords = []
        
        # 负面表达模式
        patterns = [
            r'不要(.+?)(?:[，。！？\s]|$)',
            r'不想要(.+?)(?:[，。！？\s]|$)',
            r'别(.+?)(?:[，。！？\s]|$)',
            r'不能(.+?)(?:[，。！？\s]|$)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                keyword = match.strip().replace("太", "").replace("的", "")
                if keyword and len(keyword) < 10:
                    negative_keywords.append(keyword)
        
        return negative_keywords
    
    def _parse_incremental_response(self, response_text: str) -> IncrementalAnalysis:
        """解析AI的增量分析响应"""
        try:
            # 尝试提取JSON
            if response_text.strip().startswith("{"):
                data = json.loads(response_text)
            else:
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                else:
                    raise ValueError("No JSON found")
            
            return IncrementalAnalysis(
                new_positive_attrs=data.get("new_positive_attrs", []),
                new_negative_attrs=data.get("new_negative_attrs", []),
                clarification_needed=data.get("clarification_needed", False),
                response_message=data.get("response_message", ""),
                confidence=0.9
            )
            
        except Exception as e:
            logger.error(f"Failed to parse incremental response: {e}")
            # 返回空分析结果
            return IncrementalAnalysis([], [], True, "抱歉，我没有理解您的需求，请重新描述。")
    
    def format_output(self, result: FinalIntentResult) -> str:
        """格式化输出为指定格式"""
        output_data = {
            "intent": result.intent,
            "message": result.message
        }
        
        return f"====agent gen intent info\n{json.dumps(output_data, ensure_ascii=False, indent=2)}"

# 便捷函数
async def refine_intent_enhanced(
    session_id: str,
    existing_intent: Dict[str, Any],
    conversation_history: List[Dict[str, str]],
    latest_message: Optional[str] = None,
    use_ai: bool = True
) -> str:
    """
    增强版意图精化函数
    
    Args:
        session_id: 会话ID
        existing_intent: 现有意图信息
        conversation_history: 完整对话历史
        latest_message: 最新用户消息
        use_ai: 是否使用AI
        
    Returns:
        str: 格式化的输出结果
    """
    refiner = EnhancedIntentRefiner(use_ai=use_ai)
    result = await refiner.refine_intent_incremental(
        session_id, existing_intent, conversation_history, latest_message
    )
    return refiner.format_output(result) 