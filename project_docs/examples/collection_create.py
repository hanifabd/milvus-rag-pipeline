import os
from dotenv import load_dotenv
load_dotenv()

from pymilvus import connections
from pymilvus import utility
from pymilvus import FieldSchema, CollectionSchema, DataType, Collection

db_uri = os.getenv("MILVUS_URI")
db_token = os.getenv("MILVUS_TOKEN")

collection_name = "ex_collection_name"

try:
    # Use the connection directly within this method
    connections.connect(alias="default", uri=db_uri, token=db_token)
    # Define collection schema with additional fields
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=384),  # Embedding dim -> Based on embedding model specification
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),  # Long text field
        FieldSchema(name="file_path", dtype=DataType.VARCHAR, max_length=1024),  # Text field for file path
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=1024),  # Text field for title
        FieldSchema(name="total_pages", dtype=DataType.INT64),  # Integer field for total pages
        FieldSchema(name="format", dtype=DataType.VARCHAR, max_length=256),  # Text field for format
        FieldSchema(name="client_id", dtype=DataType.VARCHAR, max_length=256),  # Text field for client ID
        FieldSchema(name="project_id", dtype=DataType.VARCHAR, max_length=256),  # Text field for project ID
        FieldSchema(name="file_id", dtype=DataType.VARCHAR, max_length=256)  # Text field for file ID
    ]
    schema = CollectionSchema(fields=fields, description="Collection for information storage")

    # Create the collection
    collection = Collection(
        name=collection_name, 
        schema=schema, 
        description="Embedding collection with metadata fields", 
        using="default", 
        consistency_level="Strong"
    )
    # IVF_FLAT Index
    collection.create_index(field_name="vector", index_params={
        "metric_type": "COSINE", 
        "index_type": "IVF_FLAT", 
        "params": {
            "nlist": 64  # 128 - Controls the number of clusters in the IVF index
        }
    })
    # # HNSW Index
    # collection.create_index(field_name="vector", index_params={
    #     "metric_type": "COSINE",
    #     "index_type": "HNSW",
    #     "params": {
    #         "M": 16,  # Number of bi-directional links created for every new added node
    #         "efConstruction": 200  # Controls the size of the dynamic list for nearest neighbors during index construction
    #     }
    # })
except Exception as e:
    raise Exception(e)
finally:
    if connections:
        connections.disconnect("default")  # Ensure the connection is closed properly