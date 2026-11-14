# Product management pack

## Vision
BountyOS помогает операторам авторизованных Bug Bounty-программ управлять scope, жизненным циклом отчетов, повторами, приоритетами и измеримыми результатами.

## Персоны
- Program owner: управляет активами, правилами и бюджетом.
- Triage analyst: проверяет качество, дубликаты и приоритеты.
- Researcher: отправляет отчет и отслеживает статус.
- Engineering lead: получает принятые проблемы и отвечает за remediation.

## North-star metric
Количество качественных, принятых и устраненных уязвимостей за квартал (не число всех отправок).

## KPI
Median time to first response; median time to triage; median time to remediation; duplicate review precision; accepted report rate; cost per valid finding; scope violations. Измерения пока не проведены.

## Roadmap
**R0 (готово в starter):** 5 API, CRUD, базовые доменные операции, аудит, Docker, unit/API smoke tests.
**R1:** Postgres, schema migrations, RBAC, auth, validation, API contracts.
**R2:** webhook event bus, интеграционные тесты, end-to-end demo, UI.
**R3:** SLA analytics, quality benchmarks, monitoring, CI/CD, security review.

## Prioritization (RICE — гипотезы, не факты)
| Feature | Reach | Impact | Confidence | Effort | RICE |
|---|---:|---:|---:|---:|---:|
| Auth + RBAC | 100 | 3 | 0.9 | 8 | 33.75 |
| Report lifecycle | 80 | 3 | 0.9 | 5 | 43.2 |
| Scope validation | 60 | 2 | 0.7 | 4 | 21 |
| Duplicate recommendations | 50 | 2 | 0.6 | 6 | 10 |
| KPI dashboard | 70 | 2 | 0.8 | 5 | 22.4 |

## Delivery / Project management
**Sprint 1:** OpenAPI contract, schema, backlog, Definition of Done.
**Sprint 2:** event integration, test fixtures, audit.
**Sprint 3:** frontend, UX tests, analytics and demo.
**Definition of Done:** tests pass, OpenAPI updated, security review completed, acceptance criteria documented, changelog entry added.

## Risks
Unauthorized access to sensitive reports (high); incorrect duplicate suggestions (medium); false sense of SLA compliance from incomplete events (high); scope ambiguity (high). Mitigate with RBAC, encryption, human review, event contracts and explicit scope policies.
