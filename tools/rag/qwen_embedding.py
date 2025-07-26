"""
Qwen文本嵌入服务封装
基于DashScope API的文本嵌入功能
"""

import os
import pickle
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from typing import List, Union, Dict, Optional
import dashscope
from dashscope import TextEmbedding
import logging

logger = logging.getLogger(__name__)

load_dotenv()

class KimiGPTService:
    """
    Kimi文本嵌入服务
    
    支持缓存机制，避免重复计算
    """
    
    def __init__(self, api_key: Optional[str] = None, cache_path: str = "kimi_embeddings_cache.pkl"):
        """
        初始化Kimi嵌入服务
        
        Args:
            api_key: Kimi API密钥，如果为None则从环境变量KIMI_API_KEY获取
            cache_path: 嵌入缓存文件路径
        """
        # 设置API密钥
        self.api_key = api_key or os.getenv("KIMI_API_KEY")
        if not self.api_key:
            raise ValueError("Kimi API密钥未设置，请设置KIMI_API_KEY环境变量或传入api_key参数")
        
        self.api_key = self.api_key
        self.cache_path = cache_path
        self.base_url = "https://api.moonshot.cn/v1"
      
    def geneate(text: str):
      return ''

class QwenEmbeddingService:
    """
    Qwen文本嵌入服务
    
    使用DashScope的text-embedding-v3模型生成文本嵌入向量
    支持缓存机制，避免重复计算
    """
    
    def __init__(self, api_key: Optional[str] = None, cache_path: str = "qwen_embeddings_cache.pkl"):
        """
        初始化Qwen嵌入服务
        
        Args:
            api_key: DashScope API密钥，如果为None则从环境变量DASHSCOPE_API_KEY获取
            cache_path: 嵌入缓存文件路径
        """
        # 设置API密钥
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("DashScope API密钥未设置，请设置DASHSCOPE_API_KEY环境变量或传入api_key参数")
        
        dashscope.api_key = self.api_key
        self.cache_path = cache_path
        self.embedding_cache = self._load_cache()    
      
      
        
    def _load_cache(self) -> Dict[str, List[float]]:
        """加载嵌入缓存"""
        try:
            with open(self.cache_path, "rb") as f:
                cache = pickle.load(f)
            logger.info(f"已加载嵌入缓存，包含 {len(cache)} 个条目")
            return cache
        except FileNotFoundError:
            logger.info("未找到缓存文件，将创建新缓存")
            return {}
        except Exception as e:
            logger.warning(f"加载缓存失败: {e}，将创建新缓存")
            return {}
    
    def _save_cache(self):
        """保存嵌入缓存"""
        try:
            with open(self.cache_path, "wb") as f:
                pickle.dump(self.embedding_cache, f)
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
    
    def generate_embeddings(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        生成文本嵌入向量
        
        Args:
            text: 输入文本字符串或字符串列表
            
        Returns:
            如果输入为字符串，返回单个嵌入向量；如果输入为列表，返回多个向量
        """
        try:
            response = TextEmbedding.call(
                model=TextEmbedding.Models.text_embedding_v3, 
                input=text
            )
            
            if response.status_code != 200:
                raise Exception(f"API调用失败: {response.message}")
            
            embeddings = [record['embedding'] for record in response.output['embeddings']]
            return embeddings if isinstance(text, list) else embeddings[0]
            
        except Exception as e:
            logger.error(f"生成嵌入向量失败: {e}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """
        获取单个文本的嵌入向量（带缓存）
        
        Args:
            text: 输入文本
            
        Returns:
            嵌入向量
        """
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        # 生成新的嵌入向量
        embedding = self.generate_embeddings(text)
        
        # 缓存结果
        self.embedding_cache[text] = embedding
        self._save_cache()
        
        return embedding
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量获取嵌入向量
        
        Args:
            texts: 文本列表
            
        Returns:
            嵌入向量列表
        """
        # 检查缓存，分离已缓存和未缓存的文本
        cached_embeddings = {}
        uncached_texts = []
        uncached_indices = []
        
        for i, text in enumerate(texts):
            if text in self.embedding_cache:
                cached_embeddings[i] = self.embedding_cache[text]
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        # 批量生成未缓存的嵌入向量
        if uncached_texts:
            new_embeddings = self.generate_embeddings(uncached_texts)
            
            # 更新缓存
            for text, embedding in zip(uncached_texts, new_embeddings):
                self.embedding_cache[text] = embedding
            
            self._save_cache()
            
            # 将新的嵌入向量添加到结果中
            for i, embedding in zip(uncached_indices, new_embeddings):
                cached_embeddings[i] = embedding
        
        # 按原始顺序返回结果
        return [cached_embeddings[i] for i in range(len(texts))]
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        计算两个向量的余弦相似度
        
        Args:
            vec1: 向量1
            vec2: 向量2
            
        Returns:
            余弦相似度值 (0-1)
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def find_similar_texts(
        self, 
        query_text: str, 
        candidate_texts: List[str], 
        top_k: int = 5
    ) -> List[Dict]:
        """
        找到与查询文本最相似的候选文本
        
        Args:
            query_text: 查询文本
            candidate_texts: 候选文本列表
            top_k: 返回最相似的前k个结果
            
        Returns:
            相似度结果列表，每个元素包含 {'text': str, 'similarity': float, 'index': int}
        """
        # 获取查询文本的嵌入向量
        query_embedding = self.get_embedding(query_text)
        
        # 获取候选文本的嵌入向量
        candidate_embeddings = self.get_embeddings_batch(candidate_texts)
        
        # 计算相似度
        similarities = []
        for i, candidate_embedding in enumerate(candidate_embeddings):
            similarity = self.cosine_similarity(query_embedding, candidate_embedding)
            similarities.append({
                'text': candidate_texts[i],
                'similarity': similarity,
                'index': i
            })
        
        # 按相似度排序并返回前k个
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]
    
    def recommend_from_list(
        self, 
        texts: List[str], 
        source_index: int, 
        top_k: int = 5
    ) -> List[Dict]:
        """
        从文本列表中推荐与源文本最相似的其他文本
        
        Args:
            texts: 文本列表
            source_index: 源文本在列表中的索引
            top_k: 推荐数量
            
        Returns:
            推荐结果列表
        """
        if source_index >= len(texts):
            raise ValueError(f"源文本索引 {source_index} 超出范围")
        
        source_text = texts[source_index]
        candidate_texts = [text for i, text in enumerate(texts) if i != source_index]
        
        results = self.find_similar_texts(source_text, candidate_texts, top_k)
        
        # 调整索引以反映原始列表中的位置
        for result in results:
            original_index = texts.index(result['text'])
            result['original_index'] = original_index
        
        return results
    
    def clear_cache(self):
        """清空缓存"""
        self.embedding_cache = {}
        try:
            os.remove(self.cache_path)
        except FileNotFoundError:
            pass
        logger.info("缓存已清空")
    
    def get_cache_info(self) -> Dict:
        """获取缓存信息"""
        return {
            'cache_size': len(self.embedding_cache),
            'cache_path': self.cache_path
        }


