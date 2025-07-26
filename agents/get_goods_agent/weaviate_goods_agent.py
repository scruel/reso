"""
Weaviate Goods Agent
Weaviate商品获取AI代理

功能：
- 理解用户选购意图和历史对话
- 拆解生成Weaviate查询语句
- 提取过滤关键词（用户不想要的商品）
- 使用Qwen-3模型进行意图理解和查询生成
- 支持PostgreSQL/Weaviate数据操作

设计理念：专业的Weaviate专家，简单能用
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

# 尝试导入CAMEL框架，支持Qwen模型
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
class WeaviateQuery:
    """Weaviate查询结构"""
    query: str
    limit: int = 10
    filters: Dict[str, Any] = None
    
@dataclass
class GoodsResult:
    """商品获取结果"""
    intent: Dict[str, Any]
    message: str
    status: int = 0
    weaviate_query: Optional[WeaviateQuery] = None
    banned_keywords: List[str] = None
    confidence: float = 0.8

class WeaviateGoodsAgent:
    """Weaviate商品获取AI代理"""
    
    def __init__(self, use_ai: bool = True, model_type: str = "qwen-turbo"):
        """
        初始化Weaviate商品代理
        
        Args:
            use_ai: 是否使用AI模型
            model_type: AI模型类型，支持Qwen系列
        """
        self.use_ai = use_ai
        self.model_type = model_type
        self.agent = None
        
        if use_ai and CAMEL_AVAILABLE:
            self._init_ai_agent()
        
        logger.info(f"WeaviateGoodsAgent initialized, use_ai={use_ai}")
    
    def _init_ai_agent(self):
        """初始化AI代理（使用Qwen模型）"""
        try:
            # 使用Qwen模型 - 支持qwen-turbo或其他qwen系列
            model = ModelFactory.create(
                model_platform=ModelPlatformType.OPENAI,  # 通过OpenAI兼容接口
                model_type=self.model_type,
            )
            
            system_message = BaseMessage.make_assistant_message(
                role_name="Weaviate Expert",
                content=self._get_system_prompt()
            )
            
            self.agent = ChatAgent(
                system_message=system_message,
                model=model,
                message_window_size=15
            )
            
            logger.info("Qwen AI agent initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize AI agent: {e}, falling back to rule mode")
            self.use_ai = False
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位专业的Weaviate数据库专家，专门为电商导购系统提供商品查询服务。

你的任务：
1. 理解用户的历史对话和选购意图
2. 生成精确的Weaviate查询语句
3. 提取用户不想要的商品关键词（banned keywords）
4. 输出标准格式的查询结果

技能要点：
- 深度理解电商场景下的用户需求
- 精通Weaviate向量数据库查询语法
- 能够从对话中提取关键商品属性
- 识别用户的排除偏好（不想要的特征）

查询生成规则：
- 使用语义搜索匹配用户意图
- 结合类目信息精确定位
- 考虑价格、品牌、功能等过滤条件
- 排除用户明确不想要的特征

输出格式：
{
  "intent": {
    "title": "用户选购意图描述",
    "attrs": ["属性1", "属性2", "属性3"]
  },
  "message": "查询说明或建议",
  "status": 0
}

记住：专注于理解用户真实需求，生成高质量的Weaviate查询。"""

    async def get_goods(
        self,
        conversation_history: List[Dict[str, str]],
        subcategory: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> GoodsResult:
        """
        获取商品 - 主要入口函数
        
        Args:
            conversation_history: 用户历史对话
            subcategory: 用户当前子类目
            user_context: 额外的用户上下文
            
        Returns:
            GoodsResult: 包含意图、查询、过滤词的结果
        """
        try:
            if self.use_ai and self.agent:
                return await self._ai_get_goods(conversation_history, subcategory, user_context)
            else:
                return self._rule_based_get_goods(conversation_history, subcategory, user_context)
                
        except Exception as e:
            logger.error(f"Get goods failed: {e}")
            return GoodsResult(
                intent={"title": "商品查询", "attrs": []},
                message=f"查询处理出错: {str(e)}",
                status=1
            )
    
    async def _ai_get_goods(
        self,
        conversation_history: List[Dict[str, str]],
        subcategory: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> GoodsResult:
        """使用AI模型进行商品获取"""
        
        # 构建输入上下文
        context_info = {
            "conversation_history": conversation_history[-8:],  # 最近8轮对话
            "subcategory": subcategory,
            "user_context": user_context or {}
        }
        
        prompt = f"""作为Weaviate专家，请分析以下电商导购场景：

对话历史：
{self._format_conversation(conversation_history[-8:])}

用户当前子类目：{subcategory or '未指定'}

请执行以下任务：
1. 理解用户的主要选购意图
2. 提取关键商品属性
3. 识别用户不想要的特征（banned keywords）
4. 生成Weaviate查询建议

输出标准JSON格式的结果。"""

        try:
            user_message = BaseMessage.make_user_message(
                role_name="E-commerce Assistant",
                content=prompt
            )
            
            response = await self.agent.step(user_message)
            result_text = response.msg.content
            
            # 解析AI响应并生成Weaviate查询
            return self._parse_ai_response(result_text, conversation_history, subcategory)
            
        except Exception as e:
            logger.error(f"AI processing failed: {e}")
            raise
    
    def _rule_based_get_goods(
        self,
        conversation_history: List[Dict[str, str]],
        subcategory: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> GoodsResult:
        """基于规则的商品获取"""
        
        # 合并所有对话文本
        conversation_text = " ".join([
            msg.get("content", "") 
            for msg in conversation_history[-5:]
        ])
        
        # 提取用户意图
        intent = self._extract_intent(conversation_text, subcategory)
        
        # 生成Weaviate查询
        weaviate_query = self._generate_weaviate_query(conversation_text, subcategory)
        
        # 提取禁用关键词
        banned_keywords = self._extract_banned_keywords(conversation_text)
        
        # 生成消息
        message = self._generate_message(intent, len(banned_keywords))
        
        return GoodsResult(
            intent=intent,
            message=message,
            status=0,
            weaviate_query=weaviate_query,
            banned_keywords=banned_keywords
        )
    
    def _extract_intent(self, text: str, subcategory: Optional[str] = None) -> Dict[str, Any]:
        """提取用户意图"""
        text_lower = text.lower()
        
        # 基础意图识别
        if subcategory:
            title = f"选购{subcategory}"
        elif "油烟机" in text_lower:
            title = "选购油烟机"
        elif "手机" in text_lower:
            title = "选购手机"
        elif "电脑" in text_lower or "笔记本" in text_lower:
            title = "选购电脑"
        elif "洗衣机" in text_lower:
            title = "选购洗衣机"
        else:
            title = "商品查询"
        
        # 提取属性
        attrs = []
        
        # 价格相关
        if re.search(r'\d+元|预算|价格|多少钱', text_lower):
            attrs.append("价格")
        
        # 品牌相关
        brands = ["华为", "小米", "苹果", "美的", "海尔", "格力", "老板", "方太"]
        for brand in brands:
            if brand in text_lower:
                attrs.append("品牌")
                break
        
        # 功能属性
        features = ["静音", "节能", "省电", "智能", "高清", "快充", "大容量", "易清洁"]
        for feature in features:
            if feature in text_lower:
                attrs.append(feature)
        
        return {
            "title": title,
            "attrs": list(set(attrs))  # 去重
        }
    
    def _generate_weaviate_query(self, text: str, subcategory: Optional[str] = None) -> WeaviateQuery:
        """生成Weaviate查询"""
        
        # 构建基础查询
        if subcategory:
            query_text = f"{subcategory} {text}"
        else:
            query_text = text
        
        # 提取限制数量
        limit = 10
        limit_match = re.search(r'(\d+)个|(\d+)款|top(\d+)', text.lower())
        if limit_match:
            limit = int(limit_match.group(1) or limit_match.group(2) or limit_match.group(3))
            limit = min(limit, 50)  # 最大50个
        
        # 构建过滤条件
        filters = {}
        
        # 价格过滤
        price_match = re.search(r'(\d+)(?:元|块钱)以下|预算(\d+)', text.lower())
        if price_match:
            price_limit = int(price_match.group(1) or price_match.group(2))
            filters["price"] = {"operator": "LessThan", "valueNumber": price_limit}
        
        # 类目过滤
        if subcategory:
            filters["category"] = {"operator": "Equal", "valueText": subcategory}
        
        return WeaviateQuery(
            query=query_text.strip(),
            limit=limit,
            filters=filters if filters else None
        )
    
    def _extract_banned_keywords(self, text: str) -> List[str]:
        """提取用户不想要的关键词"""
        text_lower = text.lower()
        banned = []
        
        # 明确的否定表达
        negative_patterns = [
            r'不要(.+?)(?:[，。！？\s]|$)',
            r'不想要(.+?)(?:[，。！？\s]|$)',
            r'除了(.+?)(?:[，。！？\s]|$)',
            r'别(.+?)(?:[，。！？\s]|$)',
            r'不喜欢(.+?)(?:[，。！？\s]|$)',
            r'不考虑(.+?)(?:[，。！？\s]|$)'
        ]
        
        for pattern in negative_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                keyword = match.strip()
                if keyword and len(keyword) < 10:  # 避免过长的匹配
                    banned.append(keyword)
        
        # 常见的排除词
        common_excludes = ["便宜", "低端", "劣质", "假货", "二手"]
        for exclude in common_excludes:
            if f"不要{exclude}" in text_lower or f"不{exclude}" in text_lower:
                banned.append(exclude)
        
        return list(set(banned))  # 去重
    
    def _generate_message(self, intent: Dict[str, Any], banned_count: int) -> str:
        """生成查询消息"""
        title = intent.get("title", "商品查询")
        attrs = intent.get("attrs", [])
        
        message_parts = [f"正在为您查询{title}"]
        
        if attrs:
            message_parts.append(f"，关注{', '.join(attrs[:3])}")
        
        if banned_count > 0:
            message_parts.append(f"，已排除{banned_count}个不符合要求的特征")
        
        return "".join(message_parts)
    
    def _format_conversation(self, conversation_history: List[Dict[str, str]]) -> str:
        """格式化对话历史"""
        formatted = []
        for msg in conversation_history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)
    
    def _parse_ai_response(
        self, 
        response_text: str, 
        conversation_history: List[Dict[str, str]], 
        subcategory: Optional[str]
    ) -> GoodsResult:
        """解析AI响应"""
        try:
            # 尝试直接解析JSON
            if response_text.strip().startswith("{"):
                result_data = json.loads(response_text)
            else:
                # 提取JSON部分
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result_data = json.loads(json_match.group())
                else:
                    raise ValueError("No JSON found in AI response")
            
            # 提取结果
            intent = result_data.get("intent", {"title": "AI查询", "attrs": []})
            message = result_data.get("message", "AI查询处理完成")
            status = result_data.get("status", 0)
            
            # 基于AI结果生成Weaviate查询
            conversation_text = " ".join([msg.get("content", "") for msg in conversation_history[-3:]])
            weaviate_query = self._generate_weaviate_query(conversation_text, subcategory)
            banned_keywords = self._extract_banned_keywords(conversation_text)
            
            return GoodsResult(
                intent=intent,
                message=message,
                status=status,
                weaviate_query=weaviate_query,
                banned_keywords=banned_keywords,
                confidence=0.9
            )
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            # 回退到规则方法
            return self._rule_based_get_goods(conversation_history, subcategory)
    
    def format_output(self, result: GoodsResult) -> str:
        """格式化输出为指定格式"""
        output_data = {
            "intent": result.intent,
            "message": result.message,
            "status": result.status
        }
        
        return f"====agent gen query\n{json.dumps(output_data, ensure_ascii=False, indent=2)}"
    
    def get_weaviate_query_string(self, result: GoodsResult) -> str:
        """获取Weaviate查询字符串"""
        if not result.weaviate_query:
            return ""
        
        query_parts = [f"query: {result.weaviate_query.query}"]
        query_parts.append(f"limit: {result.weaviate_query.limit}")
        
        if result.banned_keywords:
            query_parts.append(f"filter banned keywords: {', '.join(result.banned_keywords)}")
        
        return " | ".join(query_parts)

# 便捷函数
async def get_goods_simple(
    conversation_history: List[Dict[str, str]],
    subcategory: Optional[str] = None,
    use_ai: bool = True
) -> str:
    """
    简单的商品获取函数
    
    Args:
        conversation_history: 对话历史
        subcategory: 子类目
        use_ai: 是否使用AI
        
    Returns:
        str: 格式化的输出结果
    """
    agent = WeaviateGoodsAgent(use_ai=use_ai)
    result = await agent.get_goods(conversation_history, subcategory)
    return agent.format_output(result)

# 同步版本
def get_goods_sync(
    conversation_history: List[Dict[str, str]],
    subcategory: Optional[str] = None,
    use_ai: bool = False
) -> str:
    """
    同步版本的商品获取函数
    
    Args:
        conversation_history: 对话历史
        subcategory: 子类目
        use_ai: 是否使用AI
        
    Returns:
        str: 格式化的输出结果
    """
    agent = WeaviateGoodsAgent(use_ai=use_ai)
    result = agent._rule_based_get_goods(conversation_history, subcategory)
    return agent.format_output(result) 