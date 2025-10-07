import os
from dotenv import load_dotenv
load_dotenv()

from pymilvus import connections
from pymilvus import utility
from pymilvus import FieldSchema, CollectionSchema, DataType, Collection

db_uri = os.getenv("MILVUS_URI")
db_token = os.getenv("MILVUS_TOKEN")

collection_name = "coll_hnsw_v6"

try:
    # Use the connection directly within this method
    connections.connect(alias="default", uri=db_uri, token=db_token)
    utility.drop_collection(collection_name)
except Exception as e:
    raise Exception(e)
finally:
    if connections:
        connections.disconnect("default")  # Ensure the connection is closed properly