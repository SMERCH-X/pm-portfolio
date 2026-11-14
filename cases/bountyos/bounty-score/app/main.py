import os, sqlite3, json, uuid
from datetime import datetime, timezone
from pathlib import Path
from contextlib import contextmanager
from fastapi import FastAPI, HTTPException
from .models import Item

app = FastAPI(title="BountyScore", version="0.1.0", description="Приоритизация рисков и бюджета")
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
    return {"service":"BountyScore", "status":"ok"}

@app.post("/api/v1/assessments", status_code=201)
def create(item: Item):
    rid = str(uuid.uuid4())
    data = item.model_dump()
    data.update(priority(item))
    data.update(id=rid, created_at=datetime.now(timezone.utc).isoformat())
    with connect() as c:
        c.execute("INSERT INTO records VALUES (?,?,?)", (rid,json.dumps(data),data["created_at"]))
        log(c,rid,"created")
    return data

@app.get("/api/v1/assessments")
def list_items():
    with connect() as c:
        return [json.loads(r["payload"]) for r in c.execute("SELECT payload FROM records ORDER BY created_at DESC")]

@app.get("/api/v1/assessments/{rid}")
def get_item(rid: str):
    with connect() as c:
        r = c.execute("SELECT payload FROM records WHERE id=?",(rid,)).fetchone()
    if not r: raise HTTPException(404,"Not found")
    return json.loads(r["payload"])

@app.get("/api/v1/audit")
def audit():
    with connect() as c:
        return [dict(r) for r in c.execute("SELECT * FROM audit ORDER BY created_at DESC")]

SEVERITY={"low":1,"medium":2,"high":3,"critical":4}
@app.post("/api/v1/priority")
def priority(item:Item):
    if item.severity.lower() not in SEVERITY: raise HTTPException(422,"Invalid severity")
    if not 1 <= item.asset_criticality <= 5 or not 1 <= item.exploitability <= 5: raise HTTPException(422,"Factors must be 1..5")
    score=SEVERITY[item.severity.lower()]*5+item.asset_criticality*3+item.exploitability*2
    return {"report_id":item.report_id,"score":score,"tier":"P1" if score>=40 else "P2" if score>=30 else "P3" if score>=20 else "P4","explanation":{"severity":item.severity,"asset_criticality":item.asset_criticality,"exploitability":item.exploitability}}
