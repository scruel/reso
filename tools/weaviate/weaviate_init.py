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
client.collections.delete(collection_name)
client.collections.create(
    name=collection_name,
    # 定义文本属性
    properties=[
        Property(name="goodId", data_type=DataType.INT),
        Property(name="name", data_type=DataType.TEXT),
        Property(name="price", data_type=DataType.TEXT),
        Property(name="brandName", data_type=DataType.TEXT),
        Property(name="catagory", data_type=DataType.TEXT),
        Property(name="subCatagory", data_type=DataType.TEXT),
        Property(name="itemCatagory", data_type=DataType.TEXT),
        Property(name="picUrl", data_type=DataType.TEXT),
        Property(name="detail", data_type=DataType.TEXT)
    ],
    # 定义向量属性
    vectorizer_config=[
        Configure.NamedVectors.none(name="name"),
        Configure.NamedVectors.none(name="detail"),
    ]
)

load_dotenv()
key = os.getenv("DASHSCOPE_API_KEY")
qwen = QwenEmbeddingService(key)

def insert(item):
    article_collection = client.collections.get(collection_name)
    
    # 检查是否已存在相同 ID 的数据
    from weaviate.classes.query import Filter
    existing_items = article_collection.query.fetch_objects(
        filters=Filter.by_property("goodId").equal(item["goodId"]),
        limit=1
    )
    
    if existing_items.objects:
        print(f"跳过插入: ID {item['goodId']} 已存在")
        return

    # 如果不存在，则插入新数据
    uuid = article_collection.data.insert(
        properties=item,
        # 添加向量数据
        vector={
            "name": qwen.get_embedding(item["name"]),
            "detail": qwen.get_embedding(item["detail"])
        }
    )
    print(f"成功插入: {uuid}")
    return uuid



def process_goods_directory(base_path="/home/scruel/reso/resource/good"):
    if not os.path.exists(base_path):
        print(f"目录不存在: {base_path}")
        return
    subdirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    for subdir in subdirs:
        subdir_path = os.path.join(base_path, subdir)
        clean_data_path = os.path.join(subdir_path, "clean_data.json")
        detail_path = os.path.join(subdir_path, "detail.txt")
        
        # 检查必要文件是否存在
        if not os.path.exists(clean_data_path) or not os.path.exists(detail_path):
            print(f"跳过文件夹 {subdir}: 缺少必要文件")
            continue
        
        try:
            # 读取 clean_data.json
            with open(clean_data_path, 'r', encoding='utf-8') as f:
                clean_data = json.load(f)

            # 读取 detail.txt
            with open(detail_path, 'r', encoding='utf-8') as f:
                detail_content = f.read()
            
            # 转换数据格式以匹配 weaviate_init.py 中的 insert 方法
            item = {
                "goodId": int(subdir),  # 使用文件夹名作为 id
                "name": clean_data.get("good_short_name", ""),
                "price": clean_data.get("price", ""),
                "brandName": clean_data.get("brand_name", ""),
                "catagory": clean_data.get("catagory_full", ""),
                "subCatagory": clean_data.get("sub_catagory", ""),
                "itemCatagory": clean_data.get("item_catagory", ""),
                "picUrl": clean_data.get("pic_url", ""),
                "detail": detail_content.strip()
            }
            
            print(f"处理商品 {subdir}: {item['name']}")
            # 调用 insert 方法插入数据
            insert(item)
            print(f"成功插入商品 {subdir}")
        except Exception as e:
            raise e
            print(f"处理文件夹 {subdir} 时出错: {str(e)}")
            continue

process_goods_directory()
client.close()  # Free up resources
