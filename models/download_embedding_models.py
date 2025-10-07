# Download the model and Save the model locally
from sentence_transformers import SentenceTransformer

model_name = "BAAI/bge-reranker-v2-m3"
# model_name = 'intfloat/multilingual-e5-base'
# model_name = 'sentence-transformers/all-MiniLM-L6-v2'
model = SentenceTransformer(model_name)

models_path = f"onprem-{model_name.split('/')[1]}"
model.save(f"onprem-{model_name.split('/')[1]}")