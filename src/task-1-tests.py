import requests

BASE_URL = "http://127.0.0.1:8000/api/v1/"

names = ["Antonio", "Maria"]

for name in names:
    response = requests.get(BASE_URL, params={"name": name}, headers={"accept": "application/json"})
    print(f"[{response.status_code}] {name} -> {response.json()}")
