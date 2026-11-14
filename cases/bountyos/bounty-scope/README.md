# BountyScope

Управление программами и правилами. Самостоятельный учебный сервис экосистемы BountyOS.

## Запуск
```bash
python -m venv .venv
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
pytest -q
```
API: http://localhost:8000/docs. Для Docker: `docker build -t bounty-scope . && docker run -p 8000:8000 bounty-scope`.

## API
- `GET /health`
- `POST /api/v1/programs`
- `GET /api/v1/programs`
- `GET /api/v1/programs/{id}`
- `GET /api/v1/audit`

## Пример тела запроса
```json
{
  "name": "example",
  "policy": "example",
  "reward_budget": 10000.0
}
```

## Product brief
**Проблема:** управление программами и правилами.
**Пользователи:** bug bounty program manager, triage analyst, security researcher (в зависимости от роли).
**MVP:** API, локальное хранение, аудит и доменная операция.
**Следующая итерация:** RBAC, PostgreSQL, webhook-подписки, UI, контрактные и интеграционные тесты.
**Ограничения:** демонстрационная реализация, не предназначена для обработки реальных конфиденциальных отчетов.