class QwenTextRecommender:
    """
    基于Qwen嵌入的文本推荐系统
    """
    
    def __init__(self, embedding_service: QwenEmbeddingService):
        """
        初始化推荐系统
        
        Args:
            embedding_service: Qwen嵌入服务实例
        """
        self.embedding_service = embedding_service
    
    def load_data_from_csv(self, csv_path: str, text_column: str) -> pd.DataFrame:
        """
        从CSV文件加载数据
        
        Args:
            csv_path: CSV文件路径
            text_column: 包含文本的列名
            
        Returns:
            加载的DataFrame
        """
        df = pd.read_csv(csv_path)
        if text_column not in df.columns:
            raise ValueError(f"列 '{text_column}' 不存在于CSV文件中")
        return df
    
    def recommend_similar_articles(
        self, 
        df: pd.DataFrame, 
        text_column: str, 
        query_text: str = None,
        source_index: int = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        推荐相似文章
        
        Args:
            df: 包含文章的DataFrame
            text_column: 文本列名
            query_text: 查询文本（与source_index二选一）
            source_index: 源文章索引（与query_text二选一）
            top_k: 推荐数量
            
        Returns:
            推荐结果列表
        """
        texts = df[text_column].tolist()
        
        if query_text is not None:
            results = self.embedding_service.find_similar_texts(query_text, texts, top_k)
        elif source_index is not None:
            results = self.embedding_service.recommend_from_list(texts, source_index, top_k)
        else:
            raise ValueError("必须提供 query_text 或 source_index 其中之一")
        
        # 添加完整的行信息
        for result in results:
            if 'original_index' in result:
                row_index = result['original_index']
            else:
                row_index = result['index']
            result['row_data'] = df.iloc[row_index].to_dict()
        
        return results
    
    def print_recommendations(self, results: List[Dict], show_similarity: bool = True):
        """
        打印推荐结果
        
        Args:
            results: 推荐结果列表
            show_similarity: 是否显示相似度分数
        """
        print("\n=== 推荐结果 ===")
        for i, result in enumerate(results, 1):
            print(f"\n--- 推荐 #{i} ---")
            print(f"文本: {result['text']}")
            if show_similarity:
                print(f"相似度: {result['similarity']:.3f}")
            
            # 如果有额外的行数据，可以显示其他信息
            if 'row_data' in result:
                row_data = result['row_data']
                for key, value in row_data.items():
                    if key != result.get('text_column', 'text') and pd.notna(value):
                        print(f"{key}: {value}") 
