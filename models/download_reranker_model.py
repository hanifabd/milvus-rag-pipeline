from huggingface_hub import snapshot_download

# Define the model name and download path
model_name = "BAAI/bge-reranker-base"
# model_name = "BAAI/bge-reranker-v2-m3"
models_path = f"onprem-{model_name.split('/')[1]}"

# Download and save the model snapshot locally
snapshot_download(repo_id=model_name, local_dir=models_path, ignore_patterns=["consolidated.safetensors"])
