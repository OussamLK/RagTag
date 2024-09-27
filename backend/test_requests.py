import requests
import base64

def post(url, payload):
    
    domain = 'http://127.0.0.1:5000'
    resp = requests.post(f"{domain}{url}", json=payload)
    return resp.json()

def post_file(path):
    with open(path, "rb") as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes).decode()
        return post('/upload', {"fileName":path, "fileB64":b64})

from pprint import pprint
query = "Dois-je vraiment utiliser une formule de politesse?"
best_match = post("/query", {"query": "Comment bien ecrire une lettre", "taskId":"68643a71-2e07-4887-aa51-98b535412703"})['matches'][0]
print(best_match['sentence'])