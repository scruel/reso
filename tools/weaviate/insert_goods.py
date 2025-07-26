import weaviate
from weaviate.classes.init import Auth
import os
from dotenv import load_dotenv
from weaviate.config import AdditionalConfig, Timeout

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


# client.close()  # Free up resources
