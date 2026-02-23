# CLAUDE.md — AI Compliance & Governance Register

## Project Summary

Internal AI system registry and governance tracker. Captures AI systems an organization develops, deploys, or procures — with risk classification (EU AI Act, NIST AI RMF), impact assessments, and a governance dashboard.

Part of the Legal Quant portfolio. See `PORTFOLIO_STANDARDS.md` for cross-project conventions.

## Architecture

**API-first pattern:** FastAPI backend handles all business logic. Streamlit is a thin frontend that calls the API via HTTP.

```
streamlit (port 8501) → FastAPI (port 8000) → SQLite/PostgreSQL
```

- Backend: Python 3.11+, FastAPI
- Frontend: Streamlit
- Database: SQLAlchemy 2.0 ORM with SQLite (prototype), designed for PostgreSQL migration
- Validation: Pydantic v2
- Testing: pytest
- Deployment: Docker + Railway

## Project Structure

```
ai-governance-register/
├── api/                    # FastAPI backend
│   ├── main.py             # App entry point, CORS, routers
│   ├── models.py           # SQLAlchemy ORM models
│   ├── schemas.py          # Pydantic request/response schemas
│   ├── database.py         # DB engine, session, Base
│   ├── routers/            # Route modules
│   │   ├── systems.py      # AI system CRUD
│   │   ├── assessments.py  # Impact assessments
│   │   ├── dashboard.py    # Dashboard/analytics endpoints
│   │   └── classification.py  # Risk classification logic
│   └── services/           # Business logic
│       ├── risk_classifier.py  # EU AI Act + NIST classification
│       └── assessment.py       # Impact assessment generation
├── frontend/               # Streamlit app
│   ├── app.py              # Main Streamlit entry point
│   └── pages/              # Streamlit multipage app
├── data/
│   └── sample/             # Synthetic example data
├── tests/                  # pytest tests
├── start.sh                # One-command launch (macOS/Linux)
├── start.bat               # One-command launch (Windows)
├── Dockerfile
├── docker-compose.yml
├── Dockerfile.railway
├── railway.json
├── railway_start.sh
├── pyproject.toml
├── CLAUDE.md
├── README.md
├── PORTFOLIO_STANDARDS.md
└── LICENSE
```

## Coding Conventions

- Type hints on all function signatures
- Pydantic v2 for all request/response validation
- SQLAlchemy 2.0 style: `DeclarativeBase`, `mapped_column`, `Mapped[]`
- FastAPI dependency injection for DB sessions (`Depends(get_db)`)
- Keep modules small and focused
- Don't over-engineer — minimum complexity for the current task
- Input validation and sanitization at API boundaries
- No raw SQL — use SQLAlchemy ORM exclusively

## Security Considerations

- Validate and sanitize all user inputs via Pydantic schemas
- Use parameterized queries (SQLAlchemy ORM) — never raw SQL string interpolation
- CORS configuration: restrict origins in production
- No secrets in code or sample data — use environment variables
- `.env` files excluded via `.gitignore`
- Sample data must be fully synthetic — no real company names, systems, or internal data
- Rate limiting on API endpoints in production
- Audit logging for changes to AI system records

## Key Domain Concepts

- **EU AI Act risk tiers:** Unacceptable, High, Limited, Minimal
- **NIST AI RMF:** Govern, Map, Measure, Manage functions
- **Impact assessment:** Structured evaluation of an AI system's risks, mitigations, and governance controls
- **Human oversight mechanisms:** Controls ensuring humans can monitor, intervene in, or override AI system decisions
- **Bias testing:** Evaluation of AI system outputs for discriminatory patterns

## Deployment

Three-tier access (in order of ease):
1. **Hosted:** Railway deployment — just open a URL
2. **Local:** `./start.sh` (macOS/Linux) or `start.bat` (Windows)
3. **Docker:** `docker compose up`

Startup scripts must: auto-install deps, start API + frontend, open browser, handle Ctrl+C cleanup.

## Testing

```bash
pytest tests/ -v
```

Write tests for:
- API endpoint behavior (CRUD, validation, error cases)
- Risk classification logic (all tiers, edge cases)
- Impact assessment generation
- Dashboard aggregation queries

## Common Commands

```bash
# Start API only
uvicorn api.main:app --reload --port 8000

# Start frontend only
streamlit run frontend/app.py --server.port 8501

# Run tests
pytest tests/ -v

# Both services (use start.sh in practice)
./start.sh
```
