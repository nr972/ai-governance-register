# AI Governance Register

Internal AI system registry and governance tracker. Register AI systems your organization develops, deploys, or procures — with automated risk classification under the EU AI Act, impact assessments, and a governance dashboard.

## Getting Started

### Option 1: Hosted Version
> Coming soon — a hosted instance will be available at a public URL.

### Option 2: Run Locally (one command)

**macOS / Linux:**
```bash
./start.sh
```

**Windows:**
```
start.bat
```

This installs dependencies, starts the API and frontend, and opens your browser. No setup required beyond Python 3.11+.

### Option 3: Docker
```bash
docker compose up
```

Then open [http://localhost:8501](http://localhost:8501).

## Deploy Your Own

### Railway (one-click cloud deploy)

1. Fork this repo
2. Connect it to [Railway](https://railway.app)
3. Railway auto-detects `railway.json` and builds from `Dockerfile.railway`
4. Set environment variables in Railway dashboard:
   - `ANTHROPIC_API_KEY` (optional — enables AI-assisted classification)

## Features

- **AI System Registry** — Register and manage AI systems with structured fields aligned to the EU AI Act and NIST AI RMF
- **Automated Risk Classification** — Rule-based classification mapped to EU AI Act Annex III categories, plus optional AI-assisted classification via Claude
- **Impact Assessments** — Template-generated assessments that vary by risk tier, with fill-out workflow, status tracking, and PDF/DOCX export
- **Version History** — Full audit trail of changes to every AI system record
- **Governance Dashboard** — Portfolio risk distribution, assessment completion rates, upcoming review dates, and recent activity

### Risk Classification

The tool classifies AI systems into four EU AI Act risk tiers:

| Tier | Examples | Obligations |
|------|----------|-------------|
| **Unacceptable** | Social scoring, subliminal manipulation | Prohibited |
| **High** | Biometric ID, employment screening, critical infrastructure | Conformity assessment, ongoing monitoring |
| **Limited** | Chatbots, emotion recognition, deepfakes | Transparency obligations |
| **Minimal** | Content recommendation, general-purpose tools | Voluntary codes of conduct |

**Rule-based:** Select a use case category; the system maps it to a risk tier using EU AI Act Annex III.

**AI-assisted:** Provide a free-text description; Claude suggests a classification with reasoning and confidence. Requires an `ANTHROPIC_API_KEY`.

## For Developers

### API Documentation

With the API running, visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive Swagger documentation.

### Project Structure

```
ai-governance-register/
├── api/                        # FastAPI backend
│   ├── main.py                 # App entry, CORS, router registration
│   ├── database.py             # SQLAlchemy engine and session
│   ├── models.py               # ORM models (AISystem, ImpactAssessment, AuditLog)
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── routers/                # API route modules
│   │   ├── systems.py          # AI system CRUD
│   │   ├── classification.py   # Risk classification endpoints
│   │   ├── assessments.py      # Impact assessment CRUD + export
│   │   ├── dashboard.py        # Dashboard aggregation endpoints
│   │   └── seed.py             # Sample data loader
│   └── services/               # Business logic
│       ├── risk_classifier.py  # EU AI Act rule-based classification
│       ├── llm_classifier.py   # Claude API classification
│       ├── assessment.py       # Assessment template generation
│       ├── export.py           # PDF and DOCX export
│       └── audit.py            # Version history / audit logging
├── agr_frontend/               # Streamlit frontend
│   ├── app.py                  # Main entry point
│   ├── pages/                  # Multipage app pages
│   └── utils/                  # API client, constants
├── data/sample/                # Synthetic seed data
├── tests/                      # pytest test suite
├── start.sh / start.bat        # One-command launchers
├── Dockerfile                  # API container
├── docker-compose.yml          # Multi-service compose
├── Dockerfile.railway          # Railway deployment
└── pyproject.toml              # Dependencies (PEP 621)
```

### Running Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

### Tech Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2
- **Frontend:** Streamlit, Plotly
- **Database:** SQLite (prototype), PostgreSQL-ready
- **LLM:** Anthropic Claude API (optional)
- **Export:** ReportLab (PDF), python-docx (DOCX)
- **Testing:** pytest
- **Deployment:** Docker, Railway

### Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `DATABASE_URL` | No | `sqlite:///./data/governance.db` | Database connection |
| `ANTHROPIC_API_KEY` | No | — | AI-assisted classification |
| `FRONTEND_URL` | No | `http://localhost:8501` | CORS origin |
| `API_URL` | No | `http://localhost:8000` | Frontend → API URL |

## License

MIT
