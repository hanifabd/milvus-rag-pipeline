import os
from dotenv import load_dotenv
load_dotenv()

from pymilvus import connections
from pymilvus import utility
from pymilvus import FieldSchema, CollectionSchema, DataType, Collection

db_uri = os.getenv("MILVUS_URI")
db_token = os.getenv("MILVUS_TOKEN")

try:
    # Use the connection directly within this method
    connections.connect(alias="default", uri=db_uri, token=db_token)
    # Get existing collections
    collections = utility.list_collections()

    # Check Number of Data
    for collection_name in collections:
        collection = Collection(collection_name)
        print(f"{collection_name} - {collection.indexes}")
except Exception as e:
    raise Exception(e)
finally:
    if connections:
        connections.disconnect("default")  # Ensure the connection is closed properly