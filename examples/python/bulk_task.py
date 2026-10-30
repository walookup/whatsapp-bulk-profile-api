import os
import time

import requests

api_key = os.environ["WALOOKUP_API_KEY"]
base_url = os.getenv("API_BASE_URL", "https://walookup.com").rstrip("/")
path = os.getenv("FILE", "examples/numbers.txt")
payload = {"service_type": "ws_avatar_batch"}
payload["country"] = os.getenv("COUNTRY", "US")
headers = {"X-API-Key": api_key}
if os.getenv("IDEMPOTENCY_KEY"):
    headers["Idempotency-Key"] = os.environ["IDEMPOTENCY_KEY"]


def read_api(response):
    response.raise_for_status()
    envelope = response.json()
    if envelope.get("code") != 0:
        raise RuntimeError(f"API error: {envelope}")
    return envelope["data"]


with open(path, "rb") as handle:
    created = requests.post(
        f"{base_url}/api/v1/bulk-tasks",
        headers=headers,
        data=payload,  # requests writes service_type/country before the file part.
        files={"file": handle},
        timeout=180,
    )
task_id = read_api(created)["id"]
print("submitted", task_id)

while True:
    time.sleep(30)
    status = read_api(requests.get(
        f"{base_url}/api/v1/bulk-tasks/{task_id}",
        headers={"X-API-Key": api_key}, timeout=60,
    ))
    print(status)
    if status["status"] == "failed":
        raise RuntimeError(f"Task failed: {status.get('reason', '')} {status.get('reason_detail', '')}")
    if status["status"] == "success" and status.get("result_url"):
        break
