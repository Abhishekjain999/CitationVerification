import re
from typing import Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from rapidfuzz import fuzz

class SemanticValidator:
    """Evaluates semantic relevance between in-text citation claims and the cited paper's abstract/title."""

    def evaluate_citation_claim(self, claim_text: str, ref_title: Optional[str], ref_abstract: Optional[str]) -> Dict[str, Any]:
        if not claim_text or len(claim_text.strip()) < 15:
            return {
                "relevance_score": 0.0,
                "status": "INSUFFICIENT EVIDENCE",
                "explanation": "Citation claim text was too brief for semantic evaluation."
            }

        ref_context = (ref_title or "") + " " + (ref_abstract or "")
        if not ref_abstract or len(ref_abstract.strip()) < 20:
            return {
                "relevance_score": 0.0,
                "status": "INSUFFICIENT EVIDENCE",
                "explanation": "No usable abstract was retrieved. A title alone cannot establish claim support. No relevance assessment was computed."
            }

        # 1. Clean and normalize texts
        clean_claim = self._clean_claim_text(claim_text)
        clean_ref = self._normalize_text(ref_context)

        # 2. Extract key domain keywords & phrases
        claim_keywords = self._extract_keywords(clean_claim)
        ref_keywords = self._extract_keywords(clean_ref)

        # Keyword overlap
        overlap = set(claim_keywords).intersection(set(ref_keywords))
        keyword_overlap_ratio = len(overlap) / max(len(claim_keywords), 1)

        # 3. TF-IDF Cosine Similarity
        try:
            vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([clean_claim, clean_ref])
            cosine_sim = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
        except Exception:
            return {"relevance_score": 0.0, "status": "INSUFFICIENT EVIDENCE", "explanation": "Insufficient vocabulary for a relevance assessment."}

        # 4. RapidFuzz Token Set Ratio
        token_set_sim = fuzz.token_set_ratio(clean_claim, clean_ref) / 100.0

        # Weighted semantic score
        raw_score = (0.45 * cosine_sim + 0.35 * token_set_sim + 0.20 * keyword_overlap_ratio) * 100.0
        # Scale to 0-100
        score = float(np.clip(raw_score * 1.25, 10.0, 98.0))
        relevance_score = round(score, 1)

        # Classify status
        if relevance_score >= 75.0:
            status = "STRONGLY RELATED"
            explanation = "High lexical overlap with the retrieved title and abstract."
        elif relevance_score >= 55.0:
            status = "RELATED"
            explanation = f"The referenced paper shares contextual domain overlap ({', '.join(list(overlap)[:2]) if overlap else 'related concepts'}) with the citation context."
        elif relevance_score >= 35.0:
            status = "WEAKLY RELATED"
            explanation = "Moderate conceptual distance detected between the claim sentence and the retrieved publication summary."
        else:
            status = "LOW RELEVANCE"
            explanation = "Low lexical overlap with the retrieved title and abstract; review the full source."

        return {
            "relevance_score": relevance_score,
            "status": status,
            "explanation": explanation + " Preliminary relevance assessment using TF-IDF, token similarity and keyword overlap on title and abstract only. Similarity does not prove or disprove claim support; full source text was not accessed."
        }

    def _clean_claim_text(self, claim: str) -> str:
        # Remove citation markers like [12], (Smith, 2020)
        c = re.sub(r'\[\d+(?:[\s,\–\-]+\d+)*\]', '', claim)
        c = re.sub(r'\([A-Za-z\s\.\,\-]+,\s*\d{4}\)', '', c)
        return self._normalize_text(c)

    def _normalize_text(self, text: str) -> str:
        t = text.lower()
        t = re.sub(r'[^\w\s]', ' ', t)
        t = re.sub(r'\s+', ' ', t).strip()
        return t

    def _extract_keywords(self, text: str) -> list[str]:
        words = text.split()
        stopwords = {
            "the", "and", "for", "that", "this", "with", "from", "are", "have", "been", "which",
            "were", "their", "paper", "show", "also", "such", "than", "more", "most", "these",
            "can", "could", "will", "our", "use", "used", "using", "into", "over", "after"
        }
        return [w for w in words if len(w) > 3 and w not in stopwords]

semantic_validator = SemanticValidator()
