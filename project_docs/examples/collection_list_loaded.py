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

    # Check which collections are loaded
    loaded_collections = []
    for collection in collections:
        # Get collection info to check if it's loaded
        if str(utility.load_state(collection, using="default", timeout=None)) == "Loaded":
            loaded_collections.append(f"{collection} - Loaded")
        else:
            loaded_collections.append(f"{collection} - Not Loaded")
            
    # Print the loaded collections
    if loaded_collections:
        print("Loaded collections:")
        for collection in loaded_collections:
            print(collection)
    else:
        print("No collections are currently loaded.")
except Exception as e:
    raise Exception(e)
finally:
    if connections:
        connections.disconnect("default")  # Ensure the connection is closed properly