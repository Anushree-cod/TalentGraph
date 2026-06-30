from fastapi import APIRouter
from backend.app.api.endpoints import auth, candidates, jobs, dashboards

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(dashboards.router, prefix="/dashboards", tags=["dashboards"])
