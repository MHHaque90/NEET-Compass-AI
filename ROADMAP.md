# Roadmap

> **Phase 1 status:** Complete — database architecture locked (Sprint 2)

## Vision

Build the world's first fully open-source, self-hostable, AI-powered,
Explainable Admission Intelligence Platform for NEET Counselling.

## Phases

| Phase | Status | Goal | Deliverables |
|-------|--------|------|--------------|
| Sprint 0 | ✅ Done | Project scaffold | Repo, tooling, Docker, CI |
| Sprint 1 | ✅ Done | Core domain model | Clean architecture, 4-table DB, ETL framework, feature flags |
| Sprint 1.1 | ✅ Done | Feature flag introspection | DB-backed flags, introspection API |
| Sprint 1.2 | ✅ Done | ETL enhancement | Data seeding, column mapping, validation |
| Sprint 2 | ✅ Done | Production database | 22-table schema, versioning, full documentation |
| Sprint 3 | 🔲 Planned | REST API + Auth | FastAPI routes, JWT auth, CORS, OpenAPI |
| Sprint 4 | 🔲 Planned | Prediction engine | Rule-based, ML models, A/B testing |
| Sprint 5 | 🔲 Planned | Data pipeline | Scrapers, PDF parsing, automated ETL |
| Sprint 6 | 🔲 Planned | Frontend | Choice-filling UI, dashboard, PWA |
| Sprint 7 | 🔲 Planned | Analytics | Monitoring, reporting, dashboards |
| Sprint 8 | 🔲 Planned | Advanced features | Multi-language, ML model registry |

## Sprint 2+ Scope

### Sprint 3: REST API and Authentication
- FastAPI routes for all 22 tables
- JWT-based authentication system
- Authorization and roles (candidate, admin, superuser)
- CORS configuration for frontend clients
- API request/response validation with Pydantic schemas
- API versioning (v1, v2)
- Rate limiting and request throttling
- OpenAPI documentation

### Sprint 4: Prediction Engine
- Rule-based recommendation engine (closing rank analysis)
- Statistical/ML prediction models behind the port
- Feature engineering pipeline
- A/B testing infrastructure for model versions
- Prediction explainability (SHAP/LIME integration)
- Batch prediction support
- Real-time prediction API

### Sprint 5: Data Pipeline and Scrapers
- MCC official data source scraper (HTML/PDF)
- State counselling website scrapers
- PDF parsing for cut-off data (PyPDF2, pdfplumber)
- Automated ETL with quality monitoring
- Data drift detection
- Incremental ETL based on file modification dates
- Data quality dashboards
- Alerting system for ETL failures

### Sprint 6: Frontend Development
- Choice-filling UI for candidates
- College comparison dashboard
- Historical cut-off visualization
- Probability distribution charts
- Mobile-responsive design
- Progressive Web App (PWA) support
- Dark/light mode
- Multi-step counselling strategy wizard

### Sprint 7: Analytics and Monitoring
- Database partitioning for allotments and logs (Phase 3 hardening)
- Performance monitoring (query analysis, slow query log)
- Data quality dashboards
- Model performance monitoring
- Alerting system for ETL failures
- Usage analytics
- Audit log viewer
- Admin dashboard for system health

### Sprint 8: Advanced Features
- Multi-language support (i18n)
- Email/SMS notifications
- Community feature flags
- Data import/export APIs
- Offline mode for frontend
- Mobile app (React Native)
- Third-party integrations
- White-label deployment support

## Post-Lock Items (Architecture is LOCKED)

Per the Sprint 2 lock:

| Aspect | Status | Change Process |
|--------|--------|---------------|
| Database Architecture | 🔒 Locked | Requires ADR review |
| Folder Structure | 🔒 Locked | Requires ADR review |
| Documentation Standards | 🔒 Locked | Requires ADR review |

**Note:** Adding new tables, modifying column types, or creating new
layers requires an ADR and architecture committee review.

## Milestone Timeline

```
2026-08-08  Sprint 0   ✓  Project scaffold
2026-08-08  Sprint 1   ✓  Core domain model
2026-08-09  Sprint 1.1 ✓  Feature flag introspection
2026-08-09  Sprint 1.2 ✓  ETL enhancement
2026-08-10  Sprint 2   ✓  Production database architecture (LOCKED)
                    ────────────────────────────────────────────────
2026-08-17  Sprint 3   🔲 REST API + Auth
2026-08-24  Sprint 4   🔲 Prediction engine
2026-08-31  Sprint 5   🔲 Data pipeline + scrapers
2026-09-07  Sprint 6   🔲 Frontend (Phase 1)
2026-09-14  Sprint 7   🔲 Analytics + monitoring
2026-09-21  Sprint 8   🔲 Advanced features
```

Timeline assumes weekly sprints with 1-2 developers per sprint.

## Backlog Policy

All work items follow the backlog policy in
[PROJECT_CONSTITUTION.md](PROJECT_CONSTITUTION.md):

1. **Product backlog** is prioritized by impact × effort
2. **Technical debt** is addressed in every sprint (min 10% capacity)
3. **Architecture debt** requires ADR before implementation
4. **Sprint backlog** is committed on Monday, reviewed on Friday
5. **Items exceeding 3 days** must be broken down before sprint planning

## Improvement Policy

Continuous improvement is built into every sprint:
- **Retrospective** — Every Friday, 30 minutes
- **Architecture health review** — Updated each sprint in `ARCHITECTURE_HEALTH.md`
- **Tech debt tracking** — Logged in sprint reports, prioritized monthly
- **Metrics-driven** — Coverage, lint, mypy, and architecture debt tracked

## Releases

| Version | Date | Sprint | Notes |
|---------|------|--------|-------|
| v0.0.0 | 2026-08-08 | Sprint 0 | Project scaffold |
| v0.1.0 | 2026-08-08 | Sprint 1 | Core domain model |
| v0.1.1 | 2026-08-09 | Sprint 1.1 | Feature flag introspection |
| v0.1.2 | 2026-08-09 | Sprint 1.2 | ETL enhancement |
| v0.2.0 | 2026-08-10 | Sprint 2 | Production database (LOCKED) |
| v0.3.0 | TBD | Sprint 3 | REST API + Auth |
| v0.4.0 | TBD | Sprint 4 | Prediction engine |
| v0.5.0 | TBD | Sprint 5 | Data pipeline + scrapers |
| v0.6.0 | TBD | Sprint 6 | Frontend MVP |
| v1.0.0 | TBD | Sprint 8 | Production-ready platform |

## License

MIT — see [LICENSE](LICENSE) for details.
