import logging
import uvicorn
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Union, List
from ManageEmbeddingModel import get_sentence_transformers_model
from ManageEmbeddingRerankModel import get_reranker_model_model

# Logging Settings
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Initialize the FastAPI app
app = FastAPI()
sentence_transformers_model = get_sentence_transformers_model()
reranker_model = get_reranker_model_model()

# Define request models
class SingleTextRequest(BaseModel):
    text: str

class TextListRequest(BaseModel):
    texts: List[str] = Field(..., description="List of texts to encode")

class RerankerRequest(BaseModel):
    query: str
    top_k: int
    documents: List[str]

# Endpoint for encoding a single text
@app.post("/vectorize-query")
async def vectorize_query(request: SingleTextRequest):
    text = request.text
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")

    # Vectorize the single text query
    vector_query = sentence_transformers_model.encode_queries([text])
    return {"vector": [vector_query[0].tolist()]}

# Endpoint for encoding a list of texts (documents)
@app.post("/vectorize-documents")
async def vectorize_documents(request: TextListRequest):
    texts = request.texts
    if not texts:
        raise HTTPException(status_code=400, detail="No texts provided")

    # Vectorize the list of texts
    vectors = sentence_transformers_model.encode_documents(texts)
    return {"vectors": [vector.tolist() for vector in vectors]}

# Endpoint for Reranking Documents
@app.post("/rerank-documents")
async def rerank_documents(request: RerankerRequest):
    # Rerank Documents
    reranked_documents = reranker_model(query=request.query, documents=request.documents, top_k=request.top_k)

    return {
        "query": request.query,
        "reranked-documents": reranked_documents
    }

if __name__ == "__main__":    
    log.info(f"{Path(__file__).stem}:app")
    uvicorn.run(f"{Path(__file__).stem}:app", port=2025, host="0.0.0.0")