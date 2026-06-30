

from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional
from pathlib import Path
from rapidfuzz import fuzz, process
import pandas as pd

# =====================================================
# TYPE ALIASES (for readability)
# =====================================================

SkillMatch = Dict[str, object]   # {"skill": str, "section": str, "evidence": List[str], "count": Optional[int]}
SkillResult = Dict[str, object]  # {"skill": str, "frequency": int, "sections": List[str], "evidence": List[str]}
AliasMap = Dict[str, str]        # {"tensorflow": "TensorFlow", ...}
SectionAliasMap = Dict[str, List[str]]  # {"skills": ["SKILLS", "TECHNICAL SKILLS", ...], ...}


# =====================================================
# PATHS
# =====================================================

from backend.app.services.resume_parser.config import (
    SECTION_ALIASES_PATH,
    SKILLS_ALIASES_PATH as DEFAULT_SKILLS_ALIASES_PATH,
)


# =====================================================
# CONFIG / DATA LOADERS
# =====================================================

def load_section_aliases(path: Path = SECTION_ALIASES_PATH) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Section aliases config not found at: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_skills_database(csv_path: Path | str) -> List[str]:

    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Skills database not found at: {csv_path}")

    df = pd.read_csv(csv_path)

    if "skill" not in df.columns:
        raise ValueError(f"{csv_path} must contain a column named 'skill'")

    return df["skill"].dropna().astype(str).tolist()


def load_skill_aliases(path: Path = DEFAULT_SKILLS_ALIASES_PATH) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Skill aliases file not found at: {path}")
    df = pd.read_csv(path)
    aliases = {}
    for _, row in df.iterrows():
        alias_key = str(row["alias"]).strip().lower()
        canonical_value = str(row["canonical_skill"]).strip()
        if alias_key and canonical_value:
            aliases[alias_key] = canonical_value
    return aliases

# =====================================================
# NORMALIZATION
# =====================================================

def normalize_skill(skill: str, aliases: AliasMap) -> str:
   
    cleaned = skill.strip().rstrip(".,;:")
    if not cleaned:
        return cleaned

    key = cleaned.lower()
    return aliases.get(key, cleaned)


# =====================================================
# SECTION DETECTION
# =====================================================

def _extract_section_by_heading(text: str, heading: str) -> str:
   
    # Some resumes use inline section headings separated by large spacing, e.g.
    # "... College         Skills     Accounting, ..."
    # To keep the strict start-of-line rule while supporting that formatting,
    # we normalize such inline headings into line-start headings *only when*
    # the heading is surrounded by large whitespace and NOT followed by a comma
    # (to avoid matching "USA Skills, ...").
    inline_heading_re = rf"(?im)(?<!\n)[ \t]{{2,}}(?i:{heading})\b(?=[ \t]{{2,}}|[ \t]*[:\-])"
    text = re.sub(inline_heading_re, lambda m: "\n" + m.group(0).lstrip(), text)

    # Match only real section headings on their own line to avoid false positives like
    # "... USA Skills, Microsoft Office ..." where "Skills" appears mid-sentence.
    # We keep this strict to prevent section-leakage (especially Education -> Skills).
    # Support common resume formats:
    # - "SKILLS\nPython, Java"
    # - "Skills:\nPython, Java"
    # - "Skills     Python, Java"  (inline heading with multiple spaces)
    # Keep start-of-line requirement and DO NOT match "Skills, ..." (comma immediately after heading).
    heading_pattern = (
        rf"(?im)(?:^|\n)\s*(?i:{heading})\b"
        rf"(?!\s*,)"  # block "Skills, Microsoft Office..." cases
        rf"[ \t]*[:\-]?[ \t]*"
        rf"(?:\r?\n|[ \t]{{2,}})"
    )
    body_pattern = r"(.*?)"
    next_heading_lookahead = r"(?=\n[A-Z][A-Z\s/&-]{3,}\n|\Z)"

    pattern = heading_pattern + body_pattern + next_heading_lookahead
    match = re.search(pattern, text, re.DOTALL)

    if os.getenv("TG_DEBUG_SECTIONS") == "1":
        found = bool(match)
        snippet = ""
        if match:
            body = match.group(1) or ""
            snippet = body[:120].replace("\n", "\\n")
        print(f"[TG_DEBUG] heading={heading!r} found={found} pattern={pattern!r} body_snip={snippet!r}")

    return match.group(1).strip() if match else ""


