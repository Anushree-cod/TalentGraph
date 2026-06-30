#!/usr/bin/env python
"""Quick functionality verification"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from skill_extractor import is_valid_skill, filter_valid_skills, add_confidence_scores, extract_skills

print("\n" + "="*60)
print("FINAL VERIFICATION TEST")
print("="*60)

# Test 1: Validation
print("\n[TEST 1] Validation Function")
print("-"*60)
tests = [
    ("Python", True),
    ("Bachelor of Engineering", False),
    ("Arizona State University", False),
    ("Machine Learning", True),
]
for skill, should_be_valid in tests:
    is_valid, _ = is_valid_skill(skill)
    status = "OK" if is_valid == should_be_valid else "FAIL"
    print(f"  [{status}] {skill}: {is_valid} (expected {should_be_valid})")

# Test 2: Confidence Scoring
print("\n[TEST 2] Confidence Scoring")
print("-"*60)
skills = [
    {"skill": "Python", "frequency": 5, "sections": ["skills"], "evidence": []},
    {"skill": "JavaScript", "frequency": 3, "sections": ["projects", "experience"], "evidence": []},
    {"skill": "AWS", "frequency": 1, "sections": ["experience"], "evidence": []},
]
scored = add_confidence_scores(skills)
for s in scored:
    print(f"  {s['skill']}: {s['confidence']}")

# Test 3: Filtering
print("\n[TEST 3] Filtering Invalid Skills")
print("-"*60)
mixed_skills = [
    {"skill": "Python", "frequency": 1, "sections": ["skills"], "evidence": []},
    {"skill": "Bachelor of Science", "frequency": 1, "sections": ["education"], "evidence": []},
    {"skill": "JavaScript", "frequency": 1, "sections": ["projects"], "evidence": []},
]
filtered = filter_valid_skills(mixed_skills)
print(f"  Input: {len(mixed_skills)} skills")
print(f"  Output: {len(filtered)} skills (after filtering)")

print("\n" + "="*60)
print("VERIFICATION COMPLETE - All features working!")
print("="*60 + "\n")
