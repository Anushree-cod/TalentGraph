"""
Tests for skill category mapping and context-based validation.

Validates that:
1. Skill categories are correctly loaded and retrieved
2. Context-aware confidence adjustment works as expected
3. Backward compatibility is maintained
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from skill_extractor import (
    load_skill_categories,
    get_skill_category,
    adjust_confidence_by_context,
    add_confidence_scores,
    extract_skills,
)


def test_load_skill_categories():
    """Test that skill categories are correctly loaded from database."""
    print("\n" + "="*70)
    print("TEST 1: Load Skill Categories")
    print("="*70)
    
    # Load from actual skills database
    skills_csv = Path(__file__).resolve().parent.parent.parent.parent / "datasets" / "skills_master.csv"
    
    categories = load_skill_categories(skills_csv)
    
    print(f"\nLoaded {len(categories)} skill categories")
    
    # Verify some known categories
    assert len(categories) > 0, "Should load at least some categories"
    assert "python" in categories, "Should have Python in categories"
    assert "tensorflow" in categories, "Should have TensorFlow in categories"
    
    print("Sample categories:")
    samples = list(categories.items())[:5]
    for skill, category in samples:
        print(f"  {skill:20s} -> {category}")
    
    print("\n[OK] Skill categories loaded successfully")
    return True


def test_get_skill_category():
    """Test that individual skill categories can be retrieved."""
    print("\n" + "="*70)
    print("TEST 2: Get Individual Skill Category")
    print("="*70)
    
    skills_csv = Path(__file__).resolve().parent.parent.parent.parent / "datasets" / "skills_master.csv"
    categories = load_skill_categories(skills_csv)
    
    # Test retrieval of known skills - check what's actually in the database
    # Use skills that are definitely in the database
    test_cases = [
        ("python", "language"),
        ("tensorflow", "ml"),
        ("docker", "devops"),
        ("react", "framework"),
    ]
    
    print("\nTesting category retrieval:")
    for skill_input, expected_category in test_cases:
        # Convert to lowercase for lookup since categories are stored in lowercase
        category = get_skill_category(skill_input.lower(), categories)
        match = "[OK]" if category == expected_category else "[FAIL]"
        print(f"  {match} {skill_input:15s} -> {category:10s} (expected: {expected_category})")
        assert category == expected_category, f"{skill_input} should be {expected_category}, got {category}"
    
    print("\n[OK] All skill categories retrieved correctly")
    return True


def test_context_aware_confidence_skills_section():
    """Test that skills from SKILLS section get HIGH confidence."""
    print("\n" + "="*70)
    print("TEST 3: Context-Aware Confidence - SKILLS Section (HIGH)")
    print("="*70)
    
    skills_csv = Path(__file__).resolve().parent.parent.parent.parent / "datasets" / "skills_master.csv"
    categories = load_skill_categories(skills_csv)
    
    # Skills found in SKILLS section should have HIGH confidence
    sections = ["skills"]
    skill = "Python"
    
    confidence = adjust_confidence_by_context(sections, skill, categories)
    
    print(f"\nSkill '{skill}' found in sections: {sections}")
    print(f"Adjusted confidence: {confidence}")
    
    assert confidence == "High", f"Skills in SKILLS section should be High, got {confidence}"
    
    print("\n[OK] SKILLS section correctly rated as HIGH confidence")
    return True


def test_context_aware_confidence_projects_section():
    """Test that skills from PROJECTS section get MEDIUM confidence."""
    print("\n" + "="*70)
    print("TEST 4: Context-Aware Confidence - PROJECTS Section (MEDIUM)")
    print("="*70)
    
    skills_csv = Path(__file__).resolve().parent.parent.parent.parent / "datasets" / "skills_master.csv"
    categories = load_skill_categories(skills_csv)
    
    sections = ["projects"]
    skill = "Docker"
    
    confidence = adjust_confidence_by_context(sections, skill, categories)
    
    print(f"\nSkill '{skill}' found in sections: {sections}")
    print(f"Adjusted confidence: {confidence}")
    
    assert confidence == "Medium", f"Skills in PROJECTS section should be Medium, got {confidence}"
    
    print("\n[OK] PROJECTS section correctly rated as MEDIUM confidence")
    return True


def test_context_aware_confidence_education_section():
    """Test that skills ONLY in EDUCATION section get LOW confidence."""
    print("\n" + "="*70)
    print("TEST 5: Context-Aware Confidence - EDUCATION Section (LOW)")
    print("="*70)
    
    skills_csv = Path(__file__).resolve().parent.parent.parent.parent / "datasets" / "skills_master.csv"
    categories = load_skill_categories(skills_csv)
    
    sections = ["education"]
    skill = "Python"
    
    confidence = adjust_confidence_by_context(sections, skill, categories)
    
    print(f"\nSkill '{skill}' found ONLY in sections: {sections}")
    print(f"Adjusted confidence: {confidence}")
    
    assert confidence == "Low", f"Skills only in EDUCATION should be Low, got {confidence}"
    
    print("\n[OK] EDUCATION section correctly rated as LOW confidence")
    return True


def test_context_aware_confidence_education_keywords():
    """Test that education-related keywords get LOW confidence regardless of section."""
    print("\n" + "="*70)
    print("TEST 6: Context-Aware Confidence - Education Keywords (LOW)")
    print("="*70)
    
    skills_csv = Path(__file__).resolve().parent.parent.parent.parent / "datasets" / "skills_master.csv"
    categories = load_skill_categories(skills_csv)
    
    test_cases = [
        ("Bachelor of Science", "experience"),
        ("Master's Degree", "skills"),
        ("GPA Calculator", "projects"),
    ]
    
    print("\nTesting education keyword detection:")
    for skill, section in test_cases:
        confidence = adjust_confidence_by_context([section], skill, categories)
        print(f"  {skill:20s} in {section:15s} -> {confidence}")
        assert confidence == "Low", f"Education keywords should always be Low: {skill}"
    
    print("\n[OK] Education keywords correctly downgraded to LOW confidence")
    return True


def test_add_confidence_scores_with_categories():
    """Test that add_confidence_scores uses context-aware adjustment when categories provided."""
    print("\n" + "="*70)
    print("TEST 7: Add Confidence Scores with Categories")
    print("="*70)
    
    skills_csv = Path(__file__).resolve().parent.parent.parent.parent / "datasets" / "skills_master.csv"
    categories = load_skill_categories(skills_csv)
    
    # Mock skill results
    skill_results = [
        {
            "skill": "Python",
            "frequency": 3,
            "sections": ["skills"],
            "evidence": ["Python, Java"]
        },
        {
            "skill": "Docker",
            "frequency": 2,
            "sections": ["experience"],
            "evidence": ["Docker containerization"]
        },
        {
            "skill": "JavaScript",
            "frequency": 1,
            "sections": ["education"],
            "evidence": ["Web Development coursework"]
        },
    ]
    
    # Add confidence scores with categories
    scored = add_confidence_scores(skill_results, skill_categories=categories)
    
    print("\nSkill confidence scores with context-aware adjustment:")
    for result in scored:
        print(f"  {result['skill']:15s} in {str(result['sections']):30s} -> {result['confidence']}")
    
    # Verify confidence levels
    assert scored[0]["confidence"] == "High", "Python in SKILLS should be High"
    assert scored[1]["confidence"] == "Medium", "Docker in EXPERIENCE should be Medium"
    assert scored[2]["confidence"] == "Low", "JavaScript in EDUCATION should be Low"
    
    print("\n[OK] Confidence scores correctly adjusted by context")
    return True


def test_backward_compatibility_without_categories():
    """Test that add_confidence_scores works without skill_categories (backward compatible)."""
    print("\n" + "="*70)
    print("TEST 8: Backward Compatibility - No Categories")
    print("="*70)
    
    # Mock skill results
    skill_results = [
        {
            "skill": "Python",
            "frequency": 3,
            "sections": ["skills"],
            "evidence": ["Python, Java"]
        },
    ]
    
    # Add confidence scores WITHOUT categories (original behavior)
    scored = add_confidence_scores(skill_results)
    
    print("\nOriginal behavior without skill categories:")
    print(f"  {scored[0]['skill']:15s} -> {scored[0]['confidence']}")
    
    assert "confidence" in scored[0], "Should have confidence field"
    assert scored[0]["confidence"] == "High", "Python in SKILLS should still be High"
    
    print("\n[OK] Backward compatibility maintained")
    return True


def test_full_extraction_with_context():
    """Test full extraction pipeline with context-aware validation."""
    print("\n" + "="*70)
    print("TEST 9: Full Extraction with Context-Aware Validation")
    print("="*70)
    
    text = """
    SKILLS
    Programming Languages: Python, Java, JavaScript
    ML Frameworks: TensorFlow, PyTorch
    Tools: Docker, Kubernetes
    
    PROJECTS
    Built recommendation engine using Python and TensorFlow
    Deployed using Docker and Kubernetes
    
    EXPERIENCE
    Senior Engineer at TechCorp
    Worked with Python, SQL, and Java
    
    EDUCATION
    Bachelor of Computer Science
    GPA: 3.8
    Relevant Coursework: Data Structures (Java), Web Development (JavaScript)
    """
    
    skills_csv = Path(__file__).resolve().parent.parent.parent.parent / "datasets" / "skills_master.csv"
    
    # Extract skills with context-aware validation
    skills = extract_skills(text, str(skills_csv))
    
    print(f"\nExtracted {len(skills)} skills with context-aware confidence:")
    for skill in skills[:10]:  # Show first 10
        print(f"  {skill['skill']:20s} -> {skill['confidence']:10s} (sections: {skill['sections']})")
    
    # Verify high-confidence skills from SKILLS section exist
    high_confidence = [s for s in skills if s["confidence"] == "High"]
    print(f"\nHigh confidence skills: {len(high_confidence)}")
    
    assert len(skills) > 0, "Should extract some skills"
    assert len(high_confidence) > 0, "Should have some high-confidence skills from SKILLS section"
    
    print("\n[OK] Full extraction with context-aware validation works correctly")
    return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SKILL CATEGORY & CONTEXT-BASED VALIDATION TESTS")
    print("="*70)
    
    tests = [
        ("Load Skill Categories", test_load_skill_categories),
        ("Get Individual Category", test_get_skill_category),
        ("SKILLS Section = HIGH", test_context_aware_confidence_skills_section),
        ("PROJECTS Section = MEDIUM", test_context_aware_confidence_projects_section),
        ("EDUCATION Section = LOW", test_context_aware_confidence_education_section),
        ("Education Keywords = LOW", test_context_aware_confidence_education_keywords),
        ("Add Confidence with Categories", test_add_confidence_scores_with_categories),
        ("Backward Compatibility", test_backward_compatibility_without_categories),
        ("Full Extraction Pipeline", test_full_extraction_with_context),
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
        print("\n[OK] All skill category tests passed!")
    else:
        print(f"\n[FAIL] {total - passed} tests failed")
