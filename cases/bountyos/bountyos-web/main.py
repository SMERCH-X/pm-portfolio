from pathlib import Path
import os
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response

app = FastAPI(title="BountyOS Gateway", version="0.4.0")
SERVICES = {"scope": 8101, "reports": 8102, "duplicates": 8103, "score": 8104, "pulse": 8105}
SERVICES = {name: port + int(os.getenv("BOUNTYOS_PORT_OFFSET", "0")) for name, port in SERVICES.items()}
BASE = Path(__file__).resolve().parent

@app.get("/")
def index():
    return FileResponse(BASE / "index.html")

@app.get("/api/status")
async def status():
    async with httpx.AsyncClient(timeout=2) as client:
        result = {}
        for name, port in SERVICES.items():
            try:
                r = await client.get(f"http://127.0.0.1:{port}/health")
                result[name] = r.status_code == 200
            except httpx.HTTPError:
                result[name] = False
        return result

# v0.3: synchronous, explicitly non-transactional demonstration workflow.
from pydantic import BaseModel, Field
from typing import Literal

class Submission(BaseModel):
    program_id: str = Field(min_length=1)
    asset: str = Field(min_length=1)
    title: str = Field(min_length=3)
    description: str = Field(min_length=5)
    severity: Literal['low', 'medium', 'high', 'critical']
    asset_criticality: int = Field(default=3, ge=1, le=5)
    exploitability: int = Field(default=3, ge=1, le=5)

async def call_service(service, method, path, payload=None):
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.request(method, f'http://127.0.0.1:{SERVICES[service]}{path}', json=payload)
        except httpx.RequestError:
            raise HTTPException(503, f'{service} недоступен')
    if r.status_code >= 400:
        raise HTTPException(r.status_code, {'service':service, 'message':r.text[:350]})
    return r.json()

@app.post('/api/workflow/submit', status_code=201)
async def submit_report(item: Submission):
    # Validate the program and an explicitly allowed asset before any writes.
    await call_service('scope', 'GET', f'/api/v1/programs/{item.program_id}')
    assets = await call_service('scope', 'GET', f'/api/v1/assets/{item.program_id}')
    if not any(a['target'].strip().lower() == item.asset.strip().lower() and a['in_scope'] for a in assets):
        raise HTTPException(422, 'Актив не добавлен в разрешённый scope программы')
    existing = await call_service('reports', 'GET', '/api/v1/reports')
    # Save report first; later steps can fail. Return a visible partial result.
    report = await call_service('reports', 'POST', '/api/v1/reports', item.model_dump(include={'program_id','asset','title','description','severity'}))
    result = {'report':report, 'duplicate_candidates':[], 'priority':None, 'event':None, 'warnings':[]}
    for previous in existing:
        if previous.get('program_id') != item.program_id or previous.get('asset','').lower() != item.asset.lower():
            continue
        comparison = {'report_id':report['id'], 'candidate_id':previous['id'], 'text_a':item.title+' '+item.description, 'text_b':previous.get('title','')+' '+previous.get('description','')}
        try:
            sim = await call_service('duplicates','POST','/api/v1/similarity',comparison)
            if sim['similarity'] >= .5:
                await call_service('duplicates','POST','/api/v1/comparisons',comparison)
                result['duplicate_candidates'].append({'report_id':previous['id'],'similarity':sim['similarity'],'requires_human_review':True})
        except HTTPException as exc:
            result['warnings'].append(f'Проверка дубликатов не завершена: {exc.detail}')
            break
    assessment = {'report_id':report['id'],'severity':item.severity,'asset_criticality':item.asset_criticality,'exploitability':item.exploitability}
    try:
        result['priority'] = await call_service('score','POST','/api/v1/priority',assessment)
        result['priority'] = await call_service('score','POST','/api/v1/assessments',assessment)
    except HTTPException as exc:
        result['warnings'].append(f'Оценка риска не завершена: {exc.detail}')
    try:
        result['event'] = await call_service('pulse','POST','/api/v1/events',{'report_id':report['id'],'event_type':'report_created','program_id':item.program_id})
    except HTTPException as exc:
        result['warnings'].append(f'Событие аналитики не записано: {exc.detail}')
    return result

@app.get('/api/workflow/report-status/{report_id}')
async def workflow_status(report_id: str):
    report = await call_service('reports','GET',f'/api/v1/reports/{report_id}')
    scores = await call_service('score','GET','/api/v1/assessments')
    events = await call_service('pulse','GET','/api/v1/events')
    return {'report':report,'assessments':[s for s in scores if s.get('report_id')==report_id], 'events':[e for e in events if e.get('report_id')==report_id]}

@app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PATCH", "PUT", "DELETE"])
async def proxy(service: str, path: str, request: Request):
    if service not in SERVICES:
        raise HTTPException(404, "Unknown service")
    url = f"http://127.0.0.1:{SERVICES[service]}/{path}"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.request(request.method, url, params=request.query_params,
                content=await request.body(), headers={"content-type": request.headers.get("content-type", "application/json")})
        return Response(content=response.content, status_code=response.status_code,
                        media_type=response.headers.get("content-type", "application/json"))
    except httpx.HTTPError:
        raise HTTPException(503, f"Service {service} unavailable")

