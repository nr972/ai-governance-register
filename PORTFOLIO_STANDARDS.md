# Legal Quant Portfolio — Standards & Patterns

**Purpose:** This file captures usability and engineering patterns for all tools in the legal quant portfolio. Reference this file when starting a new project so these standards are built in from the start, not retrofitted.

**How to use:** Include this file (or a reference to it) in the CLAUDE.md of each new project, or paste it into the Claude Code session context at the start of a new build.

---

## Audience

These tools are built for **non-technical legal professionals** — in-house counsel, legal ops teams, paralegals — who:
- May not have Python, Docker, or terminal experience
- May be on managed work computers with restricted install permissions
- Need to "just open a URL" or at most run a single command
- Will not read developer documentation unless they have to

Every design decision should be filtered through: **"Can a lawyer with no engineering background use this in under 2 minutes?"**

---

## Required Files for Every Project

### Startup Scripts
Every tool must include:
- `start.sh` (macOS/Linux) — one-command launch, auto-installs deps on first run, starts all services, opens browser, clean Ctrl+C shutdown
- `start.bat` (Windows) — same behavior adapted for Windows

### Cloud Deployment
Every tool must include:
- `railway.json` — Railway deployment config
- `Dockerfile.railway` — single-container Dockerfile that runs all services (API + frontend) for one-click cloud deploy
- `railway_start.sh` — startup script for the Railway container
- Railway apps should be ready to point a Cloudflare custom domain at them (e.g., `tools.yoursite.com/nda`)

### Docker
- `Dockerfile` — standard container for the API service
- `docker-compose.yml` — single-command launch of all services

### Documentation
- `README.md` — structured for non-technical users first (see README structure below)
- `CLAUDE.md` — project context and coding conventions for AI tooling
- `LICENSE` — MIT
- `PORTFOLIO_STANDARDS.md` — this file (or a reference to it)

### Open-Source Standards
- All sample data must be synthetic — never real company names, client data, or internal policies
- `.gitignore` must exclude: `.env`, `data/real/`, `data/*.db`, `data/generated/`, `__pycache__/`
- Include `data/sample/` with example payloads so people can test immediately

---

## README Structure

The README should be structured in this order, leading with the easiest path:

1. **Title + one-line description**
2. **Getting Started** (three options, in order of ease):
   - **Hosted version** — "Just open this URL" (link to deployed instance)
   - **Run locally** — `./start.sh` or `start.bat` (one command)
   - **Docker** — `docker compose up`
3. **Deploy Your Own** — Railway one-click deploy instructions + manual steps
4. **Features** — what the tool does
5. **For Developers** (below the fold):
   - API documentation
   - Project structure
   - Running tests
   - Tech stack

The non-technical path always comes first. Developer docs are important but secondary.

---

## Tech Stack Consistency

All projects share:
- **Backend:** Python 3.11+, FastAPI
- **Database:** SQLAlchemy ORM with SQLite (prototype) — designed for PostgreSQL migration
- **Frontend:** Streamlit for rapid prototyping
- **Document handling:** docxtpl, python-docx, PyMuPDF/pdfplumber as needed
- **Validation:** Pydantic v2
- **Testing:** pytest
- **Deployment:** Docker + Railway
- **Package management:** pyproject.toml (PEP 621)

---

## Architecture Pattern

**API-first:** FastAPI backend handles all logic. Streamlit is a thin client that calls the API via HTTP. This means:
- The API is independently usable (Swagger docs, curl, integrations)
- The frontend can be swapped to React later without touching business logic
- Multiple frontends can coexist (web, CLI, Slack bot, etc.)

---

## Coding Conventions

- Type hints on all function signatures
- Pydantic for request/response validation
- SQLAlchemy 2.0 style (mapped_column, DeclarativeBase)
- FastAPI dependency injection for DB sessions
- Keep modules small and focused
- Don't over-engineer — minimum complexity for the current task

---

## Dependency Classification for Docker

Dockerfiles install with `pip install .`, which only installs core `[project.dependencies]` — it skips `[project.optional-dependencies]`. This means any package required at runtime must be in core dependencies, not dev extras.

**Core `[project.dependencies]`** — packages the app needs to run:
- `streamlit`, `requests`, `httpx` (if used by the frontend or app at runtime)
- `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`, `anthropic`, `docxtpl`, etc.

**Dev `[project.optional-dependencies]`** — packages only used for testing, linting, and local development:
- `pytest`, `pytest-asyncio`, `httpx` (only if used solely for test clients), `ruff`, etc.

**Rule of thumb:** If the Docker container would crash without it, it's a core dependency.

---

## Lessons Learned (NDA Generator)

1. **Two-terminal problem:** Users don't know they need separate terminals for API and frontend. Startup scripts solve this.
2. **Python not installed:** Many legal professionals don't have Python. Cloud deployment (Railway) and Docker are the answers.
3. **Install permissions:** Work computers often restrict software installation. A hosted URL bypasses this entirely.
4. **README audience mismatch:** Developer-oriented READMEs alienate the target users. Lead with the simplest path.
5. **Template creation:** .docx templates with Jinja2 placeholders should be created programmatically via python-docx to avoid Word's XML run-splitting issue, then verified with a test render.
6. **docxtpl gotcha:** Word sometimes splits `{{ variable }}` across XML runs, silently breaking rendering. Always test templates immediately after creation.
