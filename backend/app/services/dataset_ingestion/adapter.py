from __future__ import annotations

import json
from typing import Any

from backend.app.services.dataset_ingestion.loader import MalformedRecordError


REQUIRED_FIELDS = ("skills",)


def jsonl_record_to_profile(record: dict[str, Any]) -> dict[str, Any]:
    """
    Convert a JSONL dataset record into the internal candidate profile format
    used by the matching and ranking pipeline.
    """
    if not record:
        raise MalformedRecordError("Record is empty")

    skills = record.get("skills")
    if skills is None:
        raise MalformedRecordError("Missing required field: skills")
    if not isinstance(skills, list):
        raise MalformedRecordError("Field 'skills' must be a list")

    candidate_id = record.get("candidate_id") or record.get("id")
    applicant_name = (
        record.get("current_title")
        or record.get("headline")
        or candidate_id
        or "Unknown Candidate"
    )

    years_experience = record.get("years_experience")
    if years_experience is not None and not isinstance(years_experience, (int, float)):
        raise MalformedRecordError("Field 'years_experience' must be a number")

    profile_text = record.get("profile_text") or ""
    summary_text = record.get("summary_text") or profile_text[:500]

    structured_profile = {
        "candidate_id": candidate_id,
        "skills": skills,
        "years_experience": years_experience,
        "location": record.get("location") or "",
        "summary_text": summary_text,
        "profile_text": profile_text,
        "education": record.get("education") or [],
        "career_history": record.get("career_history") or [],
        "current_title": record.get("current_title") or "",
        "headline": record.get("headline") or "",
    }

    return {
        "candidate": structured_profile,
        "parsed_skills": json.dumps({"skills": skills}),
        "skills": skills,
        "resume_summary": summary_text,
        "applicant_name": applicant_name,
        "candidate_id": candidate_id,
    }
