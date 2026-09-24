import numpy as np
from typing import List, Dict, Any
import models

def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))

def score_outfit(items: List[models.ClothingItem], user: models.User) -> Dict[str, Any]:
    """
    Score a candidate outfit based on multiple components:
    1. Visual Similarity (CLIP embeddings) - max 30 pts
    2. Formality Match - max 25 pts
    3. Season Compatibility - max 20 pts
    4. Color Harmony - max 15 pts
    5. Body Type Bonus - max 10 pts
    Total max: 100 pts
    """
    if len(items) < 2:
        # A single item (or no items) doesn't make an outfit, score is 0
        return {
            "total_score": 0.0,
            "breakdown": {
                "visual_similarity": 0.0,
                "formality_match": 0.0,
                "season_compatibility": 0.0,
                "color_harmony": 0.0,
                "body_type_bonus": 0.0
            }
        }

    # 1. Visual Similarity
    # Average pairwise cosine similarity scaled to [0, 30]
    total_sim = 0.0
    pairs = 0
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i].embedding and items[j].embedding:
                sim = _cosine_similarity(items[i].embedding, items[j].embedding)
                total_sim += max(0.0, sim) # floor at 0
            pairs += 1
            
    avg_sim = total_sim / pairs if pairs > 0 else 0.0
    visual_score = avg_sim * 30.0

    # 2. Formality Match
    # Formality scale is 1.0 to 10.0
    formalities = [i.formality_score for i in items if i.formality_score is not None]
    formality_score = 25.0
    if len(formalities) > 1:
        variance = max(formalities) - min(formalities)
        # Max penalty kicks in if diff > 4
        penalty = min(25.0, (variance / 4.0) * 25.0)
        # However, a tiny variance (< 1.5) is essentially perfect
        if variance <= 1.5:
            penalty = 0.0
        formality_score = max(0.0, 25.0 - penalty)

    # 3. Season Compatibility
    # Simple rule: Summer vs Winter = clash. 
    # Fall/Spring are versatile.
    seasons = [i.season for i in items if i.season]
    season_score = 20.0
    if "summer" in seasons and "winter" in seasons:
        season_score = 0.0 # Clashing extremes
    elif len(set(seasons)) > 2:
        season_score = 10.0 # Too many mixed seasons
        
    # 4. Color Harmony
    # A very basic rule-based approach: reward neutrals, penalize opposite non-neutrals without neutrals
    colors = [i.color for i in items if i.color]
    neutrals = {"black", "white", "gray", "neutral"}
    color_score = 10.0 # Base ok score
    item_neutrals = [c for c in colors if c in neutrals]
    item_colors = [c for c in colors if c not in neutrals]
    
    if len(item_colors) <= 1:
        # Mostly neutrals or monochrome -> safe, looks good
        color_score = 15.0
    elif len(item_colors) > 2 and len(item_neutrals) == 0:
        # 3+ different bright colors and no neutrals -> clash
        color_score = 5.0

    # 5. Body Type Bonus
    # Heuristics based on user body type
    body_bonus = 5.0 # Base neutral bonus
    if user.body_type:
        bt = user.body_type.lower()
        cats = [i.category for i in items if i.category]
        # Example heuristic: Athletic body types get a small bonus for fitted combos
        if bt == "athletic" and "shirt" in cats and "pants" in cats:
            body_bonus = 8.0
        # Example heuristic: Plus-size gets a bonus for layered combos (jacket)
        elif bt == "plus-size" and "jacket" in cats:
            body_bonus = 8.0
        # Average/Slim gets small bonus for layered combos too
        elif bt in ["slim", "average"] and "jacket" in cats:
            body_bonus = 8.0

    total_score = visual_score + formality_score + season_score + color_score + body_bonus

    return {
        "total_score": round(total_score, 2),
        "breakdown": {
            "visual_similarity": round(visual_score, 2),
            "formality_match": round(formality_score, 2),
            "season_compatibility": round(season_score, 2),
            "color_harmony": round(color_score, 2),
            "body_type_bonus": round(body_bonus, 2)
        }
    }
