from __future__ import annotations

from typing import Any, Iterator

from backend.app.db.models import Job
from backend.app.services.dataset_ingestion.adapter import jsonl_record_to_profile
from backend.app.services.dataset_ingestion.loader import MalformedRecordError
from backend.app.services.jd_matching.matcher import match_candidate_to_job
from backend.app.services.jd_matching.ranking import rank_candidates


def _job_requirements(job: Job) -> str:
    parts = [job.requirements or "", job.skills_required or "", job.description or ""]
    return " ".join(part for part in parts if part).strip()


def _build_match_payload(
    profile: dict[str, Any],
    job: Job,
    match_result: dict[str, Any],
) -> dict[str, Any]:
    match_score = match_result.get("match_score", 0)
    return {
        "candidate_id": profile.get("candidate_id"),
        "applicant_name": profile.get("applicant_name"),
        "job_id": job.id,
        "job_title": job.title,
        "status": "dataset",
        "match_score": match_score,
        "ats_score": match_score,
        "skills": profile.get("skills", []),
        "matched_skills": match_result.get("matched_skills", []),
        "missing_skills": match_result.get("missing_skills", []),
        "recommendation": match_result.get("recommendation", "Profile Incomplete"),
        "years_experience": profile["candidate"].get("years_experience"),
        "location": profile["candidate"].get("location", ""),
        "resume_summary": profile.get("resume_summary", ""),
        "resume_preview": profile["candidate"].get("profile_text", ""),
        "education": profile["candidate"].get("education", []),
    }


def process_dataset_against_jobs(
    records: Iterator[dict[str, Any]],
    jobs: list[Job],
    *,
    limit: int | None = None,
    loader_errors: list[str] | None = None,
) -> dict[str, Any]:
    """
    Match streamed dataset records against jobs and return ranked results.

    Designed for test runs (with limit) and future full-dataset batch processing.
    """
    if not jobs:
        return {
            "records_requested": limit,
            "records_processed": 0,
            "records_skipped": 0,
            "jobs_matched": [],
            "errors": ["No recruiter jobs found to match against"],
        }

    candidates_by_job: dict[int, list[dict[str, Any]]] = {job.id: [] for job in jobs}
    errors: list[str] = list(loader_errors or [])
    processed = 0
    skipped = 0

    for index, record in enumerate(records, start=1):
        if limit is not None and processed >= limit:
            break

        try:
            profile = jsonl_record_to_profile(record)
        except MalformedRecordError as exc:
            skipped += 1
            errors.append(f"Record {index}: {exc}")
            continue

        for job in jobs:
            requirements = _job_requirements(job)
            if not requirements:
                continue
            match_result = match_candidate_to_job(profile["parsed_skills"], requirements)
            candidates_by_job[job.id].append(_build_match_payload(profile, job, match_result))

        processed += 1

    jobs_matched = []
    for job in jobs:
        ranked = rank_candidates(candidates_by_job[job.id])
        jobs_matched.append(
            {
                "job_id": job.id,
                "job_title": job.title,
                "candidate_count": len(ranked),
                "ranked_candidates": ranked,
            }
        )

    return {
        "records_requested": limit,
        "records_processed": processed,
        "records_skipped": skipped,
        "jobs_compared": len(jobs),
        "jobs_matched": jobs_matched,
        "errors": errors,
    }


def aggregate_best_candidate_matches(jobs_matched: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pick the highest-scoring job match for each dataset candidate."""
    best_by_candidate: dict[Any, dict[str, Any]] = {}

    for job_result in jobs_matched:
        job_id = job_result["job_id"]
        job_title = job_result["job_title"]
        for candidate in job_result["ranked_candidates"]:
            candidate_id = candidate.get("candidate_id")
            score = candidate.get("match_score", 0)
            existing = best_by_candidate.get(candidate_id)
            if existing is None or score > existing.get("match_score", 0):
                best_by_candidate[candidate_id] = {
                    **candidate,
                    "best_job_id": job_id,
                    "best_job_title": job_title,
                    "job_id": job_id,
                    "job_title": job_title,
                }

    return rank_candidates(list(best_by_candidate.values()))