def extract_section_by_aliases(text: str, heading_variations: List[str]) -> str:
    
    if os.getenv("TG_DEBUG_SECTIONS") == "1":
        print(f"[TG_DEBUG] extract_section_by_aliases variations={heading_variations!r}")

    for heading in heading_variations:
        section_text = _extract_section_by_heading(text, re.escape(heading))
        if section_text:
            if os.getenv("TG_DEBUG_SECTIONS") == "1":
                print(f"[TG_DEBUG] matched_heading={heading!r} extracted_len={len(section_text)} first500={section_text[:500]!r}")
            return section_text
    return ""


def detect_all_sections(text: str, section_aliases: SectionAliasMap) -> Dict[str, str]:
   
    sections: Dict[str, str] = {}
    for canonical_name, variations in section_aliases.items():
        section_text = extract_section_by_aliases(text, variations)
        if section_text:
            sections[canonical_name] = section_text
    return sections


# =====================================================
# EVIDENCE EXTRACTION
# =====================================================

def get_evidence(text: str, skill: str, max_examples: int = 3) -> List[str]:
   
    evidence: List[str] = []
    chunks = re.split(r"\n|•|\uf0b7", text)

    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        if re.search(rf"\b{re.escape(skill)}\b", chunk, re.IGNORECASE):
            if chunk not in evidence:
                evidence.append(chunk)
        if len(evidence) >= max_examples:
            break

    return evidence[:max_examples]


# =====================================================
# SKILLS-SECTION PARSER
# (handles "Category: skill1, skill2, skill3" style lines, including
#  lines that wrap across multiple physical lines in the PDF text)
# =====================================================

def _merge_wrapped_lines(skills_block: str) -> List[str]:
    
    # Collapse blank lines first
    skills_block = re.sub(r"\n+", "\n", skills_block)

    raw_lines = [line.strip() for line in skills_block.split("\n") if line.strip()]

    merged_lines: List[str] = []
    current = ""

    for line in raw_lines:
        if ":" in line:
            # Starts a new category -> flush whatever we were building
            if current:
                merged_lines.append(current)
            current = line
        else:
            # Continuation of the previous category line (wrapped text)
            if current.rstrip().endswith("&"):
                current = current.rstrip() + " " + line
            else:
                current = current.rstrip(",") + ", " + line

    if current:
        merged_lines.append(current)

    return merged_lines


def _split_skills_text_preserving_parentheses(skills_text: str) -> List[str]:
    """
    Split a comma-separated skills string, but do NOT split on commas inside parentheses.
    Example: "Microsoft Office (Word, Excel), ADP" -> ["Microsoft Office (Word, Excel)", "ADP"]
    """
    parts: List[str] = []
    buf: List[str] = []
    depth = 0

    for ch in skills_text:
        if ch == "(":
            depth += 1
            buf.append(ch)
            continue
        if ch == ")":
            depth = max(0, depth - 1)
            buf.append(ch)
            continue
        if ch == "," and depth == 0:
            part = "".join(buf).strip()
            if part:
                parts.append(part)
            buf = []
            continue

        buf.append(ch)

    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)

    return parts


