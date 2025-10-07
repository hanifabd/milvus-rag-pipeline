import torch
from pymilvus import model

model_path = "./models/onprem-bge-reranker-base"
device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
print(f"Reranker Model Device: {device}")
reranker_model = model.reranker.BGERerankFunction(
    model_name=model_path,
    device=device,
    use_fp16=True
)

def get_reranker_model_model():
    """Return the global model instance."""
    return reranker_model