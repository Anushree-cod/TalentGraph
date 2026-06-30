import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from skill_extractor import (
    merge_wrapped_lines,
    normalize_skill,
    extract_section_by_aliases,
    is_valid_skill,
    filter_valid_skills,
    extract_skills,
)


def test_multiline_merge_technical():
    block = "AI/ML: Computer Vision, YOLOv8, Model Training &\nOptimization\nDatabase: MySQL"
    result = merge_wrapped_lines(block)
    assert "Model Training & Optimization" in result[0]
    assert result[1] == "Database: MySQL"


def test_normalize_skill_exact_alias():
    aliases = {"tensorflow": "TensorFlow"}
    assert normalize_skill("tensorflow", aliases) == "TensorFlow"


def test_normalize_skill_strips_punctuation():
    aliases = {}
    assert normalize_skill("Python.", aliases) == "Python"


def test_section_headers_not_extracted():
    for header in ("EXPERIENCE", "PROJECTS"):
        is_valid, _ = is_valid_skill(header)
        assert not is_valid, f"{header} should be rejected as a section header"


def test_sentence_fragment_not_extracted():
    phrase = "Built recommendation engine using Python and TensorFlow"
    is_valid, _ = is_valid_skill(phrase)
    assert not is_valid, "Full sentence should not be extracted as a skill"


def test_valid_skills_still_extracted():
    skills_csv = Path(__file__).resolve().parent.parent.parent.parent / "datasets" / "skills_master.csv"
    text = """
    SKILLS
    Programming Languages: Python, TensorFlow

    PROJECTS
    Built recommendation engine using Python and TensorFlow
    """
    results = extract_skills(text, str(skills_csv))
    skill_names = {r["skill"] for r in results}

    assert "Python" in skill_names
    assert "TensorFlow" in skill_names
    assert "Built recommendation engine using Python and TensorFlow" not in skill_names
    assert "EXPERIENCE" not in skill_names
    assert "PROJECTS" not in skill_names


def test_filter_valid_skills_rejects_false_positives():
    mixed = [
        {"skill": "EXPERIENCE", "sections": ["skills"]},
        {"skill": "PROJECTS", "sections": ["skills"]},
        {"skill": "Built recommendation engine using Python and TensorFlow", "sections": ["skills"]},
        {"skill": "Python", "sections": ["skills"]},
        {"skill": "TensorFlow", "sections": ["skills"]},
    ]
    filtered = filter_valid_skills(mixed)
    kept = {r["skill"] for r in filtered}
    assert kept == {"Python", "TensorFlow"}


def test_parentheses_aware_splitting_preserves_office_suite():
    skills_csv = Path(__file__).resolve().parent.parent.parent.parent / "datasets" / "skills_master.csv"
    text = """
    SKILLS
    Tools: Microsoft Office (Word, Excel, PowerPoint, Outlook), ADP
    """
    results = extract_skills(text, str(skills_csv))
    skill_names = {r["skill"] for r in results}

    assert "Microsoft Office (Word, Excel, PowerPoint, Outlook)" in skill_names
    assert "Microsoft Office (Word" not in skill_names
    assert "Outlook)" not in skill_names


def test_pii_rejection():
    bad = [
        "Contact: Yes: (808) 256-4295",
        "Supervisor's Name: Joanna Bagg",
        "Supervisor: Roosevelt Pryor",
        "test@example.com",
        "https://example.com",
        "www.example.com",
    ]
    for s in bad:
        is_valid, _ = is_valid_skill(s)
        assert not is_valid, f"PII should be rejected: {s}"


def test_location_rejection():
    for loc in ("New Jersey", "Arizona", "California", "Texas"):
        is_valid, _ = is_valid_skill(loc)
        assert not is_valid, f"Location should be rejected: {loc}"


def test_inline_skills_word_does_not_start_section():
    # Previously, case-insensitive matching could treat the word "Skills" mid-line as a heading,
    # leaking EDUCATION text into the SKILLS section.
    text = "Education Bachelor of Science Arizona State University - City, State, USA Skills, Microsoft Office (Word, Excel)"
    section_aliases = {"skills": ["SKILLS"]}
    extracted = extract_section_by_aliases(text, section_aliases["skills"])
    assert extracted == ""


# Test runner for backward compatibility verification
if __name__ == "__main__":
    tests = [
        ("test_multiline_merge_technical", test_multiline_merge_technical),
        ("test_normalize_skill_exact_alias", test_normalize_skill_exact_alias),
        ("test_normalize_skill_strips_punctuation", test_normalize_skill_strips_punctuation),
        ("test_section_headers_not_extracted", test_section_headers_not_extracted),
        ("test_sentence_fragment_not_extracted", test_sentence_fragment_not_extracted),
        ("test_valid_skills_still_extracted", test_valid_skills_still_extracted),
        ("test_filter_valid_skills_rejects_false_positives", test_filter_valid_skills_rejects_false_positives),
        ("test_parentheses_aware_splitting_preserves_office_suite", test_parentheses_aware_splitting_preserves_office_suite),
        ("test_pii_rejection", test_pii_rejection),
        ("test_location_rejection", test_location_rejection),
        ("test_inline_skills_word_does_not_start_section", test_inline_skills_word_does_not_start_section),
    ]
    
    passed = 0
    failed = 0
    
    print("\nRunning original test suite for backward compatibility...\n")
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"[OK] {test_name}")
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test_name}: {e}")
            failed += 1
        except Exception as e:
            print(f"[FAIL] {test_name}: Unexpected error: {e}")
            failed += 1
    
    print(f"\nResult: {passed}/{len(tests)} tests passed")
    
    if failed == 0:
        print("[OK] All tests pass - backward compatibility maintained!")
    else:
        print(f"[FAIL] {failed} tests failed")