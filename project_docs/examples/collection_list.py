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
    # Print the available collections
    if collections:
        print("Available collections:")
        for collection in collections:
            print(collection)
    else:
        print("No collections found.")
except Exception as e:
    raise Exception(e)
finally:
    if connections:
        connections.disconnect("default")  # Ensure the connection is closed properly