from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DATASET_ROOT = Path(__file__).resolve().parents[2] / "datasets"


class DatasetIngestionError(Exception):
    """Raised when dataset ingestion cannot proceed."""


class MalformedRecordError(DatasetIngestionError):
    """Raised when a JSONL line cannot be parsed or validated."""


def resolve_dataset_path(dataset_path: str) -> Path:
    if not dataset_path or not dataset_path.strip():
        raise DatasetIngestionError("dataset_path is required")

    path = Path(dataset_path.strip())
    if not path.is_absolute():
        path = (PROJECT_ROOT / path).resolve()
    else:
        path = path.resolve()

    allowed_roots = [
        DATASET_ROOT.resolve(),
        (PROJECT_ROOT / "backend" / "app" / "datasets").resolve(),
    ]
    if not any(_is_under_root(path, root) for root in allowed_roots):
        raise DatasetIngestionError(
            "dataset_path must be located under backend/app/datasets"
        )

    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")
    if not path.is_file():
        raise DatasetIngestionError(f"dataset_path is not a file: {path}")
    if path.suffix.lower() != ".jsonl":
        raise DatasetIngestionError("dataset_path must point to a .jsonl file")

    return path


def _is_under_root(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def stream_jsonl_records(
    dataset_path: str | Path,
    *,
    limit: int | None = None,
    errors: list[str] | None = None,
) -> Iterator[dict[str, Any]]:
    """
    Stream JSONL records line-by-line without loading the full file into memory.

    Yields parsed dicts for each valid record. Stops after `limit` records when set.
    Malformed lines are collected in `errors` when provided; otherwise ingestion aborts.
    """
    path = dataset_path if isinstance(dataset_path, Path) else resolve_dataset_path(dataset_path)
    yielded = 0

    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            if limit is not None and yielded >= limit:
                return

            line = raw_line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                message = f"Malformed JSON on line {line_number}: {exc.msg}"
                if errors is not None:
                    errors.append(message)
                    continue
                raise MalformedRecordError(message) from exc

            if not isinstance(record, dict):
                message = f"Line {line_number}: each JSONL record must be a JSON object"
                if errors is not None:
                    errors.append(message)
                    continue
                raise MalformedRecordError(message)

            yielded += 1
            yield record
