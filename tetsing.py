import os
import pandas as pd
import numpy as np
from ast import literal_eval
import dashscope
from dashscope import TextEmbedding

# 设置DashScope的API Key
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")


# 读取CSV数据
datafile_path = "fine_food_reviews.csv"
df = pd.read_csv(datafile_path)

# 将embedding列的字符串数据转换为NumPy数组
df["embedding"] = df.embedding.apply(literal_eval).apply(np.array)


# 定义文本嵌入的函数
def generate_embeddings(text):
    rsp = TextEmbedding.call(model=TextEmbedding.Models.text_embedding_v3, input=text)
    embeddings = [record['embedding'] for record in rsp.output['embeddings']]
    return embeddings if isinstance(text, list) else embeddings[0]

results = search_reviews(df, "pet food", n=2)


# 定义函数：生成文本的嵌入向量（embedding）
def generate_embeddings(text):
    """
    使用 DashScope 的 text-embedding-v3 模型生成输入文本的嵌入向量。
    Args:
        text (str or list): 输入文本字符串或字符串列表。
    Returns:
        list: 如果输入为字符串，返回单个嵌入向量；若输入为列表，返回多个向量。
    """
    rsp = TextEmbedding.call(model=TextEmbedding.Models.text_embedding_v3, input=text)
    # 从 API 响应中提取 embedding
    embeddings = [record['embedding'] for record in rsp.output['embeddings']]
    return embeddings if isinstance(text, list) else embeddings[0]

# 加载数据集
dataset_path = "sampled_file.csv"  # 数据集路径
df = pd.read_csv(dataset_path)  # 读取CSV文件到 DataFrame
n_examples = 5  # 设置展示的示例数量

# 展示前 n_examples 个样本的发布日期与标题
print("展示数据集中的前几个样本：")
for idx, row in df.head(n_examples).iterrows():
    print("")
    print(f"发布日期: {row['publish_date']}")
    print(f"标题: {row['headline_text']}")

# 设置嵌入缓存路径（避免重复计算）
embedding_cache_path = "recommendations_embeddings_cache.pkl"

# 尝试加载已缓存的嵌入结果，若无缓存则初始化一个空字典
try:
    embedding_cache = pd.read_pickle(embedding_cache_path)
except FileNotFoundError:
    embedding_cache = {}

# 定义函数：通过缓存机制获取文本的嵌入向量
def embedding_from_string(
    string: str,
    embedding_cache=embedding_cache
) -> list:
    """
    获取给定文本的嵌入向量，使用缓存机制避免重复计算。
    Args:
        string (str): 输入文本字符串。
        embedding_cache (dict): 嵌入缓存字典。
    Returns:
        list: 生成的嵌入向量。
    """
    if string not in embedding_cache.keys():  # 如果缓存中不存在该文本
        embedding_cache[string] = generate_embeddings(string)  # 生成并缓存嵌入
        # 保存缓存到文件
        with open(embedding_cache_path, "wb") as embedding_cache_file:
            pickle.dump(embedding_cache, embedding_cache_file)
    return embedding_cache[string]

# 计算示例字符串的嵌入向量
example_string = df["headline_text"].values[0]  # 选取数据集中的第一个文本
print(f"\n示例文本: {example_string}")
example_embedding = embedding_from_string(example_string)  # 获取嵌入
print(f"\n示例文本的嵌入向量（前10维）: {example_embedding[:10]}...")
print("\n")


# 定义推荐函数：输出与给定文本最相似的字符串
def print_recommendations_from_strings(
        strings,  # list[str]: 输入的字符串列表
        index_of_source_string,  # int: 源字符串在列表中的索引
        k_nearest_neighbors=1,  # int: 推荐的相似字符串数量
):
    """
    输出与源字符串最相似的 k 个字符串。
    Args:
        strings (list): 输入字符串列表。
        index_of_source_string (int): 源字符串在列表中的索引。
        k_nearest_neighbors (int): 要推荐的近邻数量。
    """
    # 生成所有输入字符串的嵌入向量
    embeddings = [embedding_from_string(string) for string in strings]
    # 获取源字符串的嵌入向量
    query_embedding = embeddings[index_of_source_string]

    # 定义余弦相似度函数
    def cosine_similarity(vec1, vec2):
        """
        计算两个向量之间的余弦相似度。
        Args:
            vec1 (list): 向量1
            vec2 (list): 向量2
        Returns:
            float: 余弦相似度值
        """
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    # 计算源嵌入与所有嵌入之间的距离（1 - 相似度）
    distances = [1 - cosine_similarity(query_embedding, emb) for emb in embeddings]

    # 按照距离升序排列，获取最近邻的索引
    indices_of_nearest_neighbors = np.argsort(distances)

    # 打印源字符串
    query_string = strings[index_of_source_string]
    print(f"源文本: {query_string}")

    # 打印最相似的 k 个字符串及相似度
    k_counter = 0
    for i in indices_of_nearest_neighbors:
        if query_string == strings[i]:  # 跳过与自身的比较
            continue
        if k_counter >= k_nearest_neighbors:  # 限定推荐数量
            break
        k_counter += 1
        print(
            f"""
        --- 推荐 #{k_counter} ---
        相似文本: {strings[i]}
        相似度: {1 - distances[i]:0.3f}"""
        )
    return indices_of_nearest_neighbors

# 获取文章标题列表
article_titles = df["headline_text"].tolist()

# 获取基于某个文本的推荐结果
print("基于文本推荐示例：")
print("财经相关文章推荐")
recommendations = print_recommendations_from_strings(
    strings=article_titles,  # 输入文章标题列表
    index_of_source_string=0,  # 选取第一个文本作为源文本
    k_nearest_neighbors=5,  # 推荐5个最相似的文本
)