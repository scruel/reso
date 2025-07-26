import weaviate
from weaviate.classes.init import Auth
import os
import json
from dotenv import load_dotenv
from weaviate.config import AdditionalConfig, Timeout
from weaviate.auth import AuthApiKey
from weaviate.classes.config import Property, DataType
from weaviate.collections.classes.config import Configure
from weaviate.collections.classes.grpc import MetadataQuery
from tools.embeddings.qwen_embedding import QwenEmbeddingService

# Best practice: store your credentials in environment variables
load_dotenv()
weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")

client = weaviate.connect_to_custom(
    http_host='weaviate-http.zeabur.app',
    http_port=443,
    http_secure=True,
    grpc_host='weaviate-grpc.zeabur.app',
    grpc_port=443,
    grpc_secure=True,
    auth_credentials=Auth.api_key('P0pQ5zi27awJM1ht968rUWbDm4lHCA3V'),
    additional_config=AdditionalConfig(
        timeout=Timeout(init=30, query=60, insert=120)),
)

collection_name = "ResoGoods"
load_dotenv()
key = os.getenv("DASHSCOPE_API_KEY")
qwen = QwenEmbeddingService(key)

def query(text: str):
    article_collection = client.collections.get(collection_name)
    vector = qwen.get_embedding(text)
    response = article_collection.query.near_vector(
        # 指定目标向量
        target_vector="detail",
        # 文本向量
        near_vector=vector,
        # 限制输出的数量
        limit=10,
        # 设置返回的数据是否显示距离
        return_metadata=MetadataQuery(distance=True)
    )

    # 展示数据
    for o in response.objects:
        print(o.properties)
        print(o.metadata.distance)

    client.close()  # Free up resources
