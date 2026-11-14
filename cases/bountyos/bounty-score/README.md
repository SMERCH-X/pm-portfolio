# BountyScore

Приоритизация рисков и бюджета. Самостоятельный учебный сервис экосистемы BountyOS.

## Запуск
```bash
python -m venv .venv
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
pytest -q
```
API: http://localhost:8000/docs. Для Docker: `docker build -t bounty-score . && docker run -p 8000:8000 bounty-score`.

## API
- `GET /health`
- `POST /api/v1/assessments`
- `GET /api/v1/assessments`
- `GET /api/v1/assessments/{id}`
- `GET /api/v1/audit`

## Пример тела запроса
```json
{
  "report_id": "example",
  "severity": "high",
  "asset_criticality": 3,
  "exploitability": 3
}
```

## Product brief
**Проблема:** приоритизация рисков и бюджета.
**Пользователи:** bug bounty program manager, triage analyst, security researcher (в зависимости от роли).
**MVP:** API, локальное хранение, аудит и доменная операция.
**Следующая итерация:** RBAC, PostgreSQL, webhook-подписки, UI, контрактные и интеграционные тесты.
**Ограничения:** демонстрационная реализация, не предназначена для обработки реальных конфиденциальных отчетов.
