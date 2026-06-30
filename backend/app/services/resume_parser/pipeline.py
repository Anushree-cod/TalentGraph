"""
Member-1 resume parsing pipeline for uploaded PDF files.

Flow: PDF bytes -> text -> skill extraction -> canonicalization -> structured profile.
"""

from __future__ import annotations

import json
import re
import tempfile
import uuid
from pathlib import Path
from typing import Any

from backend.app.services.resume_parser.candidate_builder_profile import build_candidate_profile
from backend.app.services.resume_parser.config import (
    SECTION_ALIASES_PATH,
    SKILLS_ALIASES_PATH,
    SKILLS_MASTER_PATH,
)
from backend.app.services.resume_parser.resume_parser import extract_text_from_pdf
from backend.app.services.resume_parser.skill_canonicalizer import (
    canonicalize_skill_entries,
    load_skill_aliases,
)
from backend.app.services.resume_parser.skill_extractor import (
    detect_all_sections,
    extract_skills,
    load_section_aliases,
)


def _first_nonempty_line(text: str, max_len: int = 120) -> str:
    for line in text.splitlines():
        cleaned = line.strip()
        if cleaned:
            return cleaned[:max_len]
    return ""


def _parse_career_history(experience_text: str) -> list[dict[str, Any]]:
    if not experience_text.strip():
        return []

    blocks = re.split(r"\n\s*\n", experience_text.strip())
    history: list[dict[str, Any]] = []
    for block in blocks[:8]:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        title = lines[0]
        company = ""
        description = " ".join(lines[1:]) if len(lines) > 1 else ""
        if " at " in title:
            title, company = title.split(" at ", 1)
        history.append(
            {
                "title": title.strip(),
                "company": company.strip(),
                "start_date": None,
                "end_date": None,
                "is_current": False,
                "industry": None,
                "description": description.strip(),
            }
        )
    return history


def _parse_education(education_text: str) -> list[dict[str, Any]]:
    if not education_text.strip():
        return []

    entries: list[dict[str, Any]] = []
    for line in education_text.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        entries.append(
            {
                "degree": cleaned,
                "field_of_study": None,
                "institution": None,
                "tier": None,
            }
        )
    return entries[:6]


def _skill_results_to_entries(skill_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for item in skill_results:
        name = str(item.get("skill", "")).strip()
        if not name:
            continue
        entries.append(
            {
                "name": name,
                "proficiency": item.get("confidence"),
                "endorsements": int(item.get("frequency") or 0),
                "duration_months": 0,
            }
        )
    return entries


def _build_candidate_record(
    resume_text: str,
    skill_results: list[dict[str, Any]],
    user_id: int,
) -> dict[str, Any]:
    section_aliases = load_section_aliases(SECTION_ALIASES_PATH)
    sections = detect_all_sections(resume_text, section_aliases)

    summary = sections.get("summary") or sections.get("objective") or ""
    experience = sections.get("experience") or ""
    education = sections.get("education") or ""
    current_title = _first_nonempty_line(experience)

    return {
        "candidate_id": f"upload-{user_id}-{uuid.uuid4().hex[:8]}",
        "profile": {
            "headline": _first_nonempty_line(summary) or current_title,
            "current_title": current_title,
            "years_of_experience": None,
            "location": "",
            "summary": summary.strip(),
        },
        "career_history": _parse_career_history(experience),
        "education": _parse_education(education),
        "certifications": [],
        "languages": [],
        "skills": _skill_results_to_entries(skill_results),
        "redrob_signals": {
            "open_to_work_flag": False,
            "github_activity_score": -1,
            "expected_salary_range_inr_lpa": {},
            "preferred_work_mode": None,
            "notice_period_days": None,
            "willing_to_relocate": None,
            "skill_assessment_scores": {},
        },
    }


def parse_resume_text(resume_text: str, user_id: int) -> dict[str, Any]:
    """Run the Member-1 pipeline on extracted resume text."""
    skill_results = extract_skills(
        resume_text,
        skills_csv_path=SKILLS_MASTER_PATH,
        skill_aliases_path=SKILLS_ALIASES_PATH,
        section_aliases_path=SECTION_ALIASES_PATH,
    )

    candidate_record = _build_candidate_record(resume_text, skill_results, user_id)
    aliases = load_skill_aliases()
    canonical_skills, skills_detailed, raw_skills = canonicalize_skill_entries(
        candidate_record.get("skills", []),
        aliases,
    )

    return build_candidate_profile(
        candidate_record,
        canonical_skills,
        skills_detailed,
        raw_skills,
    )


def parse_resume_bytes(content: bytes, user_id: int, filename: str = "resume.pdf") -> dict[str, Any]:
    """Run the Member-1 pipeline on an uploaded PDF file."""
    suffix = Path(filename).suffix or ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        resume_text = extract_text_from_pdf(tmp_path)
        if not resume_text.strip():
            raise ValueError("No text could be extracted from the uploaded PDF")
        return parse_resume_text(resume_text, user_id)
    finally:
        Path(tmp_path).unlink(missing_ok=True)
