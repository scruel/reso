"""
Weaviate Goods Agent
"""

import json
import logging
import re
import requests
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

# Weaviate客户端
try:
    import weaviate
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False
    print("Weaviate client not available")

# CAMEL框架支持
try:
    from camel.agents import ChatAgent
    from camel.messages import BaseMessage
    from camel.models import ModelFactory
    from camel.types import ModelType, ModelPlatformType, RoleType
    CAMEL_AVAILABLE = True
except ImportError:
    CAMEL_AVAILABLE = False
    print("CAMEL framework not available")

logger = logging.getLogger(__name__)

@dataclass
class LLMIntentResult:
    """LLM意图识别结果"""
    title: str
    positive_concepts: str
    negative_keywords: List[str]
    confidence: float = 0.8

@dataclass
class WeaviateSearchResult:
    """Weaviate搜索结果"""
    products: List[Dict[str, Any]]
    total_count: int
    search_params: Dict[str, Any]

@dataclass
class RerankResult:
    """重排序结果"""
    reranked_products: List[Dict[str, Any]]
    scores: List[float]
    original_query: str

@dataclass
class FinalAgentOutput:
    """最终Agent输出"""
    intent: Dict[str, Any]
    message: str
    status: int = 0
    debug_info: Optional[Dict[str, Any]] = None