def extract_skills_from_section(text: str, aliases: AliasMap, section_aliases: SectionAliasMap) -> List[SkillMatch]:
    
    skills_block = extract_section_by_aliases(text, section_aliases.get("skills", ["SKILLS"]))
    if not skills_block:
        if os.getenv("TG_DEBUG_SECTIONS") == "1":
            print("[TG_DEBUG] skills_block empty -> no skills extracted from section parser")
        return []

    merged_lines = _merge_wrapped_lines(skills_block)

    results: List[SkillMatch] = []
    for line in merged_lines:
        if ":" not in line:
            continue

        _, skills_text = line.split(":", 1)

        parts = _split_skills_text_preserving_parentheses(skills_text)
        if os.getenv("TG_DEBUG_SECTIONS") == "1":
            print(f"[TG_DEBUG] skills_line={line!r}")
            print(f"[TG_DEBUG] split_parts_count={len(parts)} split_parts_first20={parts[:20]!r}")

        for raw_skill in parts:
            skill = normalize_skill(raw_skill, aliases)
            if not skill:
                continue

            is_valid, _ = is_valid_skill(skill)
            if not is_valid:
                if os.getenv("TG_DEBUG_SECTIONS") == "1":
                    ok, reason = is_valid_skill(skill)
                    print(f"[TG_DEBUG] filtered_out skill={skill!r} reason={reason!r}")
                continue

            results.append({
                "skill": skill,
                "section": "skills",
                "evidence": [line],
            })

    return results


# =====================================================
# DATABASE-DRIVEN SCAN (for non-SKILLS sections, e.g. projects/experience)
# =====================================================

# NEW: Generate skill candidates from section text before validation
# Chunks text into smaller, searchable units instead of scanning full paragraphs
def _extract_candidates_from_section(section_text: str, max_line_length: int = 150) -> List[str]:
    """
    Extract candidate phrases from section text for skill matching.
    Splits text into logical chunks at newlines, avoiding long paragraphs.
    
    Args:
        section_text: Text from a resume section
        max_line_length: Skip lines longer than this (likely descriptions)
    
    Returns:
        List of candidate phrases to search for skills
    """
    if not section_text:
        return []
    
    candidates = []
    
    # Split on newlines first (project/role boundaries)
    lines = section_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # NEW: Skip very long lines (likely full job descriptions/paragraphs)
        # These cause excessive discarded logs without improving precision
        if len(line) > max_line_length:
            continue
        
        # Skip section-header-only lines (e.g. "EXPERIENCE", "PROJECTS")
        if line.lower().strip() in SECTION_HEADERS:
            continue

        # NEW: For bullets or dashes, this is likely a skill/tech line
        if line.startswith('-') or line.startswith('•') or line.startswith('*'):
            candidates.append(line.lstrip('-•* ').strip())
        else:
            # For non-bulleted lines, add if not too long
            candidates.append(line)
    
    return candidates


def extract_skills_from_database(
    text: str,
    skills_db: List[str],
    aliases: AliasMap,
    section_aliases: SectionAliasMap,
    sections_to_scan: Optional[List[str]] = None,
) -> List[SkillMatch]:
    
    if sections_to_scan is None:
        # NEW: Explicit priority ordering - Projects before Experience
        sections_to_scan = ["projects", "experience"]

    found: List[SkillMatch] = []

    # NEW: Scan in priority order, skip education section explicitly
    for section_name in sections_to_scan:
        if section_name not in section_aliases:
            continue
        
        section_text = extract_section_by_aliases(text, section_aliases.get(section_name, []))
        if not section_text:
            continue

        # NEW: Generate better candidates instead of scanning full text
        # This reduces false positives from long paragraphs
        candidates = _extract_candidates_from_section(section_text)
        
        for skill in skills_db:
            normalized_skill = normalize_skill(skill, aliases)
            pattern = r"\b" + re.escape(skill.lower()) + r"\b"
            
            # Count matches across candidates instead of full section text
            # This provides better evidence granularity
            count = 0
            evidence_lines = []
            
            for candidate in candidates:
                matches = re.findall(pattern, candidate.lower())
                if matches:
                    count += len(matches)
                    evidence_lines.append(candidate)
            
            if count > 0:
                # NEW: Use candidate-specific evidence instead of section evidence
                # Keeps log output focused on actual skill context
                found.append({
                    "skill": normalized_skill,
                    "section": section_name,
                    "count": count,
                    "evidence": evidence_lines[:3],  # Cap at 3 examples
                })

    return found


