import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ALIASES_PATH = ROOT / "configs" / "skill_aliases.json"

PROFICIENCY_RANK = {
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3,
}

_aliases_cache: dict[str, str] | None = None


def load_skill_aliases(path: Path | None = None) -> dict[str, str]:
    global _aliases_cache
    aliases_path = path or DEFAULT_ALIASES_PATH
    if _aliases_cache is None or path is not None:
        with open(aliases_path, encoding="utf-8") as f:
            loaded = json.load(f)
        if path is not None:
            return loaded
        _aliases_cache = loaded
    return _aliases_cache


def to_canonical(raw_name: str, aliases: dict[str, str] | None = None) -> str:
    aliases = aliases or load_skill_aliases()
    key = raw_name.strip().lower()
    if not key:
        return ""
    if key in aliases:
        return aliases[key]
    return re.sub(r"[^a-z0-9]+", "_", key).strip("_")


def _merge_proficiency(existing: str | None, new: str | None) -> str | None:
    if not existing:
        return new
    if not new:
        return existing
    if PROFICIENCY_RANK.get(new, 0) > PROFICIENCY_RANK.get(existing, 0):
        return new
    return existing


def canonicalize_skill_entries(
    skills_list: list[dict],
    aliases: dict[str, str] | None = None,
) -> tuple[list[str], list[dict], list[str]]:
    aliases = aliases or load_skill_aliases()
    detailed_by_name: dict[str, dict] = {}
    raw_by_canonical: dict[str, str] = {}

    for skill in skills_list:
        raw = skill.get("name", "").strip()
        if not raw:
            continue

        canonical = to_canonical(raw, aliases)
        if not canonical:
            continue

        endorsements = skill.get("endorsements") or 0
        duration_months = skill.get("duration_months") or 0

        if canonical not in detailed_by_name:
            detailed_by_name[canonical] = {
                "name": canonical,
                "proficiency": skill.get("proficiency"),
                "endorsements": endorsements,
                "duration_months": duration_months,
            }
            raw_by_canonical[canonical] = raw
            continue

        entry = detailed_by_name[canonical]
        entry["proficiency"] = _merge_proficiency(
            entry.get("proficiency"),
            skill.get("proficiency"),
        )
        entry["endorsements"] = (entry.get("endorsements") or 0) + endorsements
        entry["duration_months"] = max(
            entry.get("duration_months") or 0,
            duration_months,
        )

    canonical_names = sorted(detailed_by_name.keys())
    skills_detailed = [detailed_by_name[name] for name in canonical_names]
    raw_skills = [raw_by_canonical[name] for name in canonical_names]
    return canonical_names, skills_detailed, raw_skills


def canonicalize_assessment_scores(
    scores: dict | None,
    known_skills: set[str] | None = None,
    aliases: dict[str, str] | None = None,
) -> tuple[dict[str, float], dict[str, float]]:
    if not scores:
        return {}, {}

    aliases = aliases or load_skill_aliases()
    known_skills = known_skills or set()
    matched: dict[str, float] = {}
    orphan: dict[str, float] = {}
    for skill_name, score in scores.items():
        canonical = to_canonical(skill_name, aliases)
        if not canonical:
            continue
        if canonical in known_skills:
            matched[canonical] = score
        else:
            orphan[canonical] = score
    return matched, orphan