class AdvancedWeaviateAgent:
    """高级Weaviate商品获取AI代理"""
    
    def __init__(
        self, 
        weaviate_url: str = "http://localhost:8080",
        qwen_api_url: Optional[str] = None,
        rerank_api_url: Optional[str] = None,
        use_ai: bool = True
    ):
        """
        初始化高级Weaviate代理
        
        Args:
            weaviate_url: Weaviate实例地址
            qwen_api_url: Qwen API地址
            rerank_api_url: Qwen Rerank API地址
            use_ai: 是否使用AI模型
        """
        self.weaviate_url = weaviate_url
        self.qwen_api_url = qwen_api_url
        self.rerank_api_url = rerank_api_url
        self.use_ai = use_ai
        
        # 初始化客户端
        self.weaviate_client = None
        self.qwen_agent = None
        
        self._init_clients()
        
        logger.info("AdvancedWeaviateAgent initialized")
    
    def _init_clients(self):
        """初始化各种客户端"""
        # 初始化Weaviate客户端
        if WEAVIATE_AVAILABLE:
            try:
                self.weaviate_client = weaviate.Client(self.weaviate_url)
                logger.info(f"Weaviate client connected: {self.weaviate_url}")
            except Exception as e:
                logger.warning(f"Failed to connect Weaviate: {e}")
        
        # 初始化Qwen AI代理
        if self.use_ai and CAMEL_AVAILABLE:
            try:
                model = ModelFactory.create(
                    model_platform=ModelPlatformType.OPENAI,  # 通过兼容接口
                    model_type="qwen-turbo",
                )
                
                system_message = BaseMessage.make_assistant_message(
                    role_name="E-commerce Intent Expert",
                    content=self._get_intent_system_prompt()
                )
                
                self.qwen_agent = ChatAgent(
                    system_message=system_message,
                    model=model,
                    message_window_size=10
                )
                
                logger.info("Qwen agent initialized")
                
            except Exception as e:
                logger.warning(f"Failed to initialize Qwen agent: {e}")
                self.use_ai = False
    
    def _get_intent_system_prompt(self) -> str:
        """获取意图识别的系统提示词"""
        return """你是一个电商导购专家，专门分析用户对话以提炼搜索指令。

你的任务是：
1. 识别核心购买意图，生成一个简短的标题 (title)。
2. 提取用于向量搜索的正面核心概念 (positive_concepts)，应该是一个适合语义搜索的短语。
3. 识别用户明确不想要的商品属性，提取为"排除关键词"列表 (negative_keywords)。
4. 严格按照 JSON 格式输出结果。

输出格式示例：
{
  "title": "购买轻薄办公笔记本",
  "positive_concepts": "轻薄便携的商务办公笔记本电脑",
  "negative_keywords": ["游戏本", "重", "吵"]
}

注意：
- positive_concepts 应该是完整的、适合语义搜索的描述性短语
- negative_keywords 是用户明确表示不想要的特征列表
- title 简洁明了，体现核心购买意图"""

    async def process_complete_workflow(
        self,
        conversation_history: List[Dict[str, str]],
        current_category: Optional[str] = None,
        limit: int = 20
    ) -> FinalAgentOutput:
        """
        执行完整的三阶段工作流程
        
        Args:
            conversation_history: 用户对话历史
            current_category: 当前类目
            limit: 返回商品数量限制
            
        Returns:
            FinalAgentOutput: 最终输出结果
        """
        debug_info = {"stages": {}}
        
        try:
            # 阶段一：LLM意图识别
            intent_result = await self._stage1_intent_recognition(
                conversation_history, current_category
            )
            debug_info["stages"]["stage1_intent"] = {
                "title": intent_result.title,
                "positive_concepts": intent_result.positive_concepts,
                "negative_keywords": intent_result.negative_keywords
            }
            
            # 阶段二：Weaviate查询
            search_result = await self._stage2_weaviate_search(
                intent_result, current_category, limit=100  # 先召回100个
            )
            debug_info["stages"]["stage2_search"] = {
                "total_found": search_result.total_count,
                "search_params": search_result.search_params
            }
            
            # 阶段三：Qwen Rerank重排序
            rerank_result = await self._stage3_qwen_rerank(
                intent_result, search_result, limit=limit
            )
            debug_info["stages"]["stage3_rerank"] = {
                "reranked_count": len(rerank_result.reranked_products),
                "avg_score": sum(rerank_result.scores) / len(rerank_result.scores) if rerank_result.scores else 0
            }
            
            # 生成最终输出
            final_output = self._generate_final_output(
                intent_result, rerank_result, debug_info
            )
            
            return final_output
            
        except Exception as e:
            logger.error(f"Workflow processing failed: {e}")
            return FinalAgentOutput(
                intent={"title": "商品查询失败", "attrs": []},
                message=f"处理过程出错: {str(e)}",
                status=1,
                debug_info=debug_info
            )
    
    async def _stage1_intent_recognition(
        self,
        conversation_history: List[Dict[str, str]],
        current_category: Optional[str] = None
    ) -> LLMIntentResult:
        """阶段一：LLM意图识别"""
        
        if self.use_ai and self.qwen_agent:
            return await self._ai_intent_recognition(conversation_history, current_category)
        else:
            return self._rule_based_intent_recognition(conversation_history, current_category)
    
    async def _ai_intent_recognition(
        self,
        conversation_history: List[Dict[str, str]],
        current_category: Optional[str] = None
    ) -> LLMIntentResult:
        """使用AI进行意图识别"""
        
        # 构建用户输入上下文
        conversation_text = self._format_conversation(conversation_history[-6:])  # 最近6轮
        
        prompt = f"""这是用户的上下文和对话历史：
- 当前类目: "{current_category or '未指定'}"
- 对话历史:
{conversation_text}

请分析用户的购买意图，严格按照JSON格式输出结果。"""

        try:
            user_message = BaseMessage.make_user_message(
                role_name="User",
                content=prompt
            )
            
            response = await self.qwen_agent.step(user_message)
            result_text = response.msg.content
            
            return self._parse_llm_intent_response(result_text)
            
        except Exception as e:
            logger.error(f"AI intent recognition failed: {e}")
            return self._rule_based_intent_recognition(conversation_history, current_category)
    
    def _rule_based_intent_recognition(
        self,
        conversation_history: List[Dict[str, str]],
        current_category: Optional[str] = None
    ) -> LLMIntentResult:
        """基于规则的意图识别"""
        
        conversation_text = " ".join([
            msg.get("content", "") for msg in conversation_history[-3:]
        ])
        
        # 生成标题
        if current_category:
            title = f"选购{current_category}"
        else:
            title = "商品查询"
        
        # 生成正面概念
        positive_concepts = f"{current_category or '商品'} {conversation_text}".strip()
        
        # 提取负面关键词
        negative_keywords = self._extract_negative_keywords(conversation_text)
        
        return LLMIntentResult(
            title=title,
            positive_concepts=positive_concepts,
            negative_keywords=negative_keywords,
            confidence=0.7
        )
    
    async def _stage2_weaviate_search(
        self,
        intent_result: LLMIntentResult,
        current_category: Optional[str] = None,
        limit: int = 100
    ) -> WeaviateSearchResult:
        """阶段二：Weaviate向量查询 + 排除过滤"""
        
        if self.weaviate_client:
            return self._execute_weaviate_query(intent_result, current_category, limit)
        else:
            return self._mock_weaviate_search(intent_result, limit)
    
    def _execute_weaviate_query(
        self,
        intent_result: LLMIntentResult,
        current_category: Optional[str] = None,
        limit: int = 100
    ) -> WeaviateSearchResult:
        """执行真实的Weaviate查询"""
        
        try:
            # 构建排除过滤器
            where_operands = []
            for keyword in intent_result.negative_keywords:
                where_operands.append({
                    "path": ["description"],
                    "operator": "NotLike",
                    "valueText": f"*{keyword}*"
                })
            
            # 添加类目过滤
            if current_category:
                where_operands.append({
                    "path": ["category"],
                    "operator": "Equal",
                    "valueText": current_category
                })
            
            where_filter = {
                "operator": "And",
                "operands": where_operands
            } if where_operands else None
            
            # 执行查询
            query_builder = (
                self.weaviate_client.query
                .get("Product", ["name", "description", "price", "category", "_additional {id, score}"])
                .with_near_text({
                    "concepts": [intent_result.positive_concepts]
                })
                .with_limit(limit)
            )
            
            if where_filter:
                query_builder = query_builder.with_where(where_filter)
            
            response = query_builder.do()
            
            products = response.get("data", {}).get("Get", {}).get("Product", [])
            
            return WeaviateSearchResult(
                products=products,
                total_count=len(products),
                search_params={
                    "concepts": intent_result.positive_concepts,
                    "negative_keywords": intent_result.negative_keywords,
                    "category": current_category,
                    "limit": limit
                }
            )
            
        except Exception as e:
            logger.error(f"Weaviate query failed: {e}")
            return self._mock_weaviate_search(intent_result, limit)
    
    def _mock_weaviate_search(
        self,
        intent_result: LLMIntentResult,
        limit: int = 100
    ) -> WeaviateSearchResult:
        """模拟Weaviate搜索结果"""
        
        # 生成模拟商品数据
        mock_products = []
        for i in range(min(limit, 20)):  # 模拟返回20个商品
            mock_products.append({
                "name": f"商品{i+1} - {intent_result.title}相关",
                "description": f"这是一个与{intent_result.positive_concepts}相关的优质商品",
                "price": 1000 + i * 100,
                "category": "电子产品",
                "_additional": {
                    "id": f"mock-{i+1}",
                    "score": 0.9 - i * 0.02
                }
            })
        
        return WeaviateSearchResult(
            products=mock_products,
            total_count=len(mock_products),
            search_params={
                "concepts": intent_result.positive_concepts,
                "negative_keywords": intent_result.negative_keywords,
                "mock": True
            }
        )
    
    async def _stage3_qwen_rerank(
        self,
        intent_result: LLMIntentResult,
        search_result: WeaviateSearchResult,
        limit: int = 20
    ) -> RerankResult:
        """阶段三：Qwen Rerank重排序"""
        
        if self.rerank_api_url:
            return await self._api_rerank(intent_result, search_result, limit)
        else:
            return self._simple_rerank(intent_result, search_result, limit)
    
    async def _api_rerank(
        self,
        intent_result: LLMIntentResult,
        search_result: WeaviateSearchResult,
        limit: int = 20
    ) -> RerankResult:
        """使用API进行重排序"""
        
        try:
            # 准备重排序数据
            documents = [product.get("description", "") for product in search_result.products]
            original_query = intent_result.positive_concepts
            
            payload = {
                "query": original_query,
                "documents": documents
            }
            
            # 调用重排序API
            response = requests.post(self.rerank_api_url, json=payload, timeout=30)
            response.raise_for_status()
            
            rerank_response = response.json()
            
            # 解析重排序结果
            reranked_products = []
            scores = []
            
            for item in rerank_response[:limit]:
                index = item["document_index"]
                score = item["relevance_score"]
                
                if index < len(search_result.products):
                    reranked_products.append(search_result.products[index])
                    scores.append(score)
            
            return RerankResult(
                reranked_products=reranked_products,
                scores=scores,
                original_query=original_query
            )
            
        except Exception as e:
            logger.error(f"API rerank failed: {e}")
            return self._simple_rerank(intent_result, search_result, limit)
    
    def _simple_rerank(
        self,
        intent_result: LLMIntentResult,
        search_result: WeaviateSearchResult,
        limit: int = 20
    ) -> RerankResult:
        """简单的重排序（基于原始分数）"""
        
        # 按原始分数排序
        products_with_scores = []
        for product in search_result.products:
            score = product.get("_additional", {}).get("score", 0.5)
            products_with_scores.append((product, score))
        
        # 排序并取前N个
        products_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        reranked_products = [item[0] for item in products_with_scores[:limit]]
        scores = [item[1] for item in products_with_scores[:limit]]
        
        return RerankResult(
            reranked_products=reranked_products,
            scores=scores,
            original_query=intent_result.positive_concepts
        )
    
    def _generate_final_output(
        self,
        intent_result: LLMIntentResult,
        rerank_result: RerankResult,
        debug_info: Dict[str, Any]
    ) -> FinalAgentOutput:
        """生成最终的Agent输出"""
        
        # 构建intent对象
        attrs = []
        
        # 从positive_concepts提取正面属性
        positive_words = intent_result.positive_concepts.split()
        for word in positive_words:
            if len(word) > 1 and word not in ["的", "和", "或", "与"]:
                attrs.append(word)
        
        # 添加负面属性（带NOT前缀）
        for keyword in intent_result.negative_keywords:
            attrs.append(f"NOT:{keyword}")
        
        intent = {
            "title": intent_result.title,
            "attrs": attrs[:10]  # 限制属性数量
        }
        
        # 生成消息
        excluded_count = len(intent_result.negative_keywords)
        found_count = len(rerank_result.reranked_products)
        
        if excluded_count > 0:
            message = f"好的，为您找到了{found_count}个{intent_result.title}相关商品，并排除了您不喜欢的{excluded_count}个特征。"
        else:
            message = f"为您找到了{found_count}个{intent_result.title}相关商品。"
        
        return FinalAgentOutput(
            intent=intent,
            message=message,
            status=0,
            debug_info=debug_info
        )
    
    def _format_conversation(self, conversation_history: List[Dict[str, str]]) -> str:
        """格式化对话历史"""
        formatted = []
        for msg in conversation_history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            formatted.append(f"  - {role}: \"{content}\"")
        return "\n".join(formatted)
    
    def _extract_negative_keywords(self, text: str) -> List[str]:
        """提取负面关键词"""
        text_lower = text.lower()
        negative_keywords = []
        
        # 负面表达模式
        patterns = [
            r'不要(.+?)(?:[，。！？\s]|$)',
            r'不想要(.+?)(?:[，。！？\s]|$)',
            r'除了(.+?)(?:[，。！？\s]|$)',
            r'别(.+?)(?:[，。！？\s]|$)',
            r'不喜欢(.+?)(?:[，。！？\s]|$)',
            r'不考虑(.+?)(?:[，。！？\s]|$)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                keyword = match.strip()
                if keyword and len(keyword) < 10:
                    negative_keywords.append(keyword)
        
        return list(set(negative_keywords))
    
    def _parse_llm_intent_response(self, response_text: str) -> LLMIntentResult:
        """解析LLM意图识别响应"""
        try:
            # 尝试直接解析JSON
            if response_text.strip().startswith("{"):
                data = json.loads(response_text)
            else:
                # 提取JSON部分
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                else:
                    raise ValueError("No JSON found")
            
            return LLMIntentResult(
                title=data.get("title", "商品查询"),
                positive_concepts=data.get("positive_concepts", ""),
                negative_keywords=data.get("negative_keywords", []),
                confidence=0.9
            )
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            # 返回默认结果
            return LLMIntentResult(
                title="商品查询",
                positive_concepts="商品",
                negative_keywords=[],
                confidence=0.5
            )
    
    def format_output(self, result: FinalAgentOutput) -> str:
        """格式化输出为指定格式"""
        output_data = {
            "intent": result.intent,
            "message": result.message,
            "status": result.status
        }
        
        return f"====agent gen query\n{json.dumps(output_data, ensure_ascii=False, indent=2)}"

# 便捷函数
async def get_goods_advanced(
    conversation_history: List[Dict[str, str]],
    current_category: Optional[str] = None,
    weaviate_url: str = "http://localhost:8080",
    rerank_api_url: Optional[str] = None,
    limit: int = 20
) -> str:
    """
    高级商品获取函数
    
    Args:
        conversation_history: 对话历史
        current_category: 当前类目
        weaviate_url: Weaviate地址
        rerank_api_url: 重排序API地址
        limit: 返回数量
        
    Returns:
        str: 格式化的输出结果
    """
    agent = AdvancedWeaviateAgent(
        weaviate_url=weaviate_url,
        rerank_api_url=rerank_api_url,
        use_ai=True
    )
    
    result = await agent.process_complete_workflow(
        conversation_history, current_category, limit
    )
    
    return agent.format_output(result) 