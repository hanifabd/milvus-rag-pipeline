import os
from pymilvus import connections
from pymilvus import utility
from pymilvus import FieldSchema, CollectionSchema, DataType, Collection
from dotenv import load_dotenv
load_dotenv()

class ManageVectorDB:
    def __init__(self):
        self.name = "ManageVectorDB"
        self.db_uri = os.getenv("MILVUS_URI")
        self.db_token = os.getenv("MILVUS_TOKEN")

    def check_collection_exists(self, collection_name):
        try:
            connections.connect(alias="default", uri=self.db_uri, token=self.db_token)
            is_exist = utility.has_collection(collection_name, "default")
            return is_exist
        except Exception as e:            
            raise Exception(f"Failed to check collections: {e}")
        finally:
            if connections:
                connections.disconnect("default")  # Ensure the connection is closed properly
    
    def create_collection(self, collection_name, collection_index_type):
        try:
            # Define collection schema with additional fields
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=384),  # 384, 768 Embedding dim -> Based on embedding model specification
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

            # Use the connection directly within this method
            connections.connect(alias="default", uri=self.db_uri, token=self.db_token)
            # Create the collection
            collection = Collection(
                name=collection_name, 
                schema=schema, 
                description="Embedding collection with metadata fields", 
                using="default", 
                consistency_level="Strong"
            )
            
            # Select params for IVF_FLAT or HNSW Index
            if collection_index_type == "IVF_FLAT":
                params = {
                    "nlist": 128
                }
            elif collection_index_type == "HNSW": 
                params = {
                    "M": 64,
                    "efConstruction": 64
                }
            
            # Create Collection
            collection.create_index(field_name="vector", index_params={
                "metric_type": "COSINE", 
                "index_type": collection_index_type, 
                "params": params
            })

            # Load Collection
            collection.load()
        except Exception as e:
            raise Exception(f"Failed to create collections: {e}")
        finally:
            if connections:
                connections.disconnect("default")  # Ensure the connection is closed properly

    def insert_into_collection(self, collection_name, data):
        try:
            # Use the connection directly within this method
            connections.connect(alias="default", uri=self.db_uri, token=self.db_token)
            # Get the collection object
            collection = Collection(name=collection_name, using="default")    
            # Insert the data into the collection
            insert_info = collection.insert(data)
            return insert_info  # Optionally return the insert_info if needed
        except Exception as e:
            raise Exception(f"Failed to insert data into collection '{collection_name}': {e}")
        finally:
            if connections:
                connections.disconnect("default")  # Ensure the connection is closed properly
    
    def delete_in_collection(self, client_id, project_id, collection_name, file_id):
        try:
            # Use the connection directly within this method
            connections.connect(alias="default", uri=self.db_uri, token=self.db_token)
            # Get the collection object
            collection = Collection(name=collection_name, using="default")
            # Delete
            delete_response = collection.delete(expr=f"client_id == '{client_id}' && project_id == '{project_id}' && file_id == '{file_id}'")
            return delete_response
        except Exception as e:
            raise Exception(f"Failed to delete in collections: {e}")
        finally:
            if connections:
                connections.disconnect("default")  # Ensure the connection is closed properly

    def search_in_collection(self, client_id, project_id, collection_name, collection_index_type, vector_query, number_results):
        try:
            # Use the connection directly within this method
            connections.connect(alias="default", uri=self.db_uri, token=self.db_token)
            # Get the collection object
            collection = Collection(name=collection_name, using="default")
            
            # Select params for IVF_FLAT or HNSW Index
            if collection_index_type == "IVF_FLAT":
                params = {
                    "nprobe": 32
                }
            elif collection_index_type == "HNSW": 
                params = {
                    "ef": 64
                }
            
            # Search
            results = collection.search(
                data=vector_query,
                anns_field="vector",
                output_fields=["text"],
                limit=number_results,
                filter=f"client_id == '{client_id}' AND project_id == '{project_id}'",
                param=params
            )
            return results
        except Exception as e:
            raise Exception(f"Failed to search in collections: {e}")
        finally:
            if connections:
                connections.disconnect("default")  # Ensure the connection is closed properly