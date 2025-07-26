#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语义搜索测试脚本

用于测试导入到 PGVector 的商品数据，验证语义搜索功能。

使用方法:
    python test_semantic_search.py "搜索查询"
"""

import os
import sys
import logging
from typing import List, Dict
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticSearcher:
    """语义搜索器"""
    
    def __init__(self, db_params: Dict[str, str], model_name: str = "Alibaba-NLP/gte-Qwen2-1.5B-instruct"):
        """初始化搜索器
        
        Args:
            db_params: 数据库连接参数
            model_name: 嵌入模型名称
        """
        self.db_params = db_params
        self.model_name = model_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 加载模型
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
        self.model.to(self.device)
        self.model.eval()
        
        logger.info(f"模型加载完成，使用设备: {self.device}")
    
    def encode_query(self, query: str) -> np.ndarray:
        """编码查询文本
        
        Args:
            query: 查询文本
            
        Returns:
            查询向量
        """
        with torch.no_grad():
            inputs = self.tokenizer(
                [query],
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors='pt'
            ).to(self.device)
            
            outputs = self.model(**inputs)
            embedding = outputs.last_hidden_state[:, 0, :]
            embedding = torch.nn.functional.normalize(embedding, p=2, dim=1)
            
            return embedding.cpu().numpy()[0]
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """执行语义搜索
        
        Args:
            query: 搜索查询
            limit: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        # 编码查询
        query_vector = self.encode_query(query)
        
        # 连接数据库
        conn = psycopg2.connect(**self.db_params)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # 执行语义搜索
            search_sql = """
            SELECT 
                id,
                good_short_name,
                brand_name,
                price,
                catagory_full,
                sub_catagory,
                item_catagory,
                pic_url,
                LEFT(detail, 200) as detail_preview,
                1 - (embedding <=> %s) as similarity
            FROM goods 
            ORDER BY embedding <=> %s 
            LIMIT %s;
            """
            
            cursor.execute(search_sql, (query_vector.tolist(), query_vector.tolist(), limit))
            results = cursor.fetchall()
            
            return [dict(row) for row in results]
            
        finally:
            cursor.close()
            conn.close()
    
    def get_stats(self) -> Dict:
        """获取数据库统计信息
        
        Returns:
            统计信息字典
        """
        conn = psycopg2.connect(**self.db_params)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # 总商品数
            cursor.execute("SELECT COUNT(*) as total_goods FROM goods;")
            total_goods = cursor.fetchone()['total_goods']
            
            # 品牌数
            cursor.execute("SELECT COUNT(DISTINCT brand_name) as total_brands FROM goods;")
            total_brands = cursor.fetchone()['total_brands']
            
            # 分类数
            cursor.execute("SELECT COUNT(DISTINCT catagory_full) as total_categories FROM goods;")
            total_categories = cursor.fetchone()['total_categories']
            
            return {
                'total_goods': total_goods,
                'total_brands': total_brands,
                'total_categories': total_categories
            }
            
        finally:
            cursor.close()
            conn.close()

def print_search_results(results: List[Dict], query: str):
    """打印搜索结果
    
    Args:
        results: 搜索结果
        query: 搜索查询
    """
    print(f"\n🔍 搜索查询: '{query}'")
    print(f"📊 找到 {len(results)} 个相关商品\n")
    
    for i, result in enumerate(results, 1):
        similarity = result['similarity']
        print(f"#{i} [{similarity:.3f}] {result['good_short_name']}")
        print(f"   品牌: {result['brand_name']}")
        print(f"   价格: ¥{result['price']}")
        print(f"   分类: {result['catagory_full']}")
        if result['detail_preview']:
            print(f"   详情: {result['detail_preview']}...")
        print(f"   图片: {result['pic_url']}")
        print()

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python test_semantic_search.py \"搜索查询\"")
        print("示例: python test_semantic_search.py \"充电宝\"")
        return 1
    
    query = sys.argv[1]
    
    # 数据库连接参数
    db_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'reso'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password')
    }
    
    try:
        # 创建搜索器
        searcher = SemanticSearcher(db_params)
        
        # 获取统计信息
        stats = searcher.get_stats()
        print(f"📈 数据库统计:")
        print(f"   总商品数: {stats['total_goods']}")
        print(f"   品牌数: {stats['total_brands']}")
        print(f"   分类数: {stats['total_categories']}")
        
        # 执行搜索
        results = searcher.search(query, limit=5)
        
        # 打印结果
        print_search_results(results, query)
        
        # 提供一些搜索建议
        if not results:
            print("💡 搜索建议:")
            print("   - 尝试使用更通用的关键词")
            print("   - 检查拼写是否正确")
            print("   - 尝试使用商品分类或品牌名称")
        
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())