"""
Comprehensive validation script to test all improvements to the skill extractor.
Tests all new features: validation layer, ignore patterns, confidence scoring.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from skill_extractor import (
    is_valid_skill,
    filter_valid_skills,
    add_confidence_scores,
    merge_wrapped_lines,
    normalize_skill,
    extract_section_by_aliases,
    IGNORE_PATTERNS,
)


# =====================================================
# TEST 1: Validation Function
# =====================================================

def test_is_valid_skill():
    """Test the is_valid_skill validation function."""
    print("\n" + "="*60)
    print("TEST 1: Validation Function (is_valid_skill)")
    print("="*60)
    
    # Should be valid
    valid_cases = [
        ("Python", True),
        ("JavaScript", True),
        ("Machine Learning", True),
        ("AWS", True),
    ]
    
    # Should be invalid
    invalid_cases = [
        ("", False, "empty"),
        ("a", False, "too short"),
        ("a" * 100, False, "too long"),
        ("Bachelor of Engineering", False, "education keyword"),
        ("Arizona State University", False, "university keyword"),
        ("123456", False, "mostly numeric"),
        ("University of Computer Science", False, "contains university"),
        ("GPA 3.5", False, "contains gpa"),
        ("This is a very long phrase with way too many words in it", False, "too many words"),
    ]
    
    passed = 0
    failed = 0
    
    for skill, expected_valid in valid_cases:
        is_valid, reason = is_valid_skill(skill)
        if is_valid == expected_valid:
            print(f"[OK] '{skill}' -> VALID (expected)")
            passed += 1
        else:
            print(f"[FAIL] '{skill}' -> {is_valid} (expected {expected_valid})")
            failed += 1
    
    for skill, expected_valid, reason_hint in invalid_cases:
        is_valid, reason = is_valid_skill(skill)
        if is_valid == expected_valid:
            print(f"[OK] '{skill}' -> INVALID: {reason}")
            passed += 1
        else:
            print(f"[FAIL] '{skill}' -> {is_valid} (expected {expected_valid})")
            failed += 1
    
    print(f"\nResult: {passed} passed, {failed} failed")
    return failed == 0


# =====================================================
# TEST 2: Ignore Patterns
# =====================================================

def test_ignore_patterns():
    """Test that ignore patterns work correctly."""
    print("\n" + "="*60)
    print("TEST 2: Ignore Patterns")
    print("="*60)
    
    test_skills = [
        "Business Management Arizona State University City",
        "Bachelor of Engineering",
        "Model Training",
        "Python Programming",
        "College of Engineering",
        "Email Processing",
        "Machine Learning",
    ]
    
    print("\nIgnore patterns configured:")
    for pattern in IGNORE_PATTERNS[:7]:  # Show first 7
        print(f"  - {pattern}")
    
    passed = 0
    failed = 0
    
    for skill in test_skills:
        is_valid, reason = is_valid_skill(skill)
        status = "VALID" if is_valid else f"DISCARDED ({reason})"
        print(f"  '{skill}' -> {status}")
        
        # Skills with education keywords should be invalid
        if any(keyword in skill.lower() for keyword in ["bachelor", "university", "college", "email"]):
            if not is_valid:
                passed += 1
            else:
                failed += 1
        else:
            if is_valid:
                passed += 1
            else:
                failed += 1
    
    print(f"\nResult: {passed} correct, {failed} incorrect")
    return failed == 0


# =====================================================
# TEST 3: Multiline Merging
# =====================================================

def test_multiline_merging():
    """Test multiline skill merging."""
    print("\n" + "="*60)
    print("TEST 3: Multiline Skill Merging")
    print("="*60)
    
    test_cases = [
        (
            "AI/ML: Computer Vision, YOLOv8, Model Training &\nOptimization\nDatabase: MySQL",
            ["AI/ML: Computer Vision, YOLOv8, Model Training & Optimization", "Database: MySQL"],
            "Ampersand continuation"
        ),
        (
            "Frontend: React, Vue, Angular",
            ["Frontend: React, Vue, Angular"],
            "Single-line skills (no wrapping needed)"
        ),
    ]
    
    passed = 0
    failed = 0
    
    for input_text, expected_output, description in test_cases:
        result = merge_wrapped_lines(input_text)
        print(f"\n  Test: {description}")
        print(f"    Input: {repr(input_text[:50])}...")
        print(f"    Output: {result}")
        
        # Check if result contains expected content
        matches = all(
            any(exp in line for line in result)
            for exp in expected_output
        )
        
        if matches:
            print(f"    [OK] PASSED")
            passed += 1
        else:
            print(f"    [FAIL] Expected content not found")
            failed += 1
    
    print(f"\nResult: {passed} passed, {failed} failed")
    return failed == 0


# =====================================================
# TEST 4: Filter Valid Skills
# =====================================================

def test_filter_valid_skills():
    """Test the filter_valid_skills function."""
    print("\n" + "="*60)
    print("TEST 4: Filter Valid Skills (Post-processing)")
    print("="*60)
    
    skill_results = [
        {"skill": "Python", "frequency": 5, "sections": ["skills"], "evidence": []},
        {"skill": "Bachelor of Science", "frequency": 1, "sections": ["education"], "evidence": []},
        {"skill": "JavaScript", "frequency": 3, "sections": ["projects"], "evidence": []},
        {"skill": "Arizona State University", "frequency": 1, "sections": ["education"], "evidence": []},
        {"skill": "Machine Learning", "frequency": 2, "sections": ["experience"], "evidence": []},
    ]
    
    print("\nFiltering skills...")
    filtered = filter_valid_skills(skill_results)
    
    expected_valid = ["Python", "JavaScript", "Machine Learning"]
    valid_skills = [s["skill"] for s in filtered]
    
    passed = len([s for s in valid_skills if s in expected_valid])
    failed = len([s for s in valid_skills if s not in expected_valid])
    
    print(f"\nResult: {len(filtered)}/{len(skill_results)} skills passed validation")
    print(f"Valid skills retained: {valid_skills}")
    
    return failed == 0


# =====================================================
# TEST 5: Confidence Scoring
# =====================================================

def test_confidence_scoring():
    """Test confidence scoring functionality."""
    print("\n" + "="*60)
    print("TEST 5: Confidence Scoring")
    print("="*60)
    
    skill_results = [
        {
            "skill": "Python",
            "frequency": 5,
            "sections": ["skills"],
            "evidence": ["Python, JavaScript, Java"],
            "confidence": None,
        },
        {
            "skill": "JavaScript",
            "frequency": 3,
            "sections": ["projects", "experience"],
            "evidence": ["Used JavaScript in project"],
            "confidence": None,
        },
        {
            "skill": "AWS",
            "frequency": 2,
            "sections": ["experience"],
            "evidence": ["AWS deployment experience"],
            "confidence": None,
        },
        {
            "skill": "Kubernetes",
            "frequency": 1,
            "sections": ["projects", "database_scan"],
            "evidence": ["Kubernetes deployment"],
            "confidence": None,
        },
    ]
    
    print("\nAssigning confidence scores...")
    with_scores = add_confidence_scores(skill_results)
    
    passed = 0
    failed = 0
    
    for skill in with_scores:
        expected_confidence = {
            "Python": "High",
            "JavaScript": "Medium",
            "AWS": "Medium",
            "Kubernetes": "Medium",
        }
        
        actual = skill.get("confidence")
        expected = expected_confidence.get(skill["skill"])
        
        if actual == expected:
            print(f"  [OK] {skill['skill']}: {actual} (from {skill['sections']})")
            passed += 1
        else:
            print(f"  [FAIL] {skill['skill']}: {actual} (expected {expected})")
            failed += 1
    
    print(f"\nResult: {passed} correct, {failed} incorrect")
    return failed == 0


# =====================================================
# TEST 6: API Backward Compatibility
# =====================================================

def test_api_backward_compatibility():
    """Test that existing APIs still work."""
    print("\n" + "="*60)
    print("TEST 6: API Backward Compatibility")
    print("="*60)
    
    passed = 0
    failed = 0
    
    # Test normalize_skill
    try:
        aliases = {"tf": "TensorFlow", "pytorch": "PyTorch"}
        result = normalize_skill("tensorflow", aliases)
        assert isinstance(result, str)
        print(f"  [OK] normalize_skill works: 'tensorflow' -> '{result}'")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] normalize_skill failed: {e}")
        failed += 1
    
    # Test merge_wrapped_lines
    try:
        block = "Skills: Python, Java,\nJavaScript"
        result = merge_wrapped_lines(block)
        assert isinstance(result, list)
        print(f"  [OK] merge_wrapped_lines works: returns list with {len(result)} items")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] merge_wrapped_lines failed: {e}")
        failed += 1
    
    # Test extract_section_by_aliases
    try:
        text = "SKILLS\nPython, Java\n\nEXPERIENCE\nSoftware Engineer"
        result = extract_section_by_aliases(text, ["SKILLS", "Technical Skills"])
        assert isinstance(result, str)
        print(f"  [OK] extract_section_by_aliases works: extracted '{result[:30]}...'")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] extract_section_by_aliases failed: {e}")
        failed += 1
    
    print(f"\nResult: {passed} passed, {failed} failed")
    return failed == 0


# =====================================================
# RUN ALL TESTS
# =====================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("RESUME SKILL EXTRACTOR - IMPROVEMENTS VALIDATION")
    print("="*60)
    
    tests = [
        test_is_valid_skill,
        test_ignore_patterns,
        test_multiline_merging,
        test_filter_valid_skills,
        test_confidence_scoring,
        test_api_backward_compatibility,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append((test_func.__name__, result))
        except Exception as e:
            print(f"\n[ERROR] TEST FAILED WITH EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_func.__name__, False))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, r in results if r)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n>>> ALL TESTS PASSED - Implementation successful!")
        sys.exit(0)
    else:
        print(f"\n>>> {total_tests - total_passed} tests failed")
        sys.exit(1)
