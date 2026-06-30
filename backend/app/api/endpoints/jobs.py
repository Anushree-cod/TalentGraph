from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from backend.app.db.session import get_db
from backend.app.api.deps import get_current_user, get_current_recruiter
from backend.app.db.models import User, Job, JobApplication, CandidateProfile
from backend.app.schemas.job import JobCreate, JobResponse, ApplicationResponse
from backend.app.services.application_service import process_job_application

router = APIRouter()

@router.post("/", response_model=JobResponse)
def create_job(
    job_in: JobCreate,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """
    Create a new job posting (Recruiter only).
    """
    requirements = job_in.requirements or job_in.skills_required or ""
    job = Job(
        title=job_in.title,
        description=job_in.description,
        requirements=requirements,
        skills_required=job_in.skills_required,
        experience_required=job_in.experience_required,
        location=job_in.location,
        recruiter_id=current_user.id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return _job_response(job, current_user)


def _job_response(job: Job, recruiter: User | None = None) -> dict:
    company = None
    if recruiter and recruiter.email and "@" in recruiter.email:
        company = recruiter.email.split("@", 1)[1].split(".", 1)[0].title()

    return {
        "id": job.id,
        "title": job.title,
        "description": job.description,
        "requirements": job.requirements or "",
        "skills_required": job.skills_required or "",
        "experience_required": job.experience_required or "",
        "location": job.location or "",
        "recruiter_id": job.recruiter_id,
        "created_at": job.created_at,
        "company": company,
    }

@router.get("/", response_model=List[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    """
    Get all active job postings.
    """
    jobs = db.query(Job).all()
    if not jobs:
        return []
    recruiter_ids = {job.recruiter_id for job in jobs}
    recruiters = {
        user.id: user
        for user in db.query(User).filter(User.id.in_(recruiter_ids)).all()
    } if recruiter_ids else {}
    return [_job_response(job, recruiters.get(job.recruiter_id)) for job in jobs]

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    recruiter = db.query(User).filter(User.id == job.recruiter_id).first()
    return _job_response(job, recruiter)

@router.post("/{job_id}/apply", response_model=dict)
async def apply_to_job(
    job_id: int,
    resume: UploadFile = File(...),
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    location: str = Form(...),
    years_experience: int = Form(...),
    expected_salary: Optional[str] = Form(None),
    cover_letter: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a job application with resume analysis and ATS matching.
    """
    if current_user.is_recruiter:
        raise HTTPException(status_code=403, detail="Recruiters cannot apply to jobs")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    existing = db.query(JobApplication).filter(
        JobApplication.job_id == job_id,
        JobApplication.applicant_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already applied to this job")

    content = await resume.read()
    filename = resume.filename or "resume.pdf"

    try:
        analysis = process_job_application(
            content=content,
            filename=filename,
            user_id=current_user.id,
            job_requirements=job.requirements,
            years_experience=years_experience,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Application analysis failed: {exc}") from exc

    application = JobApplication(
        job_id=job_id,
        applicant_id=current_user.id,
        status="analyzed",
        match_score=analysis["ats_score"],
        full_name=full_name,
        email=email,
        phone=phone,
        location=location,
        years_experience=years_experience,
        expected_salary=expected_salary,
        cover_letter=cover_letter,
        analysis_json=json.dumps(analysis),
    )
    db.add(application)

    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)

    profile.resume_text = analysis["candidate"].get("profile_text", "")
    profile.parsed_skills = analysis["parsed_skills"]
    db.commit()
    db.refresh(application)

    return {
        "message": "Application submitted and analyzed successfully",
        "application_id": application.id,
        "status": application.status,
        "match_score": application.match_score,
        "ats_score": analysis["ats_score"],
        "skills": analysis["skills"],
        "recommendation": analysis["matching"].get("recommendation"),
        "job_title": job.title,
    }
