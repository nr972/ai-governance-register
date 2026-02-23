import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.database import Base, engine
from api.routers import assessments, classification, dashboard, seed, systems

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AI Governance Register",
    description="AI Compliance & Governance Register — internal AI system registry and governance tracker",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        os.getenv("FRONTEND_URL", "http://localhost:8501"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(systems.router)
app.include_router(classification.router)
app.include_router(assessments.router)
app.include_router(dashboard.router)
app.include_router(seed.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
