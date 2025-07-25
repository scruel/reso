"""
向量匹配模块
实现商品向量匹配和相似度计算
"""

import math
try:
    import numpy as np
except ImportError:
    # 如果没有numpy，用纯Python实现
    np = None
from typing import Dict, List, Tuple
from dataclasses import dataclass
try:
    from .mock_database import Product
except ImportError:
    from mock_database import Product

@dataclass
class ProductMatch:
    id: int
    brand: str
    model: str
    price: float
    features: List[str]
    similarity_score: float
    match_reasons: List[str]  # 匹配原因

class VectorMatcher:
    def __init__(self):
        # 特征权重配置
        self.feature_weights = {
            "price": 0.3,
            "noise": 0.25,
            "power": 0.2,
            "features": 0.15,
            "style": 0.1
        }
    
    def find_matches(self, requirements: Dict, products: List[Product], top_k: int = 3) -> List[ProductMatch]:
        """找到最匹配的商品"""
        if not requirements or "error" in requirements:
            # 如果没有有效需求，返回默认推荐（按价格排序）
            return self._get_default_recommendations(products, top_k)
        
        scored_products = []
        
        for product in products:
            score, reasons = self._calculate_similarity(requirements, product)
            
            if score > 0:  # 只返回有匹配度的产品
                match = ProductMatch(
                    id=product.id,
                    brand=product.brand,
                    model=product.model,
                    price=product.price,
                    features=product.features,
                    similarity_score=score,
                    match_reasons=reasons
                )
                scored_products.append(match)
        
        # 按相似度排序
        scored_products.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return scored_products[:top_k]
    
    def _calculate_similarity(self, requirements: Dict, product: Product) -> Tuple[float, List[str]]:
        """计算单个产品的相似度"""
        total_score = 0.0
        match_reasons = []
        
        # 1. 价格匹配
        price_score, price_reason = self._score_price_match(requirements.get("budget"), product.price)
        total_score += price_score * self.feature_weights["price"]
        if price_reason:
            match_reasons.append(price_reason)
        
        # 2. 噪音匹配
        noise_score, noise_reason = self._score_noise_match(requirements.get("noise_preference"), product.noise_level)
        total_score += noise_score * self.feature_weights["noise"]
        if noise_reason:
            match_reasons.append(noise_reason)
        
        # 3. 吸力匹配
        power_score, power_reason = self._score_power_match(requirements.get("kitchen_size"), product.power)
        total_score += power_score * self.feature_weights["power"]
        if power_reason:
            match_reasons.append(power_reason)
        
        # 4. 功能特性匹配
        feature_score, feature_reasons = self._score_feature_match(requirements.get("features", []), product.features)
        total_score += feature_score * self.feature_weights["features"]
        match_reasons.extend(feature_reasons)
        
        # 5. 风格匹配
        style_score, style_reason = self._score_style_match(requirements.get("style_preference"), product.style)
        total_score += style_score * self.feature_weights["style"]
        if style_reason:
            match_reasons.append(style_reason)
        
        # 6. 品牌偏好匹配
        if requirements.get("brand_preference") == product.brand:
            total_score += 0.1  # 品牌匹配加分
            match_reasons.append(f"品牌偏好匹配: {product.brand}")
        
        return min(total_score, 1.0), match_reasons  # 分数不超过1.0
    
    def _score_price_match(self, budget_info: Dict, product_price: float) -> Tuple[float, str]:
        """价格匹配评分"""
        if not budget_info:
            return 0.5, ""  # 没有预算要求给中等分
        
        budget = budget_info.get("amount", 0)
        range_type = budget_info.get("range", "around")
        
        if range_type == "max" and product_price <= budget:
            # 在预算内
            ratio = product_price / budget
            score = 1.0 - (ratio - 0.5) ** 2 if ratio > 0.5 else 1.0  # 性价比曲线
            return score, f"价格{product_price}元符合{budget}元预算"
        elif range_type == "around":
            # 预算左右
            diff_ratio = abs(product_price - budget) / budget
            if diff_ratio <= 0.3:  # 30%范围内
                score = 1.0 - diff_ratio * 2
                return score, f"价格{product_price}元接近{budget}元预算"
        
        return 0.1, ""  # 价格不匹配给最低分
    
    def _score_noise_match(self, noise_preference: str, noise_level: int) -> Tuple[float, str]:
        """噪音匹配评分"""
        if not noise_preference:
            return 0.5, ""  # 没有噪音要求给中等分
        
        if noise_preference == "低噪音":
            if noise_level <= 42:
                return 1.0, f"超静音运行{noise_level}分贝"
            elif noise_level <= 45:
                return 0.8, f"静音运行{noise_level}分贝"
            elif noise_level <= 50:
                return 0.6, f"相对安静{noise_level}分贝"
            else:
                return 0.2, ""
        
        return 0.5, ""
    
    def _score_power_match(self, kitchen_size: str, power: str) -> Tuple[float, str]:
        """吸力匹配评分"""
        if not kitchen_size:
            return 0.5, ""  # 没有厨房大小信息给中等分
        
        power_num = self._extract_power_number(power)
        
        # 根据厨房大小匹配吸力
        if kitchen_size in ["小", "4", "5", "6"]:
            # 小厨房
            if 15 <= power_num <= 18:
                return 1.0, f"小厨房适配{power}吸力"
            elif 18 < power_num <= 20:
                return 0.8, f"吸力充足{power}"
        elif kitchen_size in ["中", "8", "10", "12"]:
            # 中厨房
            if 18 <= power_num <= 22:
                return 1.0, f"中厨房适配{power}吸力"
            elif power_num > 22:
                return 0.9, f"大吸力{power}"
        else:
            # 大厨房或不确定
            if power_num >= 20:
                return 1.0, f"大吸力{power}适合大厨房"
        
        return 0.5, ""
    
    def _score_feature_match(self, required_features: List[str], product_features: List[str]) -> Tuple[float, List[str]]:
        """功能特性匹配评分"""
        if not required_features:
            return 0.5, []  # 没有特殊功能要求给中等分
        
        matched_features = []
        for req_feature in required_features:
            for prod_feature in product_features:
                if self._features_similar(req_feature, prod_feature):
                    matched_features.append(f"功能匹配: {prod_feature}")
                    break
        
        if not matched_features:
            return 0.3, []
        
        match_ratio = len(matched_features) / len(required_features)
        score = match_ratio * 0.7 + 0.3  # 最低0.3分，匹配度越高分数越高
        
        return score, matched_features
    
    def _score_style_match(self, style_preference: str, product_style: str) -> Tuple[float, str]:
        """风格匹配评分"""
        if not style_preference:
            return 0.5, ""  # 没有风格偏好给中等分
        
        if style_preference == product_style:
            return 1.0, f"风格匹配: {product_style}"
        elif self._styles_compatible(style_preference, product_style):
            return 0.7, f"风格兼容: {product_style}"
        
        return 0.3, ""
    
    def _extract_power_number(self, power: str) -> int:
        """从功率字符串中提取数值"""
        try:
            return int(power.split('m³')[0])
        except:
            return 20  # 默认值
    
    def _features_similar(self, req_feature: str, prod_feature: str) -> bool:
        """判断功能特性是否相似"""
        feature_mapping = {
            "大吸力": ["大吸力", "强劲吸力", "超大吸力"],
            "静音": ["静音", "低噪音", "超静音"],
            "智能": ["智能", "智能感应", "智能控制", "自动"],
            "易清洁": ["易清洁", "自清洁", "免拆洗", "快速清洁"]
        }
        
        for base_feature, similar_features in feature_mapping.items():
            if req_feature in similar_features and prod_feature in similar_features:
                return True
        
        return req_feature in prod_feature or prod_feature in req_feature
    
    def _styles_compatible(self, style1: str, style2: str) -> bool:
        """判断风格是否兼容"""
        compatible_styles = {
            "现代简约": ["简约", "现代"],
            "简约": ["现代简约", "现代"],
            "现代": ["现代简约", "简约"]
        }
        
        return style2 in compatible_styles.get(style1, [])
    
    def _get_default_recommendations(self, products: List[Product], top_k: int) -> List[ProductMatch]:
        """获取默认推荐（当没有明确需求时）"""
        # 按性价比推荐（价格中等、功能全面）
        scored_products = []
        
        for product in products:
            # 简单的性价比评分：功能数量/价格
            value_score = len(product.features) / (product.price / 1000)
            
            match = ProductMatch(
                id=product.id,
                brand=product.brand,
                model=product.model,
                price=product.price,
                features=product.features,
                similarity_score=value_score,
                match_reasons=["综合性价比推荐"]
            )
            scored_products.append(match)
        
        scored_products.sort(key=lambda x: x.similarity_score, reverse=True)
        return scored_products[:top_k]

if __name__ == "__main__":
    # 测试代码
    from mock_database import MockProductDatabase
    
    # 创建测试数据
    db = MockProductDatabase()
    products = db.get_all_products()
    matcher = VectorMatcher()
    
    # 测试需求
    test_requirements = {
        "budget": {"amount": 3000, "range": "around"},
        "noise_preference": "低噪音",
        "kitchen_size": "8",
        "features": ["大吸力", "静音"],
        "style_preference": "现代简约"
    }
    
    # 查找匹配
    matches = matcher.find_matches(test_requirements, products, top_k=3)
    
    print("匹配结果:")
    for i, match in enumerate(matches, 1):
        print(f"{i}. {match.brand} {match.model}")
        print(f"   价格: {match.price}元")
        print(f"   相似度: {match.similarity_score:.3f}")
        print(f"   匹配原因: {', '.join(match.match_reasons)}")
        print()