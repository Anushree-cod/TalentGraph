from typing import List, Dict, Any

def rank_candidates(candidates_match_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sorts and ranks candidate match results based on their match scores.
    Expects a list of dictionaries where each dict has a 'match_score' key.
    """
    
    # Sort candidates by match_score descending
    ranked = sorted(
        candidates_match_data,
        key=lambda x: x.get('match_score', 0),
        reverse=True
    )
    
    # Add a rank field
    for idx, candidate in enumerate(ranked):
        candidate['rank'] = idx + 1
        
    return ranked
