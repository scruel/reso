#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商品数据自动导入 PGVector 工具

该脚本用于将 resource/good 目录下的商品信息自动导入到 PGVector 数据库中，
使用 qwen-embedding 模型进行向量化索引，实现语义化搜索功能。

使用方法:
    python import_goods_to_pgvector.py

环境要求:
    - PostgreSQL with pgvector extension
    - transformers
    - psycopg2-binary
    - torch
    - numpy
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('import_goods.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class QwenEmbedding:
    """Qwen 嵌入模型封装类"""
    
    def __init__(self, model_name: str = "Alibaba-NLP/gte-Qwen2-1.5B-instruct"):
        """初始化 Qwen 嵌入模型
        
        Args:
            model_name: 模型名称，默认使用 gte-Qwen2-1.5B-instruct
        """
        self.model_name = model_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"使用设备: {self.device}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
            self.model.to(self.device)
            self.model.eval()
            logger.info(f"成功加载模型: {model_name}")
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            raise
    
    def encode(self, texts: List[str], max_length: int = 512) -> np.ndarray:
        """将文本编码为向量
        
        Args:
            texts: 待编码的文本列表
            max_length: 最大序列长度
            
        Returns:
            编码后的向量数组
        """
        try:
            with torch.no_grad():
                inputs = self.tokenizer(
                    texts,
                    padding=True,
                    truncation=True,
                    max_length=max_length,
                    return_tensors='pt'
                ).to(self.device)
                
                outputs = self.model(**inputs)
                # 使用 [CLS] token 的输出作为句子嵌入
                embeddings = outputs.last_hidden_state[:, 0, :]
                
                # 归一化
                embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
                
                return embeddings.cpu().numpy()
        except Exception as e:
            logger.error(f"文本编码失败: {e}")
            raise

class PGVectorDB:
    """PGVector 数据库操作类"""
    
    def __init__(self, connection_params: Dict[str, str]):
        """初始化数据库连接
        
        Args:
            connection_params: 数据库连接参数
        """
        self.connection_params = connection_params
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """连接数据库"""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def disconnect(self):
        """断开数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("数据库连接已断开")
    
    def create_table(self, vector_dim: int = 1536):
        """创建商品表
        
        Args:
            vector_dim: 向量维度
        """
        try:
            # 启用 pgvector 扩展
            self.cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # 创建商品表
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS goods (
                id SERIAL PRIMARY KEY,
                good_short_name VARCHAR(255) NOT NULL,
                price VARCHAR(50),
                brand_name VARCHAR(255),
                catagory_full VARCHAR(500),
                sub_catagory VARCHAR(255),
                item_catagory VARCHAR(255),
                pic_url TEXT,
                detail TEXT,
                embedding vector({vector_dim}),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            self.cursor.execute(create_table_sql)
            
            # 创建向量索引
            index_sql = """
            CREATE INDEX IF NOT EXISTS goods_embedding_idx 
            ON goods USING ivfflat (embedding vector_cosine_ops) 
            WITH (lists = 100);
            """
            
            self.cursor.execute(index_sql)
            self.conn.commit()
            logger.info("商品表创建成功")
            
        except Exception as e:
            logger.error(f"创建表失败: {e}")
            self.conn.rollback()
            raise
    
    def insert_good(self, good_data: Dict, embedding: np.ndarray):
        """插入商品数据
        
        Args:
            good_data: 商品数据字典
            embedding: 商品嵌入向量
        """
        try:
            insert_sql = """
            INSERT INTO goods (
                good_short_name, price, brand_name, catagory_full, 
                sub_catagory, item_catagory, pic_url, detail, embedding
            ) VALUES (
                %(good_short_name)s, %(price)s, %(brand_name)s, %(catagory_full)s,
                %(sub_catagory)s, %(item_catagory)s, %(pic_url)s, %(detail)s, %(embedding)s
            )
            """
            
            # 将 numpy 数组转换为列表
            good_data['embedding'] = embedding.tolist()
            
            self.cursor.execute(insert_sql, good_data)
            self.conn.commit()
            logger.info(f"成功插入商品: {good_data['good_short_name']}")
            
        except Exception as e:
            logger.error(f"插入商品失败: {e}")
            self.conn.rollback()
            raise
    
    def check_good_exists(self, good_short_name: str) -> bool:
        """检查商品是否已存在
        
        Args:
            good_short_name: 商品短名称
            
        Returns:
            是否存在
        """
        try:
            self.cursor.execute(
                "SELECT id FROM goods WHERE good_short_name = %s",
                (good_short_name,)
            )
            return self.cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"检查商品存在性失败: {e}")
            return False

class GoodsImporter:
    """商品导入器"""
    
    def __init__(self, goods_dir: str, db_params: Dict[str, str]):
        """初始化导入器
        
        Args:
            goods_dir: 商品数据目录
            db_params: 数据库连接参数
        """
        self.goods_dir = Path(goods_dir)
        self.db = PGVectorDB(db_params)
        self.embedding_model = QwenEmbedding()
        
    def load_good_data(self, good_folder: Path) -> Optional[Dict]:
        """加载单个商品数据
        
        Args:
            good_folder: 商品文件夹路径
            
        Returns:
            商品数据字典或 None
        """
        try:
            # 读取 clean_data.json
            json_file = good_folder / "clean_data.json"
            if not json_file.exists():
                logger.warning(f"未找到 clean_data.json: {good_folder}")
                return None
                
            with open(json_file, 'r', encoding='utf-8') as f:
                good_data = json.load(f)
            
            # 读取 detail.txt
            detail_file = good_folder / "detail.txt"
            if detail_file.exists():
                with open(detail_file, 'r', encoding='utf-8') as f:
                    good_data['detail'] = f.read().strip()
            else:
                good_data['detail'] = ""
                logger.warning(f"未找到 detail.txt: {good_folder}")
            
            return good_data
            
        except Exception as e:
            logger.error(f"加载商品数据失败 {good_folder}: {e}")
            return None
    
    def create_embedding_text(self, good_data: Dict) -> str:
        """创建用于嵌入的文本
        
        Args:
            good_data: 商品数据
            
        Returns:
            组合后的文本
        """
        # 组合所有文本信息用于嵌入
        text_parts = [
            good_data.get('good_short_name', ''),
            good_data.get('brand_name', ''),
            good_data.get('catagory_full', ''),
            good_data.get('sub_catagory', ''),
            good_data.get('item_catagory', ''),
            good_data.get('detail', '')
        ]
        
        # 过滤空字符串并连接
        return ' '.join(filter(None, text_parts))
    
    def import_all_goods(self, skip_existing: bool = True):
        """导入所有商品
        
        Args:
            skip_existing: 是否跳过已存在的商品
        """
        try:
            # 连接数据库
            self.db.connect()
            
            # 创建表
            # 获取嵌入维度（使用示例文本测试）
            test_embedding = self.embedding_model.encode(["测试文本"])
            vector_dim = test_embedding.shape[1]
            logger.info(f"向量维度: {vector_dim}")
            
            self.db.create_table(vector_dim)
            
            # 遍历商品文件夹
            good_folders = [d for d in self.goods_dir.iterdir() if d.is_dir()]
            logger.info(f"找到 {len(good_folders)} 个商品文件夹")
            
            success_count = 0
            skip_count = 0
            error_count = 0
            
            for good_folder in good_folders:
                try:
                    # 加载商品数据
                    good_data = self.load_good_data(good_folder)
                    if not good_data:
                        error_count += 1
                        continue
                    
                    # 检查是否已存在
                    if skip_existing and self.db.check_good_exists(good_data['good_short_name']):
                        logger.info(f"商品已存在，跳过: {good_data['good_short_name']}")
                        skip_count += 1
                        continue
                    
                    # 创建嵌入文本
                    embedding_text = self.create_embedding_text(good_data)
                    
                    # 生成嵌入向量
                    embedding = self.embedding_model.encode([embedding_text])[0]
                    
                    # 插入数据库
                    self.db.insert_good(good_data, embedding)
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"处理商品失败 {good_folder.name}: {e}")
                    error_count += 1
                    continue
            
            logger.info(f"导入完成 - 成功: {success_count}, 跳过: {skip_count}, 错误: {error_count}")
            
        except Exception as e:
            logger.error(f"导入过程失败: {e}")
            raise
        finally:
            self.db.disconnect()

def main():
    """主函数"""
    # 数据库连接参数（请根据实际情况修改）
    db_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'reso'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password')
    }
    
    # 商品数据目录
    goods_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resource', 'good')
    
    logger.info("开始导入商品数据到 PGVector")
    logger.info(f"商品数据目录: {goods_dir}")
    logger.info(f"数据库连接: {db_params['host']}:{db_params['port']}/{db_params['database']}")
    
    try:
        # 创建导入器并执行导入
        importer = GoodsImporter(goods_dir, db_params)
        importer.import_all_goods(skip_existing=True)
        
        logger.info("商品数据导入完成！")
        
    except Exception as e:
        logger.error(f"导入失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())