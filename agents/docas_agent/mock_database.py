"""
Mock油烟机产品数据库
模拟真实的电商产品数据
"""

import json
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Product:
    id: int
    brand: str
    model: str
    price: float
    power: str  # 吸力
    noise_level: int  # 噪音分贝
    features: List[str]
    kitchen_size: str  # 适用厨房大小
    style: str  # 装修风格
    installation_type: str  # 安装方式
    description: str

class MockProductDatabase:
    def __init__(self):
        self.products = self._initialize_products()
    
    def _initialize_products(self) -> List[Product]:
        """初始化模拟产品数据"""
        return [
            Product(
                id=1,
                brand="方太",
                model="CXW-200-EMC2",
                price=2999.0,
                power="20m³/min",
                noise_level=45,
                features=["大吸力", "静音", "易清洁", "自动巡航"],
                kitchen_size="6-10平米",
                style="现代简约",
                installation_type="侧吸式",
                description="方太经典侧吸式油烟机，20立方大吸力，45分贝静音运行，适合现代简约风格厨房"
            ),
            Product(
                id=2,
                brand="老板",
                model="CXW-200-8229",
                price=3599.0,
                power="23m³/min",
                noise_level=42,
                features=["智能感应", "自清洁", "变频", "手势控制"],
                kitchen_size="8-15平米",
                style="欧式",
                installation_type="顶吸式",
                description="老板智能顶吸式油烟机，23立方超大吸力，智能手势控制，自清洁功能"
            ),
            Product(
                id=3,
                brand="华帝",
                model="CXW-228-i11083",
                price=2199.0,
                power="18m³/min",
                noise_level=48,
                features=["LED照明", "不锈钢材质", "三档调速"],
                kitchen_size="4-8平米",
                style="简约",
                installation_type="侧吸式",
                description="华帝入门级侧吸式油烟机，18立方吸力，适合小户型厨房使用"
            ),
            Product(
                id=4,
                brand="美的",
                model="CXW-200-DT23S",
                price=1899.0,
                power="17m³/min",
                noise_level=50,
                features=["触控面板", "延时关机", "可拆洗"],
                kitchen_size="4-6平米",
                style="现代",
                installation_type="侧吸式",
                description="美的经济型侧吸式油烟机，17立方吸力，触控操作，性价比高"
            ),
            Product(
                id=5,
                brand="西门子",
                model="LC67BE532W",
                price=4299.0,
                power="25m³/min",
                noise_level=40,
                features=["变频电机", "智能控制", "德国工艺", "低噪音"],
                kitchen_size="10-20平米",
                style="德式简约",
                installation_type="T型机",
                description="西门子德国工艺T型油烟机，25立方超强吸力，40分贝超静音，适合大厨房"
            ),
            Product(
                id=6,
                brand="樱花",
                model="SCR-3628E",
                price=2699.0,
                power="19m³/min",
                noise_level=46,
                features=["防倒灌", "快拆清洗", "节能"],
                kitchen_size="6-12平米",
                style="日式",
                installation_type="侧吸式",
                description="樱花日式侧吸油烟机，19立方吸力，防倒灌设计，节能环保"
            ),
            Product(
                id=7,
                brand="海尔",
                model="CXW-200-C389",
                price=1699.0,
                power="16m³/min",
                noise_level=52,
                features=["一键清洗", "多重过滤", "经济实用"],
                kitchen_size="3-6平米",
                style="简约",
                installation_type="侧吸式",
                description="海尔经济实用型油烟机，16立方吸力，一键清洗功能，适合小厨房"
            ),
            Product(
                id=8,
                brand="万和",
                model="CXW-200-X12A",
                price=2399.0,
                power="21m³/min",
                noise_level=44,
                features=["大风量", "快速清洁", "智能感应"],
                kitchen_size="8-12平米",
                style="现代",
                installation_type="侧吸式",
                description="万和大风量侧吸式油烟机，21立方大吸力，44分贝低噪音运行"
            ),
            Product(
                id=9,
                brand="帅康",
                model="CXW-200-TE6",
                price=3199.0,
                power="22m³/min",
                noise_level=43,
                features=["免拆洗", "智能变频", "LED显示"],
                kitchen_size="6-15平米",
                style="欧式",
                installation_type="欧式顶吸",
                description="帅康欧式顶吸油烟机，22立方强劲吸力，免拆洗设计，智能变频控制"
            ),
            Product(
                id=10,
                brand="格兰仕",
                model="CXW-168-QS1",
                price=1399.0,
                power="15m³/min",
                noise_level=55,
                features=["基础款", "简单操作", "性价比高"],
                kitchen_size="3-5平米",
                style="简约",
                installation_type="侧吸式",
                description="格兰仕基础款油烟机，15立方吸力，操作简单，超高性价比"
            )
        ]
    
    def get_all_products(self) -> List[Product]:
        """获取所有产品"""
        return self.products
    
    def get_product_by_id(self, product_id: int) -> Product:
        """根据ID获取产品"""
        for product in self.products:
            if product.id == product_id:
                return product
        return None
    
    def filter_by_price_range(self, min_price: float = 0, max_price: float = float('inf')) -> List[Product]:
        """按价格范围过滤"""
        return [p for p in self.products if min_price <= p.price <= max_price]
    
    def filter_by_brand(self, brand: str) -> List[Product]:
        """按品牌过滤"""
        return [p for p in self.products if p.brand.lower() == brand.lower()]
    
    def filter_by_features(self, required_features: List[str]) -> List[Product]:
        """按功能特性过滤"""
        result = []
        for product in self.products:
            if any(feature in product.features for feature in required_features):
                result.append(product)
        return result
    
    def filter_by_noise_level(self, max_noise: int) -> List[Product]:
        """按噪音水平过滤"""
        return [p for p in self.products if p.noise_level <= max_noise]
    
    def filter_by_kitchen_size(self, kitchen_size: str) -> List[Product]:
        """按厨房大小过滤（简单匹配）"""
        size_keywords = {
            "小": ["3-5平米", "4-6平米", "4-8平米"],
            "中": ["6-10平米", "6-12平米", "8-12平米", "6-15平米"],
            "大": ["10-15平米", "10-20平米", "8-15平米"]
        }
        
        result = []
        for size_category, size_ranges in size_keywords.items():
            if size_category in kitchen_size:
                result.extend([p for p in self.products if p.kitchen_size in size_ranges])
                break
        
        return result if result else self.products  # 如果没匹配到，返回所有产品
    
    def get_product_vectors(self) -> Dict[int, Dict]:
        """获取产品的向量化特征（简化版）"""
        vectors = {}
        for product in self.products:
            vectors[product.id] = {
                "price_range": self._get_price_range(product.price),
                "power_level": self._get_power_level(product.power),
                "noise_level": product.noise_level,
                "features": product.features,
                "style": product.style,
                "installation_type": product.installation_type
            }
        return vectors
    
    def _get_price_range(self, price: float) -> str:
        """获取价格区间"""
        if price < 2000:
            return "低价位"
        elif price < 3500:
            return "中价位"
        else:
            return "高价位"
    
    def _get_power_level(self, power: str) -> str:
        """获取吸力等级"""
        power_num = int(power.split('m³')[0])
        if power_num < 18:
            return "标准吸力"
        elif power_num < 22:
            return "大吸力"
        else:
            return "超大吸力"
    
    def to_json(self) -> str:
        """导出为JSON格式"""
        data = []
        for product in self.products:
            data.append({
                "id": product.id,
                "brand": product.brand,
                "model": product.model,
                "price": product.price,
                "power": product.power,
                "noise_level": product.noise_level,
                "features": product.features,
                "kitchen_size": product.kitchen_size,
                "style": product.style,
                "installation_type": product.installation_type,
                "description": product.description
            })
        return json.dumps(data, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # 测试代码
    db = MockProductDatabase()
    print(f"总产品数: {len(db.get_all_products())}")
    
    # 测试价格过滤
    budget_products = db.filter_by_price_range(2000, 3000)
    print(f"2000-3000元价位产品: {len(budget_products)}")
    
    # 测试静音过滤
    quiet_products = db.filter_by_noise_level(45)
    print(f"45分贝以下静音产品: {len(quiet_products)}")
    
    # 打印第一个产品的详细信息
    if db.products:
        p = db.products[0]
        print(f"\\n示例产品: {p.brand} {p.model}")
        print(f"价格: {p.price}元")
        print(f"特性: {', '.join(p.features)}")