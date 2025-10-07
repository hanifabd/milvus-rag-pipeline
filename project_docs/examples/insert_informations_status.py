import requests

task_id = "f7cd9008-6f1f-4496-a6f2-c75f26919458"
url = f"http://127.0.0.1:2024/insert/status/{task_id}"

payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
