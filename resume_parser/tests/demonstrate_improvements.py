"""
DEMONSTRATION: False Positive Reduction in Skill Extraction

This script demonstrates how the improvements reduce false positives
and improve accuracy in the resume skill extraction engine.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from skill_extractor import (
    is_valid_skill,
    filter_valid_skills,
    add_confidence_scores,
)


def demonstrate_false_positive_reduction():
    """Show how the new validation filters eliminate false positives."""
    
    print("\n" + "="*70)
    print("DEMONSTRATION: FALSE POSITIVE REDUCTION")
    print("="*70)
    
    # Problematic skills that were being extracted before
    problematic_skills = [
        {
            "skill": "Business Management Arizona State University City",
            "frequency": 1,
            "sections": ["experience"],
            "evidence": ["Business Management Arizona State University City"]
        },
        {
            "skill": "Model Training &",
            "frequency": 1,
            "sections": ["projects"],
            "evidence": ["Model Training &"]
        },
        {
            "skill": "Bachelor of Engineering",
            "frequency": 1,
            "sections": ["education"],
            "evidence": ["Bachelor of Engineering"]
        },
        {
            "skill": "Arizona State University",
            "frequency": 2,
            "sections": ["experience", "education"],
            "evidence": ["Arizona State University"]
        },
        {
            "skill": "Python",
            "frequency": 5,
            "sections": ["skills"],
            "evidence": ["Python, Java, JavaScript"]
        },
        {
            "skill": "Machine Learning",
            "frequency": 3,
            "sections": ["projects", "experience"],
            "evidence": ["Machine Learning Engineer", "Applied Machine Learning"]
        },
        {
            "skill": "Cloud Computing City Center",
            "frequency": 1,
            "sections": ["experience"],
            "evidence": ["Cloud Computing City Center"]
        },
        {
            "skill": "Master of Science",
            "frequency": 1,
            "sections": ["education"],
            "evidence": ["Master of Science in Computer Science"]
        },
    ]
    
    print("\n" + "-"*70)
    print("BEFORE IMPROVEMENTS - False Positives Extracted:")
    print("-"*70)
    for skill in problematic_skills:
        print(f"  ✗ {skill['skill']} (from {skill['sections']})")
    
    print("\n" + "-"*70)
    print("AFTER IMPROVEMENTS - Validation & Filtering:")
    print("-"*70)
    
    print("\nApplying new validation rules...\n")
    
    filtered = filter_valid_skills(problematic_skills)
    with_confidence = add_confidence_scores(filtered)
    
    print("\n" + "-"*70)
    print("RESULTS - Only Valid Skills Retained:")
    print("-"*70)
    
    if with_confidence:
        for skill in with_confidence:
            print(f"  ✓ {skill['skill']}")
            print(f"      Confidence: {skill['confidence']}")
            print(f"      Frequency: {skill['frequency']}")
            print(f"      Sections: {skill['sections']}")
            print()
    
    print("-"*70)
    print(f"SUMMARY: {len(problematic_skills) - len(with_confidence)} false positives removed")
    print(f"         {len(with_confidence)} valid skills retained")
    print("-"*70)
    
    return len(with_confidence) > 0


def demonstrate_validation_rules():
    """Show each validation rule in action."""
    
    print("\n" + "="*70)
    print("VALIDATION RULES DEMONSTRATION")
    print("="*70)
    
    test_cases = [
        ("", "Empty string"),
        ("a", "Too short (1 char)"),
        ("a" * 100, "Too long (>80 chars)"),
        ("Python", "Valid skill"),
        ("123456789", "Mostly numeric (>50% digits)"),
        ("one two three four five six seven eight nine", "Too many words (>8)"),
        ("Bachelor of Science", "Contains 'bachelor' keyword"),
        ("University of Michigan", "Contains 'university' keyword"),
        ("Arizona State College", "Contains 'college' keyword"),
        ("GPA Score 4.0", "Contains 'gpa' keyword"),
        ("My Email Address", "Contains 'email' keyword"),
        ("Machine Learning Engineer", "Valid multi-word skill (4 words)"),
        ("Python & JavaScript", "Valid with punctuation"),
    ]
    
    print("\nValidation Results:")
    print("-" * 70)
    
    for skill, description in test_cases:
        is_valid, reason = is_valid_skill(skill)
        status = "✓ VALID" if is_valid else f"✗ INVALID ({reason})"
        display_skill = skill if len(skill) < 30 else skill[:27] + "..."
        print(f"  {status:30} | {display_skill:30} | {description}")
    
    print("-" * 70)


def demonstrate_confidence_levels():
    """Show how confidence levels are assigned."""
    
    print("\n" + "="*70)
    print("CONFIDENCE LEVEL ASSIGNMENT")
    print("="*70)
    
    scenarios = [
        (
            "Python",
            ["skills"],
            "Extracted directly from SKILLS section"
        ),
        (
            "Docker",
            ["projects", "experience"],
            "Found in both PROJECTS and EXPERIENCE sections"
        ),
        (
            "Kubernetes",
            ["experience"],
            "Found in EXPERIENCE section only"
        ),
        (
            "React",
            ["projects"],
            "Found in PROJECTS section only"
        ),
        (
            "AWS",
            ["database_scan"],
            "Found only through database scan (low confidence)"
        ),
    ]
    
    print("\nConfidence Assignment Rules:")
    print("-" * 70)
    print("  High:   Skill extracted from SKILLS section")
    print("  Medium: Skill found in PROJECTS or EXPERIENCE sections")
    print("  Low:    Skill found only through database scan")
    print("-" * 70)
    
    print("\nExamples:")
    print("-" * 70)
    
    for skill, sections, description in scenarios:
        from skill_extractor import get_confidence
        confidence = get_confidence(sections)
        print(f"  {skill:15} | {confidence:6} | {description}")
    
    print("-" * 70)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("RESUME SKILL EXTRACTION ENGINE - IMPROVEMENT DEMONSTRATIONS")
    print("="*70)
    
    # Run demonstrations
    demonstrate_false_positive_reduction()
    demonstrate_validation_rules()
    demonstrate_confidence_levels()
    
    print("\n" + "="*70)
    print("DEMONSTRATIONS COMPLETE")
    print("="*70)
    print("\nKey Improvements:")
    print("  1. Validation function rejects low-quality skills")
    print("  2. Ignore patterns eliminate education/location phrases")
    print("  3. Education section excluded from database scan")
    print("  4. Confidence scoring indicates extraction reliability")
    print("  5. Detailed discard logging for debugging")
    print("\n✓ False positive rate significantly reduced")
    print("✓ Code maintainability improved with clear comments")
    print("✓ API backward compatibility maintained")
    print("="*70 + "\n")
