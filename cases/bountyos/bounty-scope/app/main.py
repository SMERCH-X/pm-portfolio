import os, sqlite3, json, uuid
from datetime import datetime, timezone
from pathlib import Path
from contextlib import contextmanager
from fastapi import FastAPI, HTTPException
from .models import Item

app = FastAPI(title="BountyScope", version="0.1.0", description="Управление программами и правилами")
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
    return {"service":"BountyScope", "status":"ok"}

@app.post("/api/v1/programs", status_code=201)
def create(item: Item):
    rid = str(uuid.uuid4())
    data = item.model_dump()
    data.update(id=rid, created_at=datetime.now(timezone.utc).isoformat())
    with connect() as c:
        c.execute("INSERT INTO records VALUES (?,?,?)", (rid,json.dumps(data),data["created_at"]))
        log(c,rid,"created")
    return data

@app.get("/api/v1/programs")
def list_items():
    with connect() as c:
        return [json.loads(r["payload"]) for r in c.execute("SELECT payload FROM records ORDER BY created_at DESC")]

@app.get("/api/v1/programs/{rid}")
def get_item(rid: str):
    with connect() as c:
        r = c.execute("SELECT payload FROM records WHERE id=?",(rid,)).fetchone()
    if not r: raise HTTPException(404,"Not found")
    return json.loads(r["payload"])

@app.get("/api/v1/audit")
def audit():
    with connect() as c:
        return [dict(r) for r in c.execute("SELECT * FROM audit ORDER BY created_at DESC")]

from .models import Asset
@app.post("/api/v1/assets",status_code=201)
def add_asset(asset: Asset):
    get_item(asset.program_id)
    with connect() as c:
        c.execute("CREATE TABLE IF NOT EXISTS assets (id TEXT PRIMARY KEY, program_id TEXT, target TEXT, in_scope INTEGER, notes TEXT)")
        aid=str(uuid.uuid4())
        c.execute("INSERT INTO assets VALUES (?,?,?,?,?)",(aid,asset.program_id,asset.target,int(asset.in_scope),asset.notes))
        log(c,asset.program_id,"asset_added")
    return {"id":aid,**asset.model_dump()}
@app.get("/api/v1/assets/{program_id}")
def assets(program_id:str):
    with connect() as c:
        c.execute("CREATE TABLE IF NOT EXISTS assets (id TEXT PRIMARY KEY, program_id TEXT, target TEXT, in_scope INTEGER, notes TEXT)")
        return [dict(r) for r in c.execute("SELECT * FROM assets WHERE program_id=?",(program_id,))]
