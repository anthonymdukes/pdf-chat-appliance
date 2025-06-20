import requests

URL = "http://localhost:5000/query"

payload = {"question": "What is this document about?"}
response = requests.post(URL, json=payload, timeout=10)
print("Status:", response.status_code)
print(response.json())
