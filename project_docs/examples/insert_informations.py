import requests
import json

url = "http://127.0.0.1:2024/insert"

payload = json.dumps({
  "client_id": "ex_client_id",
  "project_id": "ex_project_id",
  "collection_name": "coll_ivf_v4",
  "collection_index_type": "IVF_FLAT",
  "files_path": [
    "uploaded_information_data\\uu_pdp.pdf"
  ],
  "chunk_size": 512,
  "chunk_overlap": 512,
  "separator": "===="
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
