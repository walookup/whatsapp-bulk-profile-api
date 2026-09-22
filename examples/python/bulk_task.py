import os
import time

import requests

api_key = os.environ["WALOOKUP_API_KEY"]
base_url = os.getenv("API_BASE_URL", "https://walookup.com")
product = os.getenv("PRODUCT", "ws_profile_batch")
country = os.getenv("COUNTRY", "US")
path = os.getenv("FILE", "numbers.txt")

with open(path, "rb") as handle:
    created = requests.post(
        f"{base_url}/api/v1/bulk-tasks",
        headers={"X-API-Key": api_key},
        data={"product": product, "country": country},
        files={"file": handle},
        timeout=120,
    )
created.raise_for_status()
task_id = created.json()["data"]["id"]
print("submitted", task_id)

# 轮询间隔不得短于 30 秒，这是服务端的契约而不是建议。
while True:
    time.sleep(30)
    status = requests.get(
        f"{base_url}/api/v1/bulk-tasks/{task_id}", headers={"X-API-Key": api_key}, timeout=60
    )
    status.raise_for_status()
    payload = status.json()["data"]
    print(payload["status"])
    if payload["status"] != "processing":
        print(payload)
        break
