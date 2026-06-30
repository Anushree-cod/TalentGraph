import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from candidate_builder_profile import build_candidate_profile
from skill_canonicalizer import canonicalize_skill_entries, load_skill_aliases, to_canonical

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "datasets" / "provided_dataset" / "candidates.jsonl"
SCHEMA_PATH = ROOT / "backend" / "schema" / "structured_candidate_schema.json"

TOP_LEVEL_LIST_FIELDS = (
    "skills",
    "raw_skills",
    "skills_detailed",
    "career_history",
    "education",
    "certifications",
    "languages",
)
TOP_LEVEL_OBJECT_FIELDS = ("recruiter_signals",)


def _first_candidate():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.loads(f.readline())


def _build_profile(candidate):
    aliases = load_skill_aliases()
    canonical_skills, skills_detailed, raw_skills = canonicalize_skill_entries(
        candidate.get("skills", []),
        aliases,
    )
    return build_candidate_profile(
        candidate, canonical_skills, skills_detailed, raw_skills
    )


def _first_profile():
    return _build_profile(_first_candidate())


def _check_json_type(value, type_spec):
    if isinstance(type_spec, list):
        return any(_check_json_type(value, item) for item in type_spec)

    checks = {
        "string": lambda v: isinstance(v, str),
        "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "boolean": lambda v: isinstance(v, bool),
        "array": lambda v: isinstance(v, list),
        "object": lambda v: isinstance(v, dict),
        "null": lambda v: v is None,
    }
    checker = checks.get(type_spec)
    return checker(value) if checker else True


def _validate_property(value, prop_schema):
    if "type" in prop_schema:
        assert _check_json_type(value, prop_schema["type"]), (
            f"expected type {prop_schema['type']}, got {type(value).__name__}"
        )

    if "enum" in prop_schema and value is not None:
        assert value in prop_schema["enum"]

    prop_type = prop_schema.get("type")
    if prop_type == "array" or (isinstance(prop_type, list) and "array" in prop_type):
        item_schema = prop_schema.get("items", {})
        for item in value:
            if item_schema.get("type") == "string":
                assert isinstance(item, str)
            elif item_schema.get("type") == "object":
                for sub_key, sub_prop in item_schema.get("properties", {}).items():
                    if sub_key in item:
                        _validate_property(item[sub_key], sub_prop)

    if prop_type == "object" or (isinstance(prop_type, list) and "object" in prop_type):
        for sub_key, sub_prop in prop_schema.get("properties", {}).items():
            if sub_key not in value:
                continue
            sub_value = value[sub_key]
            if sub_value is None:
                continue
            _validate_property(sub_value, sub_prop)

        if prop_schema.get("additionalProperties") == {"type": "number"}:
            for sub_value in value.values():
                assert isinstance(sub_value, (int, float)) and not isinstance(
                    sub_value, bool
                )


def _validate_against_schema(profile, schema):
    for field in schema.get("required", []):
        assert field in profile, f"missing required field: {field}"

    for key, prop_schema in schema.get("properties", {}).items():
        if key in profile:
            _validate_property(profile[key], prop_schema)


def _load_schema():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_profile_text_format():
    profile = _first_profile()

    assert profile["profile_text"].strip()
    assert "    Current Title:" not in profile["profile_text"]
    assert "Current Title: Backend Engineer" in profile["profile_text"]
    assert "Skills:" in profile["profile_text"]
    skills_line = profile["profile_text"].split("Skills:")[1].split("\n")[0]
    assert ", " in skills_line.strip()
    assert "Summary:" in profile["profile_text"]
    assert "Career:" in profile["profile_text"]
    assert "Education:" in profile["profile_text"]


def test_career_text_includes_company():
    profile = _first_profile()
    assert " at Mindtree." in profile["career_text"]
    assert " at Dunder Mifflin." in profile["career_text"]


def test_schema_fields():
    profile = _first_profile()

    assert profile["candidate_id"]
    assert profile["schema_version"]
    expected_keys = {
        "schema_version",
        "candidate_id",
        "headline",
        "current_title",
        "years_experience",
        "location",
        "skills",
        "raw_skills",
        "skills_detailed",
        "summary_text",
        "career_text",
        "career_history",
        "education",
        "certifications",
        "languages",
        "open_to_work",
        "github_activity_score",
        "recruiter_signals",
        "profile_text",
    }
    assert set(profile.keys()) == expected_keys
    assert profile["schema_version"] == "1.0"


