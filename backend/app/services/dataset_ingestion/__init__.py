"""JSONL dataset ingestion for large-scale candidate batch processing."""

from backend.app.services.dataset_ingestion.loader import (
    DatasetIngestionError,
    resolve_dataset_path,
    stream_jsonl_records,
)
from backend.app.services.dataset_ingestion.adapter import jsonl_record_to_profile
from backend.app.services.dataset_ingestion.processor import process_dataset_against_jobs, aggregate_best_candidate_matches

__all__ = [
    "DatasetIngestionError",
    "resolve_dataset_path",
    "stream_jsonl_records",
    "jsonl_record_to_profile",
    "process_dataset_against_jobs",
    "aggregate_best_candidate_matches",
]
