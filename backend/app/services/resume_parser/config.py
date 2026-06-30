"""
Central configuration and path resolution for the resume parsing module.

All paths are resolved relative to the project root (TalentGraph/) so the
module works regardless of the current working directory it is invoked
from. Nothing here is a "skill" or a "section name" -- it is purely
filesystem wiring.
"""

from __future__ import annotations

from pathlib import Path

# backend/app/services/resume_parser/config.py -> backend/app/
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

CONFIG_DIR: Path = BASE_DIR / "configs"
DATASET_DIR: Path = BASE_DIR / "datasets"

SECTION_ALIASES_PATH: Path = CONFIG_DIR / "section_aliases.json"
SKILLS_MASTER_PATH: Path = DATASET_DIR / "skills_master.csv"
SKILLS_ALIASES_PATH: Path = DATASET_DIR / "skills_aliases.csv"

# Maximum number of evidence lines retained per detected skill.
MAX_EVIDENCE_LINES: int = 3