# =====================================================
# MERGE / DEDUPLICATE
# =====================================================

def merge_skills(
    section_skills: List[SkillMatch],
    database_skills: List[SkillMatch],
    aliases: AliasMap,
) -> List[SkillResult]:
    
    merged: Dict[str, SkillResult] = defaultdict(lambda: {
        "skill": "",
        "frequency": 0,
        "sections": set(),
        "evidence": [],
    })

    for item in section_skills + database_skills:
        skill = normalize_skill(str(item["skill"]), aliases)
        key = skill.lower()

        merged[key]["skill"] = skill
        merged[key]["frequency"] += item.get("count", 1)
        merged[key]["sections"].add(item["section"])

        for ev in item["evidence"]:
            if ev not in merged[key]["evidence"]:
                merged[key]["evidence"].append(ev)

    # Resolve "C" vs "C/C++" overlap: if both exist, "C" is almost always
    # a false-positive substring match of "C/C++" and should be dropped.
    if "c/c++" in merged and "c" in merged:
        del merged["c"]

    final: List[SkillResult] = []
    for value in merged.values():
        final.append({
            "skill": value["skill"],
            "frequency": value["frequency"],
            "sections": sorted(value["sections"]),
            "evidence": value["evidence"][:3],
        })

    return sorted(final, key=lambda x: str(x["skill"]).lower())


# =====================================================
# VALIDATION & FILTERING
# =====================================================

# NEW: Configurable ignore keywords to filter education/location/personal-info phrases
IGNORE_PATTERNS: List[str] = [
    "university", "college", "school", "bachelor", "master", "education",
    "gpa", "campus", "city", "state", "address", "email", "institute",
    "degree", "cgpa",
]

# NEW: Section headers that should never be extracted as skills
SECTION_HEADERS: set = {
    "skills",
    "experience",
    "projects",
    "education",
    "summary",
    "certifications",
    "technical skills",
    "professional experience",
    "work experience",
    "core competencies",
}

# NEW: Action words that indicate sentence fragments (not standalone skills)
ACTION_WORDS: set = {
    "built",
    "developed",
    "implemented",
    "created",
    "designed",
    "deployed",
    "worked",
    "using",
    "managed",
    "led",
    "worked",
}

# NEW: Common junction words that shouldn't start skills
JUNCTION_WORDS: set = {
    "and",
    "or",
    "but",
    "also",
    "as",
    "with",
}


