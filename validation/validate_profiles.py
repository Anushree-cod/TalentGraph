import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = ROOT / "datasets" / "structured_candidates.jsonl"
DEFAULT_SCHEMA = ROOT / "backend" / "schema" / "structured_candidate_schema.json"


def _is_missing_string(value) -> bool:
    return not value or not str(value).strip()


def _check_json_type(value, type_spec) -> bool:
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


def _validate_property(value, prop_schema) -> bool:
    if "type" in prop_schema and not _check_json_type(value, prop_schema["type"]):
        return False

    if "enum" in prop_schema and value is not None and value not in prop_schema["enum"]:
        return False

    prop_type = prop_schema.get("type")
    if prop_type == "array" or (isinstance(prop_type, list) and "array" in prop_type):
        item_schema = prop_schema.get("items", {})
        for item in value:
            if item_schema.get("type") == "string" and not isinstance(item, str):
                return False
            if item_schema.get("type") == "object":
                for sub_key, sub_prop in item_schema.get("properties", {}).items():
                    if sub_key in item and not _validate_property(item[sub_key], sub_prop):
                        return False

    if prop_type == "object" or (isinstance(prop_type, list) and "object" in prop_type):
        for sub_key, sub_prop in prop_schema.get("properties", {}).items():
            if sub_key not in value:
                continue
            sub_value = value[sub_key]
            if sub_value is None:
                continue
            if not _validate_property(sub_value, sub_prop):
                return False

        extra_props = prop_schema.get("additionalProperties")
        if extra_props == {"type": "number"}:
            for sub_value in value.values():
                if not isinstance(sub_value, (int, float)) or isinstance(sub_value, bool):
                    return False

    return True


def _validate_with_stdlib(profile: dict, schema: dict) -> bool:
    for field in schema.get("required", []):
        if field not in profile:
            return False

    for key, prop_schema in schema.get("properties", {}).items():
        if key in profile and not _validate_property(profile[key], prop_schema):
            return False

    return True


def _load_schema_validator(schema_path: Path):
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)

    try:
        import jsonschema

        validator = jsonschema.Draft7Validator(schema)
        return schema, lambda profile: validator.is_valid(profile)
    except ImportError:
        return schema, lambda profile: _validate_with_stdlib(profile, schema)


def validate_profiles(dataset_path: Path, schema_path: Path) -> dict:
    schema, is_schema_valid = _load_schema_validator(schema_path)

    stats = {
        "total_profiles": 0,
        "invalid_json_rows": 0,
        "missing_candidate_id": 0,
        "missing_profile_text": 0,
        "empty_skills": 0,
        "duplicate_ids": 0,
        "missing_recruiter_signals": 0,
        "missing_schema_version": 0,
        "schema_failures": 0,
    }

    seen_ids: set[str] = set()
    duplicate_ids: set[str] = set()

    with open(dataset_path, encoding="utf-8") as infile:
        for line in infile:
            if not line.strip():
                continue

            stats["total_profiles"] += 1

            try:
                profile = json.loads(line)
            except json.JSONDecodeError:
                stats["invalid_json_rows"] += 1
                continue

            if not isinstance(profile, dict):
                stats["invalid_json_rows"] += 1
                continue

            candidate_id = profile.get("candidate_id")
            if _is_missing_string(candidate_id):
                stats["missing_candidate_id"] += 1
            else:
                if candidate_id in seen_ids:
                    duplicate_ids.add(candidate_id)
                seen_ids.add(candidate_id)

            if _is_missing_string(profile.get("profile_text")):
                stats["missing_profile_text"] += 1

            skills = profile.get("skills")
            if not isinstance(skills, list) or len(skills) == 0:
                stats["empty_skills"] += 1

            recruiter_signals = profile.get("recruiter_signals")
            if not isinstance(recruiter_signals, dict):
                stats["missing_recruiter_signals"] += 1

            if _is_missing_string(profile.get("schema_version")):
                stats["missing_schema_version"] += 1

            if not is_schema_valid(profile):
                stats["schema_failures"] += 1

    stats["duplicate_ids"] = len(duplicate_ids)
    return stats


def _overall_status(stats: dict) -> str:
    failure_keys = (
        "invalid_json_rows",
        "missing_candidate_id",
        "missing_profile_text",
        "empty_skills",
        "duplicate_ids",
        "missing_recruiter_signals",
        "missing_schema_version",
        "schema_failures",
    )
    if any(stats[key] > 0 for key in failure_keys):
        return "FAIL"
    return "PASS"


def print_report(stats: dict) -> None:
    print("=" * 50)
    print("Validation Report")
    print("=" * 50)
    print(f"Total Profiles: {stats['total_profiles']}")
    print(f"Invalid JSON Rows: {stats['invalid_json_rows']}")
    print(f"Missing candidate_id: {stats['missing_candidate_id']}")
    print(f"Missing profile_text: {stats['missing_profile_text']}")
    print(f"Empty skills: {stats['empty_skills']}")
    print(f"Duplicate IDs: {stats['duplicate_ids']}")
    print(f"Missing recruiter_signals: {stats['missing_recruiter_signals']}")
    print(f"Missing schema_version: {stats['missing_schema_version']}")
    print(f"Schema Failures: {stats['schema_failures']}")
    print(f"Overall Status: {_overall_status(stats)}")
    print("=" * 50)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate structured_candidates.jsonl before Member-2/Member-3 handoff.",
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
        help="Path to structured_candidates.jsonl",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA,
        help="Path to structured_candidate_schema.json",
    )
    args = parser.parse_args(argv)

    if not args.dataset.is_file():
        print(f"Dataset not found: {args.dataset}", file=sys.stderr)
        return 1
    if not args.schema.is_file():
        print(f"Schema not found: {args.schema}", file=sys.stderr)
        return 1

    stats = validate_profiles(args.dataset, args.schema)
    print_report(stats)
    return 0 if _overall_status(stats) == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
