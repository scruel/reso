"""
DocAsAgent - 文档理解和商品推荐Agent
基于MiniMax Agent API构建
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InputType(Enum):
    TEXT = "text"
    DOCUMENT = "document" 
    URL = "url"

@dataclass
class UserInput:
    content: str
    input_type: InputType
    metadata: Optional[Dict] = None

@dataclass
class ProductMatch:
    id: int
    brand: str
    model: str
    price: float
    features: List[str]
    similarity_score: float
    
@dataclass
class AgentResponse:
    recommendation: str
    matched_products: List[ProductMatch]
    confidence: float
    reasoning: str

class DocAsAgent:
    def __init__(self):
        """初始化DocAsAgent"""
        self.api_key = None  # 待设置MiniMax API Key
        self.group_id = None  # 待设置MiniMax Group ID
        self.mock_db = None
        self._initialize_components()
    
    def _initialize_components(self):
        """初始化各个组件"""
        from .mock_database import MockProductDatabase
        from .content_parser import ContentParser
        from .vector_matcher import VectorMatcher
        from .minimax_client import MinimaxAgentClient
        
        self.mock_db = MockProductDatabase()
        self.content_parser = ContentParser()
        self.vector_matcher = VectorMatcher()
        self.minimax_client = None  # 待API信息后初始化
        
        logger.info("DocAsAgent components initialized")
    
    def set_minimax_credentials(self, api_key: str, group_id: str):
        """设置MiniMax API凭据"""
        self.api_key = api_key
        self.group_id = group_id
        from .minimax_client import MinimaxAgentClient
        self.minimax_client = MinimaxAgentClient(api_key, group_id)
        logger.info("MiniMax credentials configured")
    
    async def process_request(self, user_input: UserInput) -> AgentResponse:
        """处理用户请求的主入口"""
        try:
            logger.info(f"Processing {user_input.input_type.value} input")
            
            # 1. 内容解析和理解
            parsed_content = await self._parse_content(user_input)
            
            # 2. 提取用户需求特征
            requirements = await self._extract_requirements(parsed_content)
            
            # 3. 商品匹配
            matched_products = await self._match_products(requirements)
            
            # 4. 生成推荐语
            recommendation = await self._generate_recommendation(
                requirements, matched_products
            )
            
            return AgentResponse(
                recommendation=recommendation["text"],
                matched_products=matched_products,
                confidence=recommendation["confidence"],
                reasoning=recommendation["reasoning"]
            )
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return AgentResponse(
                recommendation="抱歉，处理您的请求时出现了问题，请稍后重试。",
                matched_products=[],
                confidence=0.0,
                reasoning=f"Error: {str(e)}"
            )
    
    async def _parse_content(self, user_input: UserInput) -> Dict:
        """解析内容"""
        if user_input.input_type == InputType.TEXT:
            return {"raw_text": user_input.content, "type": "text"}
        elif user_input.input_type == InputType.DOCUMENT:
            return await self.content_parser.parse_document(user_input.content)
        elif user_input.input_type == InputType.URL:
            return await self.content_parser.parse_url(user_input.content)
    
    async def _extract_requirements(self, parsed_content: Dict) -> Dict:
        """使用MiniMax Agent提取用户需求"""
        if self.minimax_client:
            return await self.minimax_client.extract_requirements(parsed_content)
        else:
            # 临时fallback逻辑
            return self.content_parser.extract_keywords(parsed_content)
    
    async def _match_products(self, requirements: Dict) -> List[ProductMatch]:
        """匹配商品"""
        all_products = self.mock_db.get_all_products()
        return self.vector_matcher.find_matches(requirements, all_products)
    
    async def _generate_recommendation(self, requirements: Dict, products: List[ProductMatch]) -> Dict:
        """生成推荐语"""
        if self.minimax_client:
            return await self.minimax_client.generate_recommendation(requirements, products)
        else:
            # 临时fallback逻辑
            if products:
                top_product = products[0]
                return {
                    "text": f"为您推荐{top_product.brand} {top_product.model}，价格{top_product.price}元！",
                    "confidence": top_product.similarity_score,
                    "reasoning": "基于特征匹配的推荐"
                }
            else:
                return {
                    "text": "暂未找到合适的油烟机产品，请提供更多信息。",
                    "confidence": 0.0,
                    "reasoning": "未找到匹配产品"
                }

# 对外接口
async def create_docas_agent() -> DocAsAgent:
    """创建DocAsAgent实例"""
    agent = DocAsAgent()
    return agent

if __name__ == "__main__":
    # 测试代码
    async def test():
        agent = await create_docas_agent()
        
        test_input = UserInput(
            content="我家厨房8平米，预算3000元左右，希望噪音小一些",
            input_type=InputType.TEXT
        )
        
        response = await agent.process_request(test_input)
        print(f"推荐: {response.recommendation}")
        print(f"匹配产品数: {len(response.matched_products)}")
        print(f"置信度: {response.confidence}")
    
    asyncio.run(test())