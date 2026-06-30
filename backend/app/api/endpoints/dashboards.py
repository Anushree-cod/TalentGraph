from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
import json
from backend.app.db.session import get_db
from backend.app.api.deps import get_current_recruiter, get_current_user
from backend.app.db.models import User, Job, JobApplication, CandidateProfile
from backend.app.services.jd_matching.matcher import match_candidate_to_job
from backend.app.services.jd_matching.ranking import rank_candidates

router = APIRouter()


class ApplicationStatusUpdate(BaseModel):
    status: str


def _recruiter_jobs(db: Session, recruiter_id: int) -> List[Job]:
    return db.query(Job).filter(Job.recruiter_id == recruiter_id).all()


def _recruiter_applications(db: Session, recruiter_id: int) -> List[JobApplication]:
    job_ids = [job.id for job in _recruiter_jobs(db, recruiter_id)]
    if not job_ids:
        return []
    return db.query(JobApplication).filter(JobApplication.job_id.in_(job_ids)).all()


def _get_recruiter_application(
    db: Session,
    application_id: int,
    recruiter_id: int,
) -> tuple[JobApplication, Job]:
    application = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    job = db.query(Job).filter(
        Job.id == application.job_id,
        Job.recruiter_id == recruiter_id,
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Application not found or access denied")

    return application, job


def _build_candidate_payload(app: JobApplication, job: Job, profile: CandidateProfile | None) -> Dict[str, Any]:
    analysis: Dict[str, Any] = {}
    if app.analysis_json:
        try:
            analysis = json.loads(app.analysis_json)
        except json.JSONDecodeError:
            analysis = {}

    matching = analysis.get("matching", {})
    skills = analysis.get("skills", [])
    if not skills and profile and profile.parsed_skills:
        try:
            skills = json.loads(profile.parsed_skills).get("skills", [])
        except json.JSONDecodeError:
            skills = []

    match_score = app.match_score or analysis.get("ats_score", 0)
    if not analysis and profile and profile.parsed_skills:
        match_result = match_candidate_to_job(profile.parsed_skills, job.requirements)
        match_score = match_result.get("match_score", 0)
        matching = match_result
        if not skills:
            skills = matching.get("matched_skills", [])

    return {
        "application_id": app.id,
        "job_id": job.id,
        "job_title": job.title,
        "applicant_id": app.applicant_id,
        "applicant_name": app.full_name or f"Candidate #{app.applicant_id}",
        "email": app.email,
        "phone": app.phone,
        "status": app.status,
        "match_score": match_score,
        "ats_score": analysis.get("ats_score", match_score),
        "matched_skills": matching.get("matched_skills", []),
        "missing_skills": matching.get("missing_skills", []),
        "skills": skills,
        "years_experience": app.years_experience,
        "location": app.location or "",
        "resume_summary": analysis.get("resume_summary", ""),
        "resume_preview": analysis.get("candidate", {}).get("profile_text", "")
        or (profile.resume_text if profile else ""),
        "education": analysis.get("candidate", {}).get("education", []),
        "recommendation": matching.get("recommendation", "Profile Incomplete"),
        "cover_letter": app.cover_letter or "",
    }


@router.get("/recruiter/jobs/{job_id}/candidates", response_model=List[Dict[str, Any]])
def get_ranked_candidates_for_job(
    job_id: int,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """
    Get all candidates for a specific job, matched and ranked by the AI engine.
    """
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or access denied")

    applications = db.query(JobApplication).filter(JobApplication.job_id == job_id).all()

    candidates_data = []
    for app in applications:
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == app.applicant_id).first()
        payload = _build_candidate_payload(app, job, profile)
        app.match_score = payload["match_score"]
        candidates_data.append(payload)

    db.commit()
    return rank_candidates(candidates_data)


@router.get("/recruiter/metrics", response_model=Dict[str, Any])
def get_recruiter_metrics(
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    jobs = _recruiter_jobs(db, current_user.id)
    applications = _recruiter_applications(db, current_user.id)

    scores = [app.match_score for app in applications if app.match_score]
    avg_ats = round(sum(scores) / len(scores)) if scores else 0
    shortlisted = sum(1 for app in applications if app.status.lower() == "shortlisted")
    interviewing = sum(1 for app in applications if app.status.lower() == "interviewing")
    rejected = sum(1 for app in applications if app.status.lower() == "rejected")

    pipeline = [
        {"name": "Shortlisted", "value": shortlisted or 0, "color": "#22c55e"},
        {"name": "Interviewing", "value": interviewing or 0, "color": "#22d3ee"},
        {"name": "Rejected", "value": rejected or 0, "color": "#f43f5e"},
        {
            "name": "Applied",
            "value": sum(
                1 for app in applications
                if app.status.lower() in {"applied", "analyzed"}
            ) or 0,
            "color": "#8b5cf6",
        },
    ]

    applications_per_job = []
    for job in jobs[:7]:
        count = sum(1 for app in applications if app.job_id == job.id)
        applications_per_job.append({
            "day": job.title[:12],
            "count": count,
        })

    skill_scores: Dict[str, List[int]] = {}
    all_candidates: List[Dict[str, Any]] = []
    for app in applications:
        job = next((item for item in jobs if item.id == app.job_id), None)
        if not job:
            continue
        profile = db.query(CandidateProfile).filter(
            CandidateProfile.user_id == app.applicant_id
        ).first()
        payload = _build_candidate_payload(app, job, profile)
        app.match_score = payload["match_score"]
        all_candidates.append(payload)
        score = payload["ats_score"] or 0
        for skill in payload["skills"][:3]:
            skill_scores.setdefault(skill, []).append(score)

    db.commit()

    domain_data = []
    for skill, values in sorted(skill_scores.items(), key=lambda item: sum(item[1]) / len(item[1]), reverse=True)[:5]:
        domain_data.append({
            "domain": skill[:10],
            "score": round(sum(values) / len(values)),
        })

    top_candidates = rank_candidates(all_candidates)[:5]

    return {
        "total_jobs": len(jobs),
        "total_applications": len(applications),
        "avg_ats": avg_ats,
        "shortlisted": shortlisted,
        "interviewing": interviewing,
        "stats": {
            "candidates": len(applications),
            "shortlisted": shortlisted,
            "interviewing": interviewing,
            "avg_ats": avg_ats,
        },
        "pipeline": pipeline,
        "applications_per_job": applications_per_job,
        "domain_data": domain_data,
        "top_candidates": top_candidates,
    }


@router.get("/recruiter/applications/{application_id}", response_model=Dict[str, Any])
def get_application_detail(
    application_id: int,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    application, job = _get_recruiter_application(db, application_id, current_user.id)
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == application.applicant_id
    ).first()
    payload = _build_candidate_payload(application, job, profile)

    job_candidates = []
    for app in db.query(JobApplication).filter(JobApplication.job_id == job.id).all():
        app_profile = db.query(CandidateProfile).filter(
            CandidateProfile.user_id == app.applicant_id
        ).first()
        job_candidates.append(_build_candidate_payload(app, job, app_profile))

    ranked = rank_candidates(job_candidates)
    for candidate in ranked:
        if candidate["application_id"] == application_id:
            payload["rank"] = candidate.get("rank")
            break

    return payload


@router.patch("/recruiter/applications/{application_id}/status", response_model=Dict[str, Any])
def update_application_status(
    application_id: int,
    status_update: ApplicationStatusUpdate,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    allowed_statuses = {"shortlisted", "rejected", "analyzed", "applied", "interviewing"}
    new_status = status_update.status.lower()
    if new_status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Invalid application status")

    application, job = _get_recruiter_application(db, application_id, current_user.id)
    application.status = new_status
    db.commit()
    db.refresh(application)

    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == application.applicant_id
    ).first()
    return _build_candidate_payload(application, job, profile)


@router.get("/applicant/status")
def get_applicant_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard data for an applicant (their applications and statuses).
    """
    applications = db.query(JobApplication).filter(JobApplication.applicant_id == current_user.id).all()

    dashboard_data = []
    for app in applications:
        job = db.query(Job).filter(Job.id == app.job_id).first()
        dashboard_data.append({
            "job_id": job.id,
            "job_title": job.title,
            "status": app.status,
            "match_score": app.match_score,
            "ats_score": app.match_score,
        })

    return {"applications": dashboard_data}
