import torch
from pymilvus import model

model_path = "./models/onprem-multilingual-e5-small"
device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
print(f"Embedding Model Device: {device}")
sentence_transformers_model = model.dense.SentenceTransformerEmbeddingFunction(
    model_name=model_path,
    device=device
)

def get_sentence_transformers_model():
    """Return the global model instance."""
    return sentence_transformers_model