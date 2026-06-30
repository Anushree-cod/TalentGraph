from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
import json
from typing import Optional
from pydantic import BaseModel, Field
from backend.app.db.session import get_db
from backend.app.api.deps import get_current_user, get_current_recruiter
from backend.app.db.models import User, CandidateProfile, Job
from backend.app.schemas.github_schemas import AnalyzeRequest, ContributionData, ProfileAnalysis
from backend.app.services.github_analyzer.github_fetcher import GitHubFetcher
from backend.app.services.github_analyzer.data_processor import DataProcessor
from backend.app.services.resume_parser.pipeline import parse_resume_bytes
from backend.app.services.jd_matching.matcher import match_candidate_to_job
from backend.app.services.jd_matching.ranking import rank_candidates
from backend.app.services.dataset_ingestion import (
    DatasetIngestionError,
    aggregate_best_candidate_matches,
    process_dataset_against_jobs,
    resolve_dataset_path,
    stream_jsonl_records,
)

router = APIRouter()


class TestDatasetRequest(BaseModel):
    dataset_path: str
    limit: int = Field(default=5, ge=1, le=1000)


@router.post("/test-dataset", response_model=dict)
def test_dataset_ingestion(
    request: TestDatasetRequest,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    """
    Stream a JSONL dataset, process the first N records, and rank against all recruiter jobs.
    """
    try:
        dataset_file = resolve_dataset_path(request.dataset_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DatasetIngestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    jobs = db.query(Job).all()
    if not jobs:
        raise HTTPException(
            status_code=404,
            detail="No jobs found in the system. Post a job before testing datasets.",
        )

    loader_errors: list[str] = []
    try:
        record_stream = stream_jsonl_records(
            dataset_file,
            limit=request.limit,
            errors=loader_errors,
        )
        result = process_dataset_against_jobs(
            record_stream,
            jobs,
            limit=request.limit,
            loader_errors=loader_errors,
        )
    except DatasetIngestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    best_matches = aggregate_best_candidate_matches(result["jobs_matched"])

    return {
        "dataset_path": str(dataset_file),
        **result,
        "best_matches": best_matches,
    }


@router.post("/resume", response_model=dict)
async def upload_resume(
    resume: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    job_title: Optional[str] = Form(None),
    company: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and parse a resume.
    """
    if not resume.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Read file content
    content = await resume.read()
    
    try:
        structured_profile = parse_resume_bytes(
            content,
            user_id=current_user.id,
            filename=resume.filename or "resume.pdf",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {exc}") from exc

    resume_text = structured_profile.get("profile_text", "")
    parsed_skills = json.dumps({"skills": structured_profile.get("skills", [])})
    
    # Save to db
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)
    
    profile.resume_text = resume_text
    profile.parsed_skills = parsed_skills
    db.commit()
    
    response = {
        "message": "Resume uploaded and parsed successfully",
        "skills": structured_profile.get("skills", []),
        "candidate": structured_profile,
        "job": {
            "title": job_title or "",
            "company": company or "",
            "description": job_description or "",
        },
    }

    if job_description and job_description.strip():
        match_result = match_candidate_to_job(parsed_skills, job_description)
        ranked = rank_candidates([
            {
                "application_id": 1,
                "applicant_id": current_user.id,
                "status": "analyzed",
                **match_result,
            }
        ])
        response["matching"] = match_result
        response["ranking"] = ranked[0] if ranked else None

    return response

@router.post("/github", response_model=dict)
async def analyze_github(
    request: AnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze GitHub profile and store results.
    """
    try:
        username = request.get_username()
        fetcher = GitHubFetcher()
        raw_data = await fetcher.fetch_all(username)
        processor = DataProcessor()
        profile = raw_data["profile"]
        repos = raw_data["repositories"]
        contributions = raw_data.get("contributions") or ContributionData()
        language_stats = processor.process_languages(repos)
        scores = processor.calculate_scores(profile, repos, contributions, language_stats)
        extracted_skills = processor.extract_skills(repos, language_stats)
        processed_data = ProfileAnalysis(
            profile=profile,
            repositories=repos,
            language_stats=language_stats,
            contributions=contributions,
            scores=scores,
            extracted_skills=extracted_skills,
            metadata=raw_data.get("metadata", {}),
        )
        
        # Save to db
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
        if not profile:
            profile = CandidateProfile(user_id=current_user.id)
            db.add(profile)
            
        profile.github_analysis = '{"username": "' + username + '", "status": "analyzed"}'
        db.commit()
        
        return {"message": "GitHub profile analyzed successfully", "data": processed_data.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
