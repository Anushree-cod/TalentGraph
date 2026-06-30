"""
FastAPI Application — main entry point for the GitHub Profile Analyzer.

Routes:
  POST /api/analyze     — Full analysis: GitHub URL + optional JD
  GET  /api/profile/{u} — Fetch raw GitHub profile data
  POST /api/match       — Match existing profile against a JD
  GET  /dashboard       — Minimal HTML dashboard for testing
  GET  /health          — Health check
"""

import time
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.models.schemas import (
    AnalyzeRequest,
    MatchRequest,
    ProfileAnalysis,
    ContributionData,
    Visualizations,
)
from app.services.github_fetcher import GitHubFetcher
from app.services.data_processor import DataProcessor
from app.services.ai_analyzer import AIAnalyzer
from app.services.visualizer import Visualizer

# ─── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ─── App Setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="GitHub Profile Analyzer",
    description="AI-powered GitHub profile analysis for recruiting",
    version="1.0.0",
)

# Static files and templates
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Service instances
fetcher = GitHubFetcher()
processor = DataProcessor()
analyzer = AIAnalyzer()
visualizer = Visualizer()

# ─── CORS (allow all for development) ────────────────────────────────────────

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════════════════
# API Routes
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "github_authenticated": settings.is_authenticated,
        "gemini_available": settings.has_gemini,
    }


@app.post("/api/analyze", response_model=ProfileAnalysis)
async def analyze_profile(request: AnalyzeRequest):
    """
    Main analysis endpoint.
    Fetches GitHub data, processes it, generates visualizations,
    and optionally matches against a job description.
    """
    start_time = time.time()
    username = request.get_username()

    logger.info(f"Starting analysis for: {username}")

    # ── Step 1: Fetch GitHub data ─────────────────────────────────────
    try:
        raw_data = await fetcher.fetch_all(username)
    except Exception as e:
        logger.error(f"Failed to fetch GitHub data: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch data from GitHub: {str(e)}",
        )

    if not raw_data.get("profile"):
        raise HTTPException(
            status_code=404,
            detail=f"GitHub user '{username}' not found or profile is inaccessible",
        )

    profile = raw_data["profile"]
    repos = raw_data["repositories"]

    # ── Step 2: Process data ──────────────────────────────────────────
    contributions = raw_data.get("contributions")
    if not contributions:
        contributions = ContributionData()

    language_stats = processor.process_languages(repos)
    scores = processor.calculate_scores(
        profile, repos, contributions, language_stats
    )
    extracted_skills = processor.extract_skills(repos, language_stats)

    logger.info(
        f"Processed: {len(repos)} repos, {len(language_stats)} languages, "
        f"{len(extracted_skills)} skills extracted"
    )

    # ── Step 3: AI Analysis (if JD provided) ──────────────────────────
    ai_analysis = None
    if request.job_description:
        logger.info("Running AI analysis against job description...")
        ai_analysis = await analyzer.analyze(
            job_description=request.job_description,
            profile=profile,
            repos=repos,
            language_stats=language_stats,
            contributions=contributions,
            scores=scores,
            extracted_skills=extracted_skills,
        )
        logger.info(
            f"AI analysis complete: {ai_analysis.match_percentage}% match "
            f"({ai_analysis.analysis_method})"
        )

    # ── Step 4: Generate visualizations ───────────────────────────────
    skill_matches = ai_analysis.matching_skills if ai_analysis else None
    visualizations = visualizer.generate_all(
        language_stats=language_stats,
        repos=repos,
        contributions=contributions,
        skill_matches=skill_matches,
    )

    # ── Step 5: Build response ────────────────────────────────────────
    total_time = round(time.time() - start_time, 2)
    metadata = {
        **raw_data.get("metadata", {}),
        "total_analysis_time_seconds": total_time,
        "skills_count": len(extracted_skills),
        "languages_count": len(language_stats),
    }

    result = ProfileAnalysis(
        profile=profile,
        repositories=repos,
        language_stats=language_stats,
        contributions=contributions,
        scores=scores,
        extracted_skills=extracted_skills,
        ai_analysis=ai_analysis,
        visualizations=visualizations,
        metadata=metadata,
    )

    logger.info(f"Analysis complete for {username} in {total_time}s")
    return result


@app.get("/api/profile/{username}")
async def get_profile(username: str):
    """Fetch raw GitHub profile data only (no analysis)."""
    try:
        raw_data = await fetcher.fetch_all(username)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch data from GitHub: {str(e)}",
        )

    if not raw_data.get("profile"):
        raise HTTPException(
            status_code=404,
            detail=f"GitHub user '{username}' not found",
        )

    # Basic processing
    repos = raw_data["repositories"]
    language_stats = processor.process_languages(repos)
    extracted_skills = processor.extract_skills(repos, language_stats)

    return {
        "profile": raw_data["profile"],
        "repositories_count": len(repos),
        "language_stats": language_stats,
        "extracted_skills": extracted_skills,
        "metadata": raw_data.get("metadata", {}),
    }


@app.post("/api/match")
async def match_profile(request: MatchRequest):
    """Match an already-fetched profile against a new job description."""
    # Fetch the profile first
    try:
        raw_data = await fetcher.fetch_all(request.username)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch data from GitHub: {str(e)}",
        )

    if not raw_data.get("profile"):
        raise HTTPException(
            status_code=404,
            detail=f"GitHub user '{request.username}' not found",
        )

    profile = raw_data["profile"]
    repos = raw_data["repositories"]
    contributions = raw_data.get("contributions") or ContributionData()
    language_stats = processor.process_languages(repos)
    scores = processor.calculate_scores(
        profile, repos, contributions, language_stats
    )
    extracted_skills = processor.extract_skills(repos, language_stats)

    # Run AI analysis
    ai_analysis = await analyzer.analyze(
        job_description=request.job_description,
        profile=profile,
        repos=repos,
        language_stats=language_stats,
        contributions=contributions,
        scores=scores,
        extracted_skills=extracted_skills,
    )

    return {
        "username": request.username,
        "ai_analysis": ai_analysis,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard Route
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the minimal testing dashboard."""
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "github_authenticated": settings.is_authenticated,
            "gemini_available": settings.has_gemini,
        },
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Error Handlers
# ═══════════════════════════════════════════════════════════════════════════════


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred",
            "error": str(exc),
        },
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Startup Events
# ═══════════════════════════════════════════════════════════════════════════════


@app.on_event("startup")
async def startup_event():
    """Log configuration on startup."""
    logger.info("=" * 60)
    logger.info("GitHub Profile Analyzer - Starting Up")
    logger.info(f"  GitHub Auth: {'✅ Authenticated' if settings.is_authenticated else '⚠️ Unauthenticated (60 req/hr)'}")
    logger.info(f"  Gemini AI:   {'✅ Available' if settings.has_gemini else '⚠️ Unavailable (keyword fallback)'}")
    logger.info(f"  Max Repos:   {settings.max_repos_to_analyze}")
    logger.info(f"  Max READMEs: {settings.max_readme_repos}")
    logger.info("=" * 60)
