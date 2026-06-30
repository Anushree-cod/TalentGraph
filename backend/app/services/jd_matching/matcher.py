import json
from typing import Dict, Any

def match_candidate_to_job(candidate_skills: str, job_requirements: str) -> Dict[str, Any]:
    """
    Analyzes how well a candidate matches a job description.
    This is a placeholder for actual LLM or NLP matching logic.
    """
    try:
        skills_dict = json.loads(candidate_skills)
        candidate_skill_list = skills_dict.get("skills", [])
    except (json.JSONDecodeError, TypeError):
        candidate_skill_list = [candidate_skills] if candidate_skills else []
        
    job_req_lower = job_requirements.lower()
    
    # Simple keyword overlap simulation
    matched_skills = [skill for skill in candidate_skill_list if skill.lower() in job_req_lower]
    
    match_score = 0
    if candidate_skill_list:
        match_score = int((len(matched_skills) / len(candidate_skill_list)) * 100)
        
    # Ensure minimum base score if there is some overlap
    if len(matched_skills) > 0 and match_score < 30:
        match_score = 30
        
    return {
        "match_score": match_score,
        "matched_skills": matched_skills,
        "missing_skills": ["Simulated missing skill 1", "Simulated missing skill 2"],
        "recommendation": "Strong Match" if match_score > 75 else "Good Match" if match_score > 50 else "Weak Match"
    }
