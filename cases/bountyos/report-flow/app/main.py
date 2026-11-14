import os, sqlite3, json, uuid
from datetime import datetime, timezone
from pathlib import Path
from contextlib import contextmanager
from fastapi import FastAPI, HTTPException
from .models import Item

app = FastAPI(title="ReportFlow", version="0.1.0", description="Приём и триаж отчетов")
DB = os.environ.get("DATABASE_PATH", "./data/service.sqlite3")

def connect():
    Path(DB).parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB, timeout=15)
    c.row_factory = sqlite3.Row
    c.execute("CREATE TABLE IF NOT EXISTS records (id TEXT PRIMARY KEY, payload TEXT NOT NULL, created_at TEXT NOT NULL)")
    c.execute("CREATE TABLE IF NOT EXISTS audit (id TEXT PRIMARY KEY, record_id TEXT, action TEXT, created_at TEXT)")
    c.commit()
    return c

def log(c, record_id, action):
    c.execute("INSERT INTO audit VALUES (?,?,?,?)", (str(uuid.uuid4()),record_id,action,datetime.now(timezone.utc).isoformat()))

@app.get("/health")
def health():
    return {"service":"ReportFlow", "status":"ok"}

@app.post("/api/v1/reports", status_code=201)
def create(item: Item):
    rid = str(uuid.uuid4())
    data = item.model_dump()
    data.update(id=rid, created_at=datetime.now(timezone.utc).isoformat())
    with connect() as c:
        c.execute("INSERT INTO records VALUES (?,?,?)", (rid,json.dumps(data),data["created_at"]))
        log(c,rid,"created")
    return data

@app.get("/api/v1/reports")
def list_items():
    with connect() as c:
        return [json.loads(r["payload"]) for r in c.execute("SELECT payload FROM records ORDER BY created_at DESC")]

@app.get("/api/v1/reports/{rid}")
def get_item(rid: str):
    with connect() as c:
        r = c.execute("SELECT payload FROM records WHERE id=?",(rid,)).fetchone()
    if not r: raise HTTPException(404,"Not found")
    return json.loads(r["payload"])

@app.get("/api/v1/audit")
def audit():
    with connect() as c:
        return [dict(r) for r in c.execute("SELECT * FROM audit ORDER BY created_at DESC")]

from .models import StatusChange
@app.patch("/api/v1/reports/{rid}/status")
def change_status(rid:str, change:StatusChange):
    record=get_item(rid)
    record.update(status=change.status,assignee=change.assignee,updated_at=datetime.now(timezone.utc).isoformat())
    with connect() as c:
        c.execute("UPDATE records SET payload=? WHERE id=?",(json.dumps(record),rid))
        log(c,rid,"status:"+change.status)
    return record