def test_skill_canonicalization():
    aliases = load_skill_aliases()

    assert to_canonical("LLM", aliases) == "large_language_models"
    assert to_canonical("llms", aliases) == "large_language_models"
    assert to_canonical("Large Language Models", aliases) == "large_language_models"
    assert to_canonical("Fine-tuning LLMs", aliases) == "large_language_models"
    assert to_canonical("JS", aliases) == "javascript"
    assert to_canonical("Node.js", aliases) == "nodejs"


def test_skills_remain_string_array():
    profile = _first_profile()

    assert isinstance(profile["skills"], list)
    assert profile["skills"]
    assert all(isinstance(skill, str) for skill in profile["skills"])
    assert "large_language_models" in profile["skills"]
    assert "fine-tuning llms" not in profile["skills"]


def test_skills_detailed_preserves_metadata():
    profile = _first_profile()
    nlp = next(s for s in profile["skills_detailed"] if s["name"] == "nlp")
    assert nlp["proficiency"] == "advanced"
    assert nlp["endorsements"] == 37
    assert nlp["duration_months"] == 26


def test_raw_skills_preserved():
    profile = _first_profile()
    assert "Fine-tuning LLMs" in profile["raw_skills"]
    assert len(profile["raw_skills"]) == len(profile["skills"])


def test_no_null_list_or_object_fields():
    profile = _first_profile()

    for field in TOP_LEVEL_LIST_FIELDS:
        assert profile[field] is not None
        assert isinstance(profile[field], list)

    for field in TOP_LEVEL_OBJECT_FIELDS:
        assert profile[field] is not None
        assert isinstance(profile[field], dict)

    signals = profile["recruiter_signals"]
    assert "preferred_work_mode" in signals
    assert "notice_period_days" in signals
    assert signals["expected_salary_range_inr_lpa"] is not None
    assert signals["expected_salary_range"] is not None
    assert signals["skill_assessment_scores"] is not None
    assert signals["orphan_assessment_scores"] is not None


def test_recruiter_signals_passthrough():
    profile = _first_profile()
    signals = profile["recruiter_signals"]

    assert signals["notice_period_days"] == 60
    assert signals["preferred_work_mode"] == "onsite"
    assert signals["willing_to_relocate"] is False
    assert signals["expected_salary_range_inr_lpa"]["min"] == 18.7
    assert signals["expected_salary_range"]["min"]["value"] == 18.7
    assert signals["expected_salary_range"]["min"]["currency"] == "INR"
    assert signals["expected_salary_range"]["min"]["unit"] == "LPA"
    assert signals["skill_assessment_scores"]["nlp"] == 38.8
    assert signals["skill_assessment_scores"]["large_language_models"] == 41.6
    assert signals["orphan_assessment_scores"] == {}


def test_conforms_to_structured_candidate_schema():
    profile = _first_profile()
    schema = _load_schema()
    _validate_against_schema(profile, schema)


if __name__ == "__main__":
    tests = [
        ("test_profile_text_format", test_profile_text_format),
        ("test_career_text_includes_company", test_career_text_includes_company),
        ("test_schema_fields", test_schema_fields),
        ("test_skill_canonicalization", test_skill_canonicalization),
        ("test_skills_remain_string_array", test_skills_remain_string_array),
        ("test_skills_detailed_preserves_metadata", test_skills_detailed_preserves_metadata),
        ("test_raw_skills_preserved", test_raw_skills_preserved),
        ("test_no_null_list_or_object_fields", test_no_null_list_or_object_fields),
        ("test_recruiter_signals_passthrough", test_recruiter_signals_passthrough),
        ("test_conforms_to_structured_candidate_schema", test_conforms_to_structured_candidate_schema),
    ]
    passed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"[OK] {name}")
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {name}: {e}")

    print(f"\nResult: {passed}/{len(tests)} passed")
    if passed != len(tests):
        sys.exit(1)
