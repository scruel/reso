"""
内容解析模块
处理文档、链接和文本内容的解析和关键信息提取
"""

import re
import json
try:
    import aiohttp
except ImportError:
    aiohttp = None
import asyncio
from typing import Dict, List, Optional
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class ContentParser:
    def __init__(self):
        self.session = None
        self._initialize_session()
    
    def _initialize_session(self):
        """初始化HTTP会话"""
        if aiohttp:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
        else:
            self.session = None
    
    async def parse_document(self, content: str) -> Dict:
        """解析文档内容"""
        try:
            # 假设content是文档文本内容或文件路径
            if content.startswith('/') or content.startswith('./'):
                # 文件路径
                return await self._parse_file(content)
            else:
                # 直接文本内容
                return self._parse_text_content(content)
        except Exception as e:
            logger.error(f"Document parsing error: {e}")
            return {"error": str(e), "type": "document"}
    
    async def parse_url(self, url: str) -> Dict:
        """解析URL内容"""
        try:
            if not self._is_valid_url(url):
                return {"error": "Invalid URL format", "type": "url"}
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    return self._parse_web_content(content, url)
                else:
                    return {
                        "error": f"HTTP {response.status}",
                        "type": "url",
                        "url": url
                    }
        except Exception as e:
            logger.error(f"URL parsing error: {e}")
            return {"error": str(e), "type": "url", "url": url}
    
    def extract_keywords(self, parsed_content: Dict) -> Dict:
        """从解析内容中提取关键词和需求信息（Fallback方法）"""
        if "error" in parsed_content:
            return {"error": parsed_content["error"]}
        
        text = parsed_content.get("raw_text", "") or parsed_content.get("content", "")
        
        # 提取关键信息
        requirements = {
            "budget": self._extract_budget(text),
            "kitchen_size": self._extract_kitchen_size(text),
            "noise_preference": self._extract_noise_preference(text),
            "style_preference": self._extract_style_preference(text),
            "features": self._extract_features(text),
            "brand_preference": self._extract_brand_preference(text),
            "installation_type": self._extract_installation_type(text),
            "keywords": self._extract_general_keywords(text)
        }
        
        return requirements
    
    async def _parse_file(self, file_path: str) -> Dict:
        """解析本地文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_type = file_path.split('.')[-1].lower()
            
            return {
                "raw_text": content,
                "type": "file",
                "file_type": file_type,
                "file_path": file_path
            }
        except Exception as e:
            return {"error": f"File reading error: {e}", "type": "file"}
    
    def _parse_text_content(self, text: str) -> Dict:
        """解析纯文本内容"""
        return {
            "raw_text": text,
            "type": "text",
            "length": len(text),
            "word_count": len(text.split())
        }
    
    def _parse_web_content(self, html_content: str, url: str) -> Dict:
        """解析网页内容"""
        # 简单的HTML标签清理
        text_content = re.sub(r'<[^>]+>', '', html_content)
        text_content = re.sub(r'\\s+', ' ', text_content).strip()
        
        return {
            "raw_text": text_content[:5000],  # 限制长度
            "type": "web",
            "url": url,
            "content_length": len(text_content),
            "domain": urlparse(url).netloc
        }
    
    def _is_valid_url(self, url: str) -> bool:
        """验证URL格式"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _extract_budget(self, text: str) -> Optional[Dict]:
        """提取预算信息"""
        budget_patterns = [
            r'预算.*?([0-9]+).*?元',
            r'([0-9]+).*?元.*?左右',
            r'([0-9]+).*?块钱',
            r'价格.*?([0-9]+)',
            r'([0-9]{4})以下',
            r'([0-9]{4})以内'
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, text)
            if match:
                budget = int(match.group(1))
                return {
                    "amount": budget,
                    "range": "around" if "左右" in text else "max"
                }
        return None
    
    def _extract_kitchen_size(self, text: str) -> Optional[str]:
        """提取厨房大小信息"""
        size_patterns = [
            r'厨房.*?([0-9]+).*?平',
            r'([0-9]+).*?平.*?厨房',
            r'厨房.*?(大|中|小)',
            r'(小|中|大).*?厨房'
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None
    
    def _extract_noise_preference(self, text: str) -> Optional[str]:
        """提取噪音偏好"""
        noise_keywords = ["静音", "噪音小", "安静", "不吵", "低噪"]
        
        for keyword in noise_keywords:
            if keyword in text:
                return "低噪音"
        return None
    
    def _extract_style_preference(self, text: str) -> Optional[str]:
        """提取装修风格偏好"""
        style_mapping = {
            "现代": "现代简约",
            "简约": "简约",
            "欧式": "欧式",
            "中式": "中式",
            "日式": "日式",
            "德式": "德式简约",
            "工业风": "工业风"
        }
        
        for style, mapped_style in style_mapping.items():
            if style in text:
                return mapped_style
        return None
    
    def _extract_features(self, text: str) -> List[str]:
        """提取功能特性需求"""
        feature_keywords = {
            "大吸力": ["大吸力", "吸力强", "强吸力"],
            "静音": ["静音", "安静", "低噪"],
            "智能": ["智能", "自动", "感应"],
            "易清洁": ["好清洗", "易清洁", "自清洁"],
            "节能": ["节能", "省电"],
            "LED照明": ["照明", "LED", "灯光"]
        }
        
        found_features = []
        for feature, keywords in feature_keywords.items():
            if any(keyword in text for keyword in keywords):
                found_features.append(feature)
        
        return found_features
    
    def _extract_brand_preference(self, text: str) -> Optional[str]:
        """提取品牌偏好"""
        brands = ["方太", "老板", "华帝", "美的", "西门子", "樱花", "海尔", "万和", "帅康", "格兰仕"]
        
        for brand in brands:
            if brand in text:
                return brand
        return None
    
    def _extract_installation_type(self, text: str) -> Optional[str]:
        """提取安装类型偏好"""
        type_keywords = {
            "侧吸": ["侧吸", "侧面"],
            "顶吸": ["顶吸", "上面", "顶部"],
            "T型": ["T型", "T形"]
        }
        
        for install_type, keywords in type_keywords.items():
            if any(keyword in text for keyword in keywords):
                return install_type
        return None
    
    def _extract_general_keywords(self, text: str) -> List[str]:
        """提取通用关键词"""
        # 简单的关键词提取
        keywords = []
        
        # 常见关键词
        common_keywords = [
            "装修", "新房", "厨房", "油烟机", "抽油烟机",
            "烟机", "家电", "电器", "购买", "选择"
        ]
        
        for keyword in common_keywords:
            if keyword in text:
                keywords.append(keyword)
        
        return keywords
    
    async def close(self):
        """关闭HTTP会话"""
        if self.session:
            await self.session.close()

# 异步上下文管理器
class AsyncContentParser:
    def __init__(self):
        self.parser = None
    
    async def __aenter__(self):
        self.parser = ContentParser()
        return self.parser
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.parser:
            await self.parser.close()

if __name__ == "__main__":
    # 测试代码
    async def test():
        async with AsyncContentParser() as parser:
            # 测试文本解析
            test_text = "我家新房装修，厨房8平米，预算3000元左右，希望噪音小一些，最好是现代简约风格"
            
            text_result = parser._parse_text_content(test_text)
            print("文本解析结果:")
            print(json.dumps(text_result, ensure_ascii=False, indent=2))
            
            keywords = parser.extract_keywords(text_result)  
            print("\\n关键词提取结果:")
            print(json.dumps(keywords, ensure_ascii=False, indent=2))
            
            # 测试URL解析（示例）
            # url_result = await parser.parse_url("https://example.com")
            # print("URL解析结果:")
            # print(json.dumps(url_result, ensure_ascii=False, indent=2))
    
    asyncio.run(test())