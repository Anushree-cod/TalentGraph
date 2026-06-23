"""
Tests for false positive filtering and precision improvements.

Validates that section headers, action word phrases, and overly long candidates
are properly rejected while preserving valid skills and multi-word skills.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from skill_extractor import (
    is_valid_skill,
    filter_valid_skills,
    SECTION_HEADERS,
    ACTION_WORDS,
    load_skills_database,
)


def test_section_headers_rejected():
    """Test that section headers are not extracted as skills."""
    print("\n" + "="*70)
    print("TEST 1: Section Headers Rejected")
    print("="*70)
    
    # Test cases: section headers that should be rejected
    test_headers = ["SKILLS", "EXPERIENCE", "PROJECTS", "EDUCATION", "Summary"]
    
    print("\nRejecting section headers:")
    for header in test_headers:
        is_valid, reason = is_valid_skill(header)
        assert not is_valid, f"{header} should be rejected"
        print(f"  [OK] {header:20s} -> {reason}")
    
    print("\n[OK] All section headers rejected")
    return True


def test_action_word_phrases_rejected():
    """Test that action word phrases (>3 words) are rejected."""
    print("\n" + "="*70)
    print("TEST 2: Action Word Phrases Rejected")
    print("="*70)
    
    test_phrases = [
        # Must be >3 words to match current validation rule
        "Built recommendation engine using Python",
        "Deployed using Docker and Kubernetes",
        "Implemented new system for payments",
        "Created automated tests for services",
        "Developed REST APIs for clients",
        "Led the team on project",
    ]
    
    print("\nRejecting action word phrases (>3 words):")
    for phrase in test_phrases:
        is_valid, reason = is_valid_skill(phrase)
        assert not is_valid, f"{phrase} should be rejected"
        word_count = len(phrase.split())
        print(f"  [OK] {phrase:35s} ({word_count} words) -> {reason}")
    
    print("\n[OK] All action word phrases rejected")
    return True


def test_long_phrases_rejected():
    """Test that phrases >4 words are rejected."""
    print("\n" + "="*70)
    print("TEST 3: Long Phrases Rejected")
    print("="*70)
    
    test_phrases = [
        "Data Structures and Algorithms",  # 4 words -> OK
        "Very Long Phrase That Has Many Words",  # 7 words -> REJECT
        "Built using Python and TensorFlow",  # 6 words + has action word -> REJECT
    ]
    
    print("\nTesting word count threshold (>4 words):")
    
    # First: should pass (4 words, no action word)
    phrase1 = test_phrases[0]
    is_valid, reason = is_valid_skill(phrase1)
    word_count = len(phrase1.split())
    print(f"  [OK] {phrase1:35s} ({word_count} words) -> Valid: {is_valid}")
    assert is_valid, f"{phrase1} should pass (4 words allowed)"
    
    # Second: should fail (7 words)
    phrase2 = test_phrases[1]
    is_valid, reason = is_valid_skill(phrase2)
    word_count = len(phrase2.split())
    print(f"  [OK] {phrase2:35s} ({word_count} words) -> {reason}")
    assert not is_valid, f"{phrase2} should be rejected"
    
    # Third: should fail (6 words + action word)
    phrase3 = test_phrases[2]
    is_valid, reason = is_valid_skill(phrase3)
    word_count = len(phrase3.split())
    print(f"  [OK] {phrase3:35s} ({word_count} words) -> {reason}")
    assert not is_valid, f"{phrase3} should be rejected"
    
    print("\n[OK] Word count filtering works correctly")
    return True


def test_valid_skills_preserved():
    """Test that valid single and 2-3 word skills are preserved."""
    print("\n" + "="*70)
    print("TEST 4: Valid Skills Preserved")
    print("="*70)
    
    test_skills = [
        "Python",
        "Java",
        "Docker",
        "Kubernetes",
        "TensorFlow",
        "Machine Learning",
        "Deep Learning",
        "Computer Vision",
        "Data Preprocessing",
    ]
    
    print("\nPreserving valid single and multi-word skills:")
    for skill in test_skills:
        is_valid, reason = is_valid_skill(skill)
        word_count = len(skill.split())
        status = "[OK]" if is_valid else "[FAIL]"
        print(f"  {status} {skill:30s} ({word_count} words) -> Valid: {is_valid}")
        assert is_valid, f"{skill} should be valid"
    
    print("\n[OK] All valid skills preserved")
    return True


def test_false_positives_filtered():
    """Test that the false positives from the issue are filtered."""
    print("\n" + "="*70)
    print("TEST 5: False Positives Filtered")
    print("="*70)
    
    # Mock skill results (as they would come from extraction)
    false_positive_skills = [
        {"skill": "and Java", "sections": ["skills"]},
        {"skill": "Built recommendation engine using Python and TensorFlow", "sections": ["skills"]},
        {"skill": "Deployed using Docker and Kubernetes", "sections": ["skills"]},
        {"skill": "EXPERIENCE", "sections": ["skills"]},
        {"skill": "PROJECTS", "sections": ["skills"]},
    ]
    
    # Valid skills that should survive (note: "Data Structures (Java)" becomes "Data Structures" after cleaning)
    valid_skills = [
        {"skill": "Python", "sections": ["skills"]},
        {"skill": "TensorFlow", "sections": ["skills"]},
        {"skill": "Docker", "sections": ["skills"]},
        {"skill": "Kubernetes", "sections": ["skills"]},
        {"skill": "Java", "sections": ["skills"]},
        {"skill": "Data Structures (Java)", "sections": ["skills"]},  # Cleaned to "Data Structures"
    ]
    
    print("\nFiltering false positive skills:")
    for skill_result in false_positive_skills:
        skill_name = skill_result["skill"]
        is_valid, reason = is_valid_skill(skill_name)
        assert not is_valid, f"{skill_name} should be rejected"
        print(f"  [FILTERED] {skill_name:50s} -> {reason}")
    
    print("\nPreserving valid skills:")
    for skill_result in valid_skills:
        skill_name = skill_result["skill"]
        is_valid, reason = is_valid_skill(skill_name)
        assert is_valid, f"{skill_name} should be valid"
        # Show what it becomes after cleaning
        import re
        cleaned = skill_name.strip().strip(".,;:-_*•")
        cleaned = re.sub(r"\([^)]*\)", "", cleaned).strip()
        display = f"{skill_name} -> {cleaned}" if cleaned != skill_name else skill_name
        print(f"  [KEPT] {display}")
    
    # Test with filter_valid_skills function
    mixed_results = false_positive_skills + valid_skills
    filtered = filter_valid_skills(mixed_results)
    
    print(f"\nTotal input skills: {len(mixed_results)}")
    print(f"After filtering: {len(filtered)} skills")
    print(f"Discarded: {len(mixed_results) - len(filtered)} false positives")
    
    assert len(filtered) == len(valid_skills), "Should only keep valid skills"
    
    print("\n[OK] False positives correctly filtered")
    return True


def test_multiword_skills_from_database():
    """Test that known multi-word skills from database are preserved."""
    print("\n" + "="*70)
    print("TEST 6: Multi-Word Skills from Database Preserved")
    print("="*70)
    
    # Load actual skills database
    skills_csv = Path(__file__).resolve().parent.parent.parent.parent / "datasets" / "skills_master.csv"
    skills_db = load_skills_database(skills_csv)
    
    # Convert to lowercase for matching
    skills_db_lower = [s.lower() for s in skills_db]
    
    # Find some multi-word skills in the database
    multiword_skills = [s for s in skills_db if len(s.split()) > 1 and len(s.split()) <= 4][:5]
    
    print(f"\nTesting {len(multiword_skills)} multi-word skills from database:")
    for skill in multiword_skills:
        is_valid, reason = is_valid_skill(skill, known_skills=skills_db)
        word_count = len(skill.split())
        status = "[OK]" if is_valid else "[WARN]"
        print(f"  {status} {skill:35s} ({word_count} words) -> Valid: {is_valid}")
        # These should be valid since they're in the database
        assert is_valid, f"{skill} should be valid (it's in database)"
    
    print("\n[OK] Multi-word skills from database preserved")
    return True


def test_filter_valid_skills_with_database():
    """Test filter_valid_skills with known_skills parameter."""
    print("\n" + "="*70)
    print("TEST 7: Filter with Database Integration")
    print("="*70)
    
    # Load skills database
    skills_csv = Path(__file__).resolve().parent.parent.parent.parent / "datasets" / "skills_master.csv"
    skills_db = load_skills_database(skills_csv)
    
    # Mixed results: some false positives, some valid
    mixed_results = [
        {"skill": "EXPERIENCE", "sections": ["skills"]},
        {"skill": "Python", "sections": ["skills"]},
        {"skill": "Built using Docker and Kubernetes", "sections": ["skills"]},
        {"skill": "TensorFlow", "sections": ["skills"]},
        {"skill": "Machine Learning", "sections": ["skills"]},  # Multi-word, should be kept
        {"skill": "Deployed using Kubernetes in production", "sections": ["skills"]},
    ]
    
    print(f"\nFiltering {len(mixed_results)} mixed results:")
    for result in mixed_results:
        print(f"  Input: {result['skill']}")
    
    # Filter with database
    filtered = filter_valid_skills(mixed_results, known_skills=skills_db)
    
    print(f"\nFiltered results: {len(filtered)} kept, {len(mixed_results) - len(filtered)} discarded")
    for result in filtered:
        print(f"  Kept: {result['skill']}")
    
    # Verify expected results
    kept_skills = {r["skill"] for r in filtered}
    assert "Python" in kept_skills, "Python should be kept"
    assert "TensorFlow" in kept_skills, "TensorFlow should be kept"
    assert "Machine Learning" in kept_skills, "Machine Learning should be kept"
    assert "EXPERIENCE" not in kept_skills, "EXPERIENCE should be discarded"
    assert "Built using Docker and Kubernetes" not in kept_skills, "Long action phrase should be discarded"
    assert "Deployed using Kubernetes in production" not in kept_skills, "Long action phrase should be discarded"
    
    print("\n[OK] Filter with database integration works")
    return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("FALSE POSITIVE FILTERING & PRECISION TESTS")
    print("="*70)
    
    tests = [
        ("Section Headers Rejected", test_section_headers_rejected),
        ("Action Word Phrases Rejected", test_action_word_phrases_rejected),
        ("Long Phrases Rejected", test_long_phrases_rejected),
        ("Valid Skills Preserved", test_valid_skills_preserved),
        ("False Positives Filtered", test_false_positives_filtered),
        ("Multi-Word Skills Preserved", test_multiword_skills_from_database),
        ("Filter with Database", test_filter_valid_skills_with_database),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, True))
        except AssertionError as e:
            print(f"\n[FAIL] {test_name}: {e}")
            results.append((test_name, False))
        except Exception as e:
            print(f"\n[ERROR] {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[OK] All precision filtering tests passed!")
    else:
        print(f"\n[FAIL] {total - passed} tests failed")
