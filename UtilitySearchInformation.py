import os
from dotenv import load_dotenv
load_dotenv()
import httpx
from ManageVectorDB import ManageVectorDB

class SearchInformation:
    def __init__(self):
        self.name = "InsertInformation"
        self.vectorize_url = os.getenv("VECTOR_QUERY_URI")
        self.reranker_url = os.getenv("RERANK_DOCS_URI")

    async def vectorize_query(self, query):
        """Send async request to vectorize the query."""
        async with httpx.AsyncClient() as client:
            response = await client.post(self.vectorize_url, json={"text": query})
            if response.status_code != 200:
                raise Exception(f"Failed to vectorize query: {response.text}")
            vector_query = response.json().get("vector")
        if not vector_query:
            raise Exception("No vector returned from vectorization service")
        return vector_query

    async def rerank_documents(self, query, documents, top_k):
        """Send async request to rerank documents."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.reranker_url,
                json={"query": query, "documents": documents, "top_k": top_k}
            )
            if response.status_code != 200:
                raise Exception(f"Failed to rerank documents: {response.text}")
            reranked_documents = response.json().get("reranked-documents")
        if not reranked_documents:
            raise Exception("No documents returned from reranker service")
        return reranked_documents

    async def format_rerank_results(self, results):
        result_dicts = []
        for data in results:
            for item in data:
                result_dicts.append(item.fields.get("text"))
        return result_dicts

    async def search_information(self, client_id, project_id, collection_name, collection_index_type, query, number_results, rerank):
        # Vectorize the query
        vector_query = await self.vectorize_query(query)
        # Perform the search with the vectorized query
        db_engine = ManageVectorDB()
        search_result = db_engine.search_in_collection(
            client_id,
            project_id,
            collection_name,
            collection_index_type,
            vector_query,
            number_results
        )
        # Rerank if needed
        if rerank:
            reranker_formated_documents = await self.format_rerank_results(search_result)
            search_result = await self.rerank_documents(query, reranker_formated_documents, number_results)
        return search_result

    async def format_search_results(self, results):
        try:
            result_dicts = []
            for data in results:
                for item in data:
                    entry = {
                        "score": item.distance,
                        "text": item.fields.get("text")
                    }
                    result_dicts.append(entry)
        except:
            result_dicts = results
        return result_dicts

