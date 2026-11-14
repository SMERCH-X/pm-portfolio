import os
os.environ["DATABASE_PATH"]="/tmp/bounty-score-test.sqlite3"
from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_health():
    assert client.get("/health").status_code==200

def test_create_and_read():
    payload={"report_id": "example", "severity": "high", "asset_criticality": 3, "exploitability": 3}
    response=client.post("/api/v1/assessments",json=payload)
    assert response.status_code==201, response.text
    rid=response.json()["id"]
    assert client.get(f"/api/v1/assessments/{rid}").status_code==200
    assert client.get("/api/v1/audit").json()

def test_not_found():
    assert client.get("/api/v1/assessments/missing").status_code==404
