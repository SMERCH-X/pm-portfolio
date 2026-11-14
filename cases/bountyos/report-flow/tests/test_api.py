import os
os.environ["DATABASE_PATH"]="/tmp/report-flow-test.sqlite3"
from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_health():
    assert client.get("/health").status_code==200

def test_create_and_read():
    payload={"program_id": "example", "asset": "example", "title": "example", "description": "example", "severity": "medium"}
    response=client.post("/api/v1/reports",json=payload)
    assert response.status_code==201, response.text
    rid=response.json()["id"]
    assert client.get(f"/api/v1/reports/{rid}").status_code==200
    assert client.get("/api/v1/audit").json()

def test_not_found():
    assert client.get("/api/v1/reports/missing").status_code==404