# NEW: Validation function to reject low-quality skill strings
def is_valid_skill(
    skill: str,
    ignore_patterns: List[str] = IGNORE_PATTERNS,
    known_skills: Optional[List[str]] = None,
) -> tuple:
    """
    Validates if a skill string should be kept or rejected.
    
    Args:
        skill: Skill string to validate
        ignore_patterns: Keywords to reject
        known_skills: List of valid skills (for multi-word validation)
    
    Returns:
        (is_valid: bool, reason: str or None)
    """
    cleaned = skill.strip().strip(".,;:-_*•")
    
    # Remove content inside parentheses for simple qualifiers like "(Java)",
    # but preserve parenthesized lists like "Microsoft Office (Word, Excel, ...)".
    paren_content = re.findall(r"\(([^)]*)\)", cleaned)
    has_parenthesized_list = bool(paren_content and any("," in p for p in paren_content))
    if paren_content and not has_parenthesized_list:
        cleaned = re.sub(r"\([^)]*\)", "", cleaned).strip()

    if not cleaned:
        return False, "empty after cleaning"
    if len(cleaned) < 2:
        return False, "too short (<2 chars)"
    if len(cleaned) > 80:
        return False, "too long (>80 chars)"

    lower = cleaned.lower()
    
    # Reject common PII / contact fragments
    if lower.startswith("contact"):
        return False, "contact/PII fragment"
    if lower.startswith("supervisor"):
        return False, "contact/PII fragment"
    if "supervisor's name" in lower or "supervisors name" in lower:
        return False, "contact/PII fragment"
    if re.search(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", cleaned):
        return False, "email address"
    if re.search(r"\bhttps?://\S+|\bwww\.\S+", cleaned, re.IGNORECASE):
        return False, "url"
    if re.search(r"\b(?:\+?\d{1,2}[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b", cleaned):
        return False, "phone number"

    # NEW: Reject exact section header matches
    if lower in SECTION_HEADERS:
        return False, "is a section header"
    
    # NEW: Reject if starts with a section header (e.g., "EXPERIENCE" in longer phrase)
    for header in SECTION_HEADERS:
        if lower.startswith(header + " ") or lower.startswith(header + ","):
            return False, f"starts with section header '{header}'"
    
    # NEW: Reject if starts with junction words (and, or, but, etc.)
    first_word = lower.split()[0] if lower.split() else ""
    if first_word in JUNCTION_WORDS:
        return False, f"starts with junction word '{first_word}'"

    # Reject obvious US locations (lightweight deny-list)
    LOCATION_DENYLIST = {
        "new jersey",
        "arizona",
        "california",
        "texas",
        "florida",
        "washington",
        "illinois",
        "massachusetts",
        "colorado",
        "georgia",
        "ohio",
        "pennsylvania",
        "virginia",
        "north carolina",
        "south carolina",
        "new york",
    }
    if lower in LOCATION_DENYLIST:
        return False, "location"

    word_count = len(cleaned.split())
    
    # NEW: Check for action word + sentence fragment pattern
    # If phrase has action word AND >3 words, it's likely a sentence fragment
    words = lower.split()
    has_action_word = any(word in ACTION_WORDS for word in words)
    if has_action_word and word_count > 3:
        return False, "action word sentence fragment"

    # Reject dangling parenthesis fragments (often produced by bad splitting)
    if cleaned.count("(") != cleaned.count(")"):
        return False, "unmatched parentheses"
    
    # NEW: Reject overly long phrases (>4 words) unless in known skills database
    if word_count > 4:
        # Allow common \"suite\" patterns like \"Microsoft Office (Word, Excel, PowerPoint, Outlook)\"
        # even if they exceed the normal word limit.
        if has_parenthesized_list:
            return True, None

        # Check if this is a known multi-word skill
        is_known = False
        if known_skills:
            skill_lower = cleaned.lower()
            is_known = any(
                skill_lower == known.lower() for known in known_skills
            )
        
        if not is_known:
            return False, f"too many words ({word_count} > 4)"
    
    # Keep original check for very long strings
    if word_count > 8:
        return False, f"too many words ({word_count} > 8)"

    digit_count = sum(c.isdigit() for c in cleaned)
    if len(cleaned) > 0 and digit_count > len(cleaned) / 2:
        return False, "mostly numeric"

    for pattern in ignore_patterns:
        if pattern in lower:
            return False, f"matched ignore pattern '{pattern}'"

    return True, None


# NEW: Post-processing filter - applies validation to all extracted skills
def filter_valid_skills(
    skill_results: list,
    ignore_patterns: List[str] = IGNORE_PATTERNS,
    known_skills: Optional[List[str]] = None,
) -> list:
    """
    Filters out invalid or low-quality skills with detailed discard logging.
    
    Args:
        skill_results: List of skill results to filter
        ignore_patterns: Keywords to reject
        known_skills: Valid skills database (for multi-word skill validation)
    """
    valid_results = []
    for entry in skill_results:
        is_valid, reason = is_valid_skill(
            str(entry["skill"]), ignore_patterns, known_skills=known_skills
        )
        if is_valid:
            valid_results.append(entry)
        else:
            print(f"[DISCARDED] {entry['skill']!r} -> {reason}")
    return valid_results


# =====================================================
# SKILL CATEGORIES & CONTEXT-BASED VALIDATION
# =====================================================

# NEW: Load skill categories from database for context-aware validation
def load_skill_categories(csv_path: Path | str) -> Dict[str, str]:
    """
    Load skill-to-category mapping from the skills database.
    
    Args:
        csv_path: Path to skills CSV (must have 'skill' and 'category' columns)
    
    Returns:
        Dict mapping skill names (lowercase) to category strings
        E.g., {"python": "language", "tensorflow": "ml", "docker": "devops"}
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        return {}
    
    try:
        df = pd.read_csv(csv_path)
        if "skill" not in df.columns or "category" not in df.columns:
            return {}
        
        categories = {}
        for _, row in df.iterrows():
            skill_name = str(row["skill"]).strip().lower()
            category = str(row["category"]).strip()
            if skill_name and category:
                categories[skill_name] = category
        return categories
    except Exception:
        return {}


def get_skill_category(skill: str, skill_categories: Dict[str, str]) -> str:
    """
    Get the category for a skill.
    
    Args:
        skill: Skill name to categorize
        skill_categories: Category mapping (from load_skill_categories)
    
    Returns:
        Category string (e.g., "language", "framework", "ml") or empty string if not found
    """
    key = skill.strip().lower()
    return skill_categories.get(key, "")


# NEW: Adjust confidence based on extraction context
def adjust_confidence_by_context(
    sections: List[str],
    skill: str,
    skill_categories: Dict[str, str],
) -> str:
    """
    Adjust confidence level based on extraction context.
    
    Context Rules:
    - High confidence: Found in SKILLS or PROJECTS section (structured, expert-chosen)
    - Medium confidence: Found in EXPERIENCE section (mixed with descriptions)
    - Low confidence: Found only in EDUCATION section (often coursework, not real experience)
    
    Discount Rules:
    - Education phrases (Bachelor, Master, GPA, etc.) get lower confidence
    - Generic academic terms reduce confidence
    
    Args:
        sections: List of sections where skill was found
        skill: Skill name to validate
        skill_categories: Skill category mapping
    
    Returns:
        Adjusted confidence level: "High", "Medium", or "Low"
    """
    base_confidence = ["High", "Medium", "Low"]
    
    # Determine base level from sections
    if "skills" in sections:
        base_level = "High"
    elif "projects" in sections:
        base_level = "Medium"
    elif "experience" in sections:
        base_level = "Medium"
    elif "education" in sections:
        base_level = "Low"
    else:
        base_level = "Low"
    
    # Apply discount rules for education-related content
    skill_lower = skill.lower()
    education_keywords = ["bachelor", "master", "degree", "gpa", "coursework", "campus", "university"]
    if any(keyword in skill_lower for keyword in education_keywords):
        # Downgrade education-related skills
        return "Low"
    
    # If ONLY in education section, reduce confidence
    if sections == ["education"]:
        return "Low"
    
    return base_level


# =====================================================
# CONFIDENCE SCORING
# =====================================================

# NEW: Confidence levels based on extraction source
SECTION_CONFIDENCE: Dict[str, str] = {
    "skills": "High",
    "projects": "Medium",
    "experience": "Medium",
    "database_scan": "Low",
}


def get_confidence(sections: list) -> str:
    """Determines confidence level based on which sections contributed the skill."""
    order = ["High", "Medium", "Low"]
    levels = [SECTION_CONFIDENCE.get(s, "Low") for s in sections]
    for level in order:
        if level in levels:
            return level
    return "Low"


# NEW: Adds confidence score to each skill result
def add_confidence_scores(skill_results: list, skill_categories: Optional[Dict[str, str]] = None) -> list:
    """
    Attaches confidence level to each skill based on source section and context.
    
    Args:
        skill_results: List of skill results to score
        skill_categories: Optional skill category mapping for context-aware adjustment
    
    Returns:
        skill_results with confidence scores attached
    """
    for entry in skill_results:
        if skill_categories:
            # Use context-aware confidence adjustment if categories provided
            entry["confidence"] = adjust_confidence_by_context(
                list(entry["sections"]),
                entry["skill"],
                skill_categories
            )
        else:
            # Fall back to original behavior for backward compatibility
            entry["confidence"] = get_confidence(list(entry["sections"]))
    return skill_results


# =====================================================
# MAIN PIPELINE ENTRY POINT
# =====================================================

def extract_skills(
    text: str,
    skills_csv_path: Path | str,
    skill_aliases_path: Path | str = DEFAULT_SKILLS_ALIASES_PATH,
    section_aliases_path: Path | str = SECTION_ALIASES_PATH,
) -> List[SkillResult]:
   
    section_aliases = load_section_aliases(Path(section_aliases_path))
    skills_db = load_skills_database(skills_csv_path)
    aliases = load_skill_aliases(skill_aliases_path)
    
    # NEW: Load skill categories for context-aware validation
    skill_categories = load_skill_categories(skills_csv_path)

    # NEW: Explicit section extraction priority
    # 1. Skills section (highest confidence, structured format)
    # 2. Projects section (good for technical skills)
    # 3. Experience section (contains skills mixed with descriptions)
    # 4. Education section is explicitly NOT scanned (handled by validation layer)
    
    skills_section = extract_skills_from_section(text, aliases, section_aliases)
    
    # NEW: Explicit sections to scan in priority order
    database_scan = extract_skills_from_database(
        text, 
        skills_db, 
        aliases, 
        section_aliases, 
        sections_to_scan=["projects", "experience"]  # Explicit: skip education
    )

    merged = merge_skills(skills_section, database_scan, aliases)
    
    # NEW: validation layer - filter skills with low confidence/invalid patterns
    # Pass skills_db for multi-word skill validation
    filtered = filter_valid_skills(
        merged, ignore_patterns=IGNORE_PATTERNS, known_skills=skills_db
    )
    
    # NEW: context-aware confidence scoring with skill categories
    with_confidence = add_confidence_scores(filtered, skill_categories=skill_categories)
    
    return with_confidence

def merge_wrapped_lines(block: str) -> list:
    """
    Generic line-unwrapping for PDF-extracted section text.
    Provided as public API wrapper around _merge_wrapped_lines for backward compatibility.
    """
    return _merge_wrapped_lines(block)


def normalize_skill_fuzzy(raw_skill, aliases, canonical_skills, threshold=90):
    """
    Exact match first, fuzzy match fallback (RapidFuzz).
    Useful for typo-tolerance in skill matching.
    """
    exact = normalize_skill(raw_skill, aliases)
    if exact.lower() != raw_skill.strip().lower():
        return exact

    canonical_lower = {c.lower(): c for c in canonical_skills}
    key = exact.lower()
    if key in canonical_lower:
        return canonical_lower[key]

    choices = list(aliases.keys()) + list(canonical_lower.keys())
    if not choices:
        return exact

    result = process.extractOne(key, choices, scorer=fuzz.WRatio)
    if result and result[1] >= threshold:
        matched_text = result[0]
        return aliases.get(matched_text, canonical_lower.get(matched_text, exact))

    return exact


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    from resume_parser import extract_text_from_pdf

    resume_path = "datasets/sample_resumes/Resume.pdf"
    skills_csv = "datasets/skills_master.csv"

    text = extract_text_from_pdf(resume_path)
    # NEW: extract_skills now automatically applies filtering and confidence scoring
    skills = extract_skills(text, skills_csv)

    print("\nDetected Skills:\n")
    for skill in skills:
        print(skill)



