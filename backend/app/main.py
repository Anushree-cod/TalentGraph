from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.api_router import api_router
from backend.app.db.session import Base, engine
from backend.app.db import models  # noqa: F401
from backend.app.db.migrate import run_migrations

app = FastAPI(
    title="TalentGraph API",
    description="Backend API for TalentGraph",
    version="1.0.0",
)

# CORS setup for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    run_migrations()

@app.get("/")
def read_root():
    return {"message": "Welcome to TalentGraph API"}
