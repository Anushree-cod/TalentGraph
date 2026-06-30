from backend.app.services.resume_parser.skill_canonicalizer import canonicalize_assessment_scores

SCHEMA_VERSION = "1.0"

VALID_WORK_MODES = frozenset({"remote", "hybrid", "onsite", "flexible"})
WORK_MODE_ALIASES = {
    "remote": "remote",
    "wfh": "remote",
    "work from home": "remote",
    "hybrid": "hybrid",
    "onsite": "onsite",
    "on-site": "onsite",
    "on site": "onsite",
    "in-office": "onsite",
    "in office": "onsite",
    "office": "onsite",
    "flexible": "flexible",
}


def _normalize_work_mode(mode) -> str | None:
    if mode is None:
        return None
    key = str(mode).strip().lower()
    if not key:
        return None
    normalized = WORK_MODE_ALIASES.get(key, key)
    if normalized in VALID_WORK_MODES:
        return normalized
    return "flexible"


def _normalize_salary_range(salary_raw: dict | None) -> tuple[dict, dict]:
    if not isinstance(salary_raw, dict):
        return {}, {}

    preserved: dict = {}
    normalized: dict = {}
    for bound in ("min", "max"):
        value = salary_raw.get(bound)
        if isinstance(value, (int, float)):
            preserved[bound] = value
            normalized[bound] = {
                "value": value,
                "currency": "INR",
                "unit": "LPA",
            }
    return preserved, normalized


def build_candidate_profile(
    candidate,
    normalized_skills,
    skills_detailed=None,
    raw_skills=None,
):

    profile = candidate.get("profile", {})
    redrob = candidate.get("redrob_signals", {})

    # -----------------------------
    # Skills
    # -----------------------------
    skills = list(normalized_skills)
    raw_skills = list(raw_skills or [])
    # -----------------------------
    # Career History
    # -----------------------------
    career_history = []

    career_text_parts = []

    for job in candidate.get("career_history", []):

        career_history.append({
            "title": job.get("title"),
            "company": job.get("company"),
            "start_date": job.get("start_date"),
            "end_date": job.get("end_date"),
            "is_current": job.get("is_current", False),
            "industry": job.get("industry")
        })

        title = (job.get("title") or "").strip()
        company = (job.get("company") or "").strip()
        description = (job.get("description") or "").strip()

        if title and company:
            text = f"{title} at {company}. {description}"
        elif title:
            text = f"{title}. {description}"
        else:
            text = description

        career_text_parts.append(text)

    career_text = " ".join(career_text_parts)

    # -----------------------------
    # Education
    # -----------------------------
    education = []

    for edu in candidate.get("education", []):

        education.append({
            "degree": edu.get("degree"),
            "field": edu.get("field_of_study"),
            "institution": edu.get("institution"),
            "tier": edu.get("tier")
        })

    # -----------------------------
    # Certifications
    # -----------------------------
    certifications = []

    for cert in candidate.get("certifications", []):

        certifications.append({
            "name": cert.get("name"),
            "issuer": cert.get("issuer"),
            "year": cert.get("year")
        })

    # -----------------------------
    # Languages
    # -----------------------------
    languages = []

    for lang in candidate.get("languages", []):

        languages.append({
            "language": lang.get("language"),
            "proficiency": lang.get("proficiency")
        })

    # -----------------------------
    # Profile Text
    # -----------------------------
    headline = profile.get("headline", "")
    current_title = profile.get("current_title", "")
    summary_text = profile.get("summary", "")

    skills_line = ", ".join(sorted(skills))
    education_parts = [
        f"{(e.get('degree') or '').strip()} {(e.get('field') or '').strip()}".strip()
        for e in education
    ]
    education_line = ", ".join(p for p in education_parts if p)

    profile_text = "\n".join([
        f"Headline: {headline}",
        "",
        f"Current Title: {current_title}",
        "",
        f"Skills: {skills_line}",
        "",
        "Summary:",
        summary_text,
        "",
        "Career:",
        career_text,
        "",
        "Education:",
        education_line,
    ]).strip()

    # -----------------------------
    # Recruiter Signals
    # -----------------------------
    salary_preserved, salary_normalized = _normalize_salary_range(
        redrob.get("expected_salary_range_inr_lpa"),
    )
    assessment_scores, orphan_assessment_scores = canonicalize_assessment_scores(
        redrob.get("skill_assessment_scores") or {},
        set(skills),
    )

    recruiter_signals = {
        "expected_salary_range_inr_lpa": salary_preserved,
        "expected_salary_range": salary_normalized,
        "preferred_work_mode": _normalize_work_mode(redrob.get("preferred_work_mode")),
        "notice_period_days": redrob.get("notice_period_days"),
        "willing_to_relocate": redrob.get("willing_to_relocate"),
        "skill_assessment_scores": assessment_scores,
        "orphan_assessment_scores": orphan_assessment_scores,
    }

    # -----------------------------
    # Final Structured Profile
    # -----------------------------
    return {

        "schema_version": SCHEMA_VERSION,

        "candidate_id": candidate.get("candidate_id"),

        "headline": headline,

        "current_title": current_title,

        "years_experience": profile.get("years_of_experience"),

        "location": profile.get("location"),

        "skills": skills,

        "raw_skills": raw_skills,

        "skills_detailed": skills_detailed or [],

        "summary_text": summary_text,

        "career_text": career_text,

        "career_history": career_history,

        "education": education,

        "certifications": certifications,

        "languages": languages,

        "open_to_work": redrob.get("open_to_work_flag", False),

        "github_activity_score": redrob.get(
            "github_activity_score",
            -1
        ),

        "recruiter_signals": recruiter_signals,

        "profile_text": profile_text.strip()
    }
