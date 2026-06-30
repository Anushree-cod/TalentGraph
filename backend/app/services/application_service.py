import json
from typing import Any

from backend.app.services.resume_parser.pipeline import parse_resume_bytes
from backend.app.services.jd_matching.matcher import match_candidate_to_job


ALLOWED_RESUME_EXTENSIONS = (".pdf", ".docx")


def validate_resume_filename(filename: str) -> str:
    lowered = (filename or "").lower()
    if not any(lowered.endswith(ext) for ext in ALLOWED_RESUME_EXTENSIONS):
        raise ValueError("Only PDF and DOCX resume files are supported")
    if lowered.endswith(".docx"):
        raise ValueError("DOCX is accepted for upload, but resume parsing currently requires a PDF file")
    return lowered


def process_job_application(
    *,
    content: bytes,
    filename: str,
    user_id: int,
    job_requirements: str,
    years_experience: int | None = None,
) -> dict[str, Any]:
    validate_resume_filename(filename)

    structured_profile = parse_resume_bytes(content, user_id=user_id, filename=filename)
    if years_experience is not None:
        structured_profile["years_experience"] = years_experience

    parsed_skills = json.dumps({"skills": structured_profile.get("skills", [])})
    match_result = match_candidate_to_job(parsed_skills, job_requirements)
    ats_score = match_result.get("match_score", 0)

    return {
        "candidate": structured_profile,
        "matching": match_result,
        "skills": structured_profile.get("skills", []),
        "resume_summary": (
            structured_profile.get("summary_text")
            or structured_profile.get("profile_text", "")[:500]
        ),
        "ats_score": ats_score,
        "parsed_skills": parsed_skills,
    }
