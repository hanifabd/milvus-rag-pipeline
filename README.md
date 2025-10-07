# **Project Documentation: Information Retrieval Application**

## **Knowledges**
- Vector Database Comparison: https://medium.com/@mutahar789/optimizing-rag-a-guide-to-choosing-the-right-vector-database-480f71a33139
- Embedding Model Comparison: https://github.com/LazarusNLP/indonesian-sentence-embeddings

## **How to Run App**

### 1. Run Milvus Local 
```sh
cd milvus-services
sudo docker-compose up -d
```

### 2. Run Vectorizer Application
```sh
uvicorn app_vectorizer:app --host 0.0.0.0 --port 2025 --reload
# or
uvicorn app_vectorizer:app --host 0.0.0.0 --port 2025
```

### 3. Run Information Retrieval Application
```sh
uvicorn app_information_retrieval:app --host 0.0.0.0 --port 2024 --reload
# or
uvicorn app_information_retrieval:app --host 0.0.0.0 --port 2024
```

### 4. Run Worker for Insert Information
```sh
python -m celery --app=app_worker.insert_app worker --pool=eventlet --loglevel=INFO
# or
python -m celery --app=app_worker.insert_app worker --pool=gevent --loglevel=INFO
# or
python -m celery --app=app_worker.insert_app worker --pool=solo --loglevel=INFO
```