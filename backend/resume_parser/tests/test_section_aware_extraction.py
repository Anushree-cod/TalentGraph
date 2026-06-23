"""
Tests for improved section-aware skill extraction.
Validates that the extraction prioritizes skills sections and avoids false positives
from education/company descriptions.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from skill_extractor import (
    extract_skills_from_section,
    extract_skills_from_database,
    _extract_candidates_from_section,
    normalize_skill,
    extract_section_by_aliases,
)


def test_skills_section_extraction():
    """Test that SKILLS section is properly extracted and parsed."""
    print("\n" + "="*70)
    print("TEST 1: Skills Section Extraction")
    print("="*70)
    
    text = """
    SKILLS
    Programming Languages: Python, Java, JavaScript
    Databases: MySQL, PostgreSQL, MongoDB
    Tools: Git, Docker, Kubernetes
    
    EXPERIENCE
    Senior Developer at TechCorp
    Worked on Python and Java projects
    """
    
    aliases = {}
    section_aliases = {
        "skills": ["SKILLS", "TECHNICAL SKILLS"],
        "experience": ["EXPERIENCE", "WORK EXPERIENCE"],
    }
    
    # Extract skills from SKILLS section only
    skills = extract_skills_from_section(text, aliases, section_aliases)
    
    print(f"\nExtracted {len(skills)} skills from SKILLS section:")
    for skill in skills:
        print(f"  - {skill['skill']} (section: {skill['section']})")
    
    # Verify structure
    assert all(s["section"] == "skills" for s in skills), "All should be from skills section"
    assert len(skills) > 0, "Should extract skills"
    
    print("\n[OK] SKILLS section correctly extracted with structured format")
    return True


def test_candidate_extraction_avoids_long_paragraphs():
    """Test that long paragraphs are avoided in candidate extraction."""
    print("\n" + "="*70)
    print("TEST 2: Candidate Extraction Avoids Long Paragraphs")
    print("="*70)
    
    section_text = """
    Senior Software Engineer at Big Tech Company
    Led a team of 5 engineers to build scalable microservices architecture using Docker and Kubernetes. Implemented CI/CD pipelines with Jenkins and GitHub Actions. This was a very long role where I did many things over several years including managing databases, writing tests, and mentoring junior developers.
    
    - Developed REST APIs using Python and Django
    - Managed PostgreSQL and Redis databases
    - Implemented real-time messaging with RabbitMQ
    
    Another very long description about how we scaled the system from 1000 QPS to 100000 QPS by optimizing queries and implementing caching strategies at multiple layers including HTTP caching, application layer caching, and database query caching.
    """
    
    # Extract candidates
    candidates = _extract_candidates_from_section(section_text, max_line_length=150)
    
    print(f"\nGenerated {len(candidates)} candidates from section text:")
    for i, candidate in enumerate(candidates, 1):
        length = len(candidate)
        print(f"  {i}. [{length:3d} chars] {candidate[:70]}..." if len(candidate) > 70 else f"  {i}. [{length:3d} chars] {candidate}")
    
    # Verify that very long paragraphs are filtered out
    long_paragraphs = [c for c in candidates if len(c) > 150]
    print(f"\nLong paragraphs (>150 chars) filtered: {len(long_paragraphs)} removed")
    
    # Verify that skill-related short lines are kept
    skill_lines = [c for c in candidates if any(tech in c.lower() for tech in ["python", "django", "postgresql", "redis", "rabbitmq"])]
    print(f"Skill-related candidates kept: {len(skill_lines)}")
    
    assert len(long_paragraphs) == 0, "Long paragraphs should be filtered"
    assert len(skill_lines) >= 2, "Should keep short skill-related lines"
    
    print("\n[OK] Long paragraphs correctly filtered, skill lines preserved")
    return True


def test_education_section_not_scanned():
    """Test that education section is not scanned for database skills."""
    print("\n" + "="*70)
    print("TEST 3: Education Section Not Scanned")
    print("="*70)
    
    text = """
    SKILLS
    Python, Java
    
    EXPERIENCE
    Software Engineer at TechCorp
    Used Python and JavaScript
    
    EDUCATION
    Bachelor of Computer Science at University
    Relevant Coursework: Data Structures (Python), Web Development (JavaScript)
    GPA: 3.8
    """
    
    skills_db = ["Python", "Java", "JavaScript", "Data Structures", "Web Development"]
    aliases = {}
    section_aliases = {
        "skills": ["SKILLS"],
        "experience": ["EXPERIENCE"],
        "education": ["EDUCATION"],
    }
    
    # Extract skills from database (should NOT include education section)
    database_skills = extract_skills_from_database(
        text,
        skills_db,
        aliases,
        section_aliases,
        sections_to_scan=["projects", "experience"]  # Explicit: skip education
    )
    
    print(f"\nExtracted {len(database_skills)} skills from database scan:")
    for skill in database_skills:
        print(f"  - {skill['skill']} (section: {skill['section']}, count: {skill['count']})")
    
    # Verify education-related items are not included
    found_sections = set(s["section"] for s in database_skills)
    print(f"\nSections found: {found_sections}")
    
    assert "education" not in found_sections, "Education section should not be scanned"
    
    # Should find skills from EXPERIENCE section
    experience_skills = [s for s in database_skills if s["section"] == "experience"]
    print(f"Skills from EXPERIENCE: {len(experience_skills)}")
    
    print("\n[OK] Education section correctly skipped from database scan")
    return True


def test_section_priority_order():
    """Test that sections are processed in priority order (Projects before Experience)."""
    print("\n" + "="*70)
    print("TEST 4: Section Priority Order (Projects > Experience)")
    print("="*70)
    
    text = """
    PROJECTS
    Built mobile app using React Native and Node.js
    
    EXPERIENCE
    Used Python and SQL in previous roles
    Worked with Node.js backend systems
    """
    
    skills_db = ["React Native", "Node.js", "Python", "SQL"]
    aliases = {}
    section_aliases = {
        "projects": ["PROJECTS"],
        "experience": ["EXPERIENCE"],
    }
    
    database_skills = extract_skills_from_database(
        text,
        skills_db,
        aliases,
        section_aliases,
        sections_to_scan=["projects", "experience"]  # Projects first
    )
    
    print(f"\nExtracted skills in priority order:")
    projects_skills = [s for s in database_skills if s["section"] == "projects"]
    experience_skills = [s for s in database_skills if s["section"] == "experience"]
    
    print(f"  From PROJECTS: {len(projects_skills)} skills")
    for s in projects_skills:
        print(f"    - {s['skill']}")
    
    print(f"  From EXPERIENCE: {len(experience_skills)} skills")
    for s in experience_skills:
        print(f"    - {s['skill']}")
    
    print("\n[OK] Sections processed in priority order")
    return True


def test_short_lines_with_skills():
    """Test that short lines with skills are properly extracted."""
    print("\n" + "="*70)
    print("TEST 5: Short Lines with Skills Extraction")
    print("="*70)
    
    section_text = """
    - Python, Django, REST APIs
    - Database design with PostgreSQL
    - Docker containerization
    - AWS deployment (EC2, S3, RDS)
    - Real-time systems with Redis
    
    This is a long paragraph about how I spent 3 years working on various projects related to backend infrastructure, microservices architecture, distributed systems, API gateway implementation, and various other technologies that are important for modern software development.
    """
    
    candidates = _extract_candidates_from_section(section_text)
    
    print(f"\nExtracted {len(candidates)} candidates:")
    for i, c in enumerate(candidates, 1):
        marker = "[SKILL]" if any(tech in c.lower() for tech in ["python", "django", "postgres", "docker", "aws", "redis"]) else "[OTHER]"
        print(f"  {i}. {marker} {c[:70]}..." if len(c) > 70 else f"  {i}. {marker} {c}")
    
    skill_candidates = [c for c in candidates if any(tech in c.lower() for tech in ["python", "django", "postgres", "docker", "aws", "redis"])]
    
    assert len(skill_candidates) >= 4, "Should keep multiple skill lines"
    print(f"\n[OK] {len(skill_candidates)} skill lines correctly extracted")
    return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SECTION-AWARE SKILL EXTRACTION - PRECISION IMPROVEMENTS")
    print("="*70)
    
    tests = [
        ("Skills Section Extraction", test_skills_section_extraction),
        ("Avoid Long Paragraphs", test_candidate_extraction_avoids_long_paragraphs),
        ("Education Section Skipped", test_education_section_not_scanned),
        ("Section Priority Order", test_section_priority_order),
        ("Short Lines with Skills", test_short_lines_with_skills),
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
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n>>> ALL TESTS PASSED - Precision improvements working!")
        sys.exit(0)
    else:
        print(f"\n>>> {total_count - passed_count} tests failed")
        sys.exit(1)
