from typing import Dict, Any

class HealthScorer:
    """Calculates the composite ResearchGuard Reference Health Score and sub-dimension breakdowns."""

    def calculate_health_score(
        self,
        total_references: int,
        verified_count: int,
        metadata_issues_count: int,
        possible_matches_count: int,
        not_found_count: int,
        invalid_doi_count: int,
        duplicate_count: int,
        orphan_count: int,
        unused_count: int,
        citation_coverage_pct: float,
        semantic_relevance_pct: float
    ) -> Dict[str, Any]:
        
        if total_references == 0:
            return {
                "health_score": 0.0,
                "health_rating": "Inconclusive",
                "breakdown": {
                    "verification_score": 0.0,
                    "metadata_score": 0.0,
                    "coverage_score": 0.0,
                    "consistency_score": 0.0,
                    "hygiene_score": 0.0,
                }
            }

        # 1. Verification Component (Max 40 pts)
        verif_points = (
            (verified_count * 1.0 + metadata_issues_count * 0.80 + possible_matches_count * 0.40)
            / total_references
        ) * 40.0
        verif_score = max(0.0, min(40.0, verif_points))

        # 2. Metadata Correctness Component (Max 20 pts)
        meta_ratio = verified_count / total_references
        meta_score = max(0.0, min(20.0, meta_ratio * 20.0))

        # 3. Citation Coverage Component (Max 15 pts)
        coverage_score = max(0.0, min(15.0, (citation_coverage_pct / 100.0) * 15.0))

        # 4. Citation-Reference Consistency Component (Max 15 pts)
        consistency_base = 15.0
        orphan_penalty = min(8.0, orphan_count * 3.0)
        consistency_score = max(0.0, min(15.0, consistency_base - orphan_penalty))

        # 5. Hygiene & Deduplication Component (Max 10 pts)
        hygiene_base = 10.0
        invalid_doi_penalty = min(10.0, invalid_doi_count * 8.0)
        duplicate_penalty = min(4.0, duplicate_count * 3.0)
        unused_penalty = min(2.0, unused_count * 0.5)
        hygiene_score = max(0.0, min(10.0, hygiene_base - invalid_doi_penalty - duplicate_penalty - unused_penalty))

        # Total Composite Score
        total_score = round(verif_score + meta_score + coverage_score + consistency_score + hygiene_score, 1)
        total_score = max(5.0, min(100.0, total_score))

        # Determine Health Rating
        if not_found_count / total_references >= .5:
            rating = "Inconclusive"
        elif total_score >= 85.0:
            rating = "Excellent"
        elif total_score >= 70.0:
            rating = "Good"
        elif total_score >= 50.0:
            rating = "Needs Review"
        else:
            rating = "Poor"

        return {
            "health_score": total_score,
            "health_rating": rating,
            "breakdown": {
                "verification_score": round(verif_score, 1),
                "metadata_score": round(meta_score, 1),
                "coverage_score": round(coverage_score, 1),
                "consistency_score": round(consistency_score, 1),
                "hygiene_score": round(hygiene_score, 1),
            }
        }

health_scorer = HealthScorer()
