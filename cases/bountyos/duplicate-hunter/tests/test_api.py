import os
os.environ["DATABASE_PATH"]="/tmp/duplicate-hunter-test.sqlite3"
from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_health():
    assert client.get("/health").status_code==200

def test_create_and_read():
    payload={"report_id": "example", "candidate_id": "example", "text_a": "example", "text_b": "example"}
    response=client.post("/api/v1/comparisons",json=payload)
    assert response.status_code==201, response.text
    rid=response.json()["id"]
    assert client.get(f"/api/v1/comparisons/{rid}").status_code==200
    assert client.get("/api/v1/audit").json()

def test_not_found():
    assert client.get("/api/v1/comparisons/missing").status_code==404
