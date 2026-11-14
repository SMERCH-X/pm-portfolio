# ReportFlow

Приём и триаж отчетов. Самостоятельный учебный сервис экосистемы BountyOS.

## Запуск
```bash
python -m venv .venv
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
pytest -q
```
API: http://localhost:8000/docs. Для Docker: `docker build -t report-flow . && docker run -p 8000:8000 report-flow`.

## API
- `GET /health`
- `POST /api/v1/reports`
- `GET /api/v1/reports`
- `GET /api/v1/reports/{id}`
- `GET /api/v1/audit`

## Пример тела запроса
```json
{
  "program_id": "example",
  "asset": "example",
  "title": "example",
  "description": "example",
  "severity": "medium"
}
```

## Product brief
**Проблема:** приём и триаж отчетов.
**Пользователи:** bug bounty program manager, triage analyst, security researcher (в зависимости от роли).
**MVP:** API, локальное хранение, аудит и доменная операция.
**Следующая итерация:** RBAC, PostgreSQL, webhook-подписки, UI, контрактные и интеграционные тесты.
**Ограничения:** демонстрационная реализация, не предназначена для обработки реальных конфиденциальных отчетов.
