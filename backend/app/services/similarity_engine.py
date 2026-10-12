import unicodedata
from app.services.normalization import normalize_doi
import re
from typing import List, Any, Tuple, Optional
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SimilarityEngine:
    """Calculates multi-dimensional similarity scores between reference citations and scholarly database records."""

    VENUE_ACRONYMS = {
        "neurips": "advances in neural information processing systems",
        "nips": "advances in neural information processing systems",
        "cvpr": "ieee cvf conference on computer vision and pattern recognition",
        "icml": "international conference on machine learning",
        "iclr": "international conference on learning representations",
        "acl": "association for computational linguistics",
        "emnlp": "empirical methods in natural language processing",
        "naacl": "north american chapter of the association for computational linguistics",
        "kdd": "acm sigkdd conference on knowledge discovery and data mining",
        "aaai": "aaai conference on artificial intelligence",
        "ijcai": "international joint conference on artificial intelligence",
        "tpami": "ieee transactions on pattern analysis and machine intelligence",
        "ieee tpami": "ieee transactions on pattern analysis and machine intelligence",
        "jmlr": "journal of machine learning research",
        "tacl": "transactions of the association for computational linguistics",
        "sigir": "international acm sigir conference on research and development in information retrieval",
        "www": "the web conference acm thewebconf",
        "nature": "nature scientific journal",
        "science": "science aaas american association for the advancement of science",
        "pnas": "proceedings of the national academy of sciences",
        "arxiv": "arxiv preprint",
    }

    def normalize_text(self, text: Optional[str]) -> str:
        if not text:
            return ""
        # 1. Unicode normalization (NFKD)
        norm = unicodedata.normalize('NFKD', text)
        # 2. Lowercase
        norm = norm.lower()
        # 3. Replace curly quotes, smart quotes, dashes
        norm = re.sub(r'[\u2018\u2019\u201c\u201d\"\'`]', '', norm)
        norm = re.sub(r'[\u2013\u2014\-–—]', ' ', norm)
        # 4. Remove punctuation
        norm = re.sub(r'[^\w\s]', ' ', norm)
        # 5. Collapse whitespace
        norm = re.sub(r'\s+', ' ', norm).strip()
        return norm

    def calculate_title_similarity(self, ref_title: Optional[str], db_title: Optional[str]) -> float:
        if not ref_title or not db_title:
            return 0.0

        norm_ref = self.normalize_text(ref_title)
        norm_db = self.normalize_text(db_title)

        if not norm_ref or not norm_db:
            return 0.0

        if norm_ref == norm_db:
            return 1.0

        # RapidFuzz metrics
        ratio = fuzz.ratio(norm_ref, norm_db) / 100.0
        token_sort = fuzz.token_sort_ratio(norm_ref, norm_db) / 100.0
        token_set = fuzz.token_set_ratio(norm_ref, norm_db) / 100.0

        # TF-IDF N-gram cosine similarity (character 3-grams)
        try:
            vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 4))
            tfidf_matrix = vectorizer.fit_transform([norm_ref, norm_db])
            tfidf_sim = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
        except Exception:
            tfidf_sim = ratio

        # Hybrid weighted similarity
        # Emphasize token_set for subtitle variations or partial title truncations
        combined = 0.35 * token_sort + 0.35 * token_set + 0.15 * ratio + 0.15 * tfidf_sim
        return round(float(np.clip(combined, 0.0, 1.0)), 4)

    def extract_author_surnames(self, authors: List[Any]) -> List[str]:
        surnames = []
        for author in authors:
            name_str = ""
            if isinstance(author, str):
                name_str = author
            elif isinstance(author, dict):
                name_str = author.get("name") or author.get("family") or ""

            if not name_str or name_str == "Unknown Author":
                continue

            # Check if format is "Surname, Given"
            if "," in name_str:
                surname = name_str.split(",")[0].strip()
            else:
                parts = name_str.strip().split()
                surname = parts[-1] if parts else ""

            clean_surname = self.normalize_text(surname)
            if clean_surname and len(clean_surname) >= 2:
                surnames.append(clean_surname)

        return surnames

    def calculate_author_similarity(self, ref_authors: List[Any], db_authors: List[Any]) -> float:
        if not ref_authors or not db_authors:
            return 0.5  # Neutral if one list is missing

        ref_surnames = self.extract_author_surnames(ref_authors)
        db_surnames = self.extract_author_surnames(db_authors)

        if not ref_surnames or not db_surnames:
            return 0.5

        # 1. First author match (crucial in academic citations)
        first_author_match = False
        first_author_sim = fuzz.ratio(ref_surnames[0], db_surnames[0]) / 100.0
        if first_author_sim >= 0.85:
            first_author_match = True

        # Check if ref first author exists anywhere in db authors (sometimes order differs)
        first_author_in_db = any(fuzz.ratio(ref_surnames[0], s) / 100.0 >= 0.85 for s in db_surnames)

        # 2. Surnames Set Jaccard Overlap
        matches = 0
        for r_s in ref_surnames:
            if any(fuzz.ratio(r_s, d_s) / 100.0 >= 0.85 for d_s in db_surnames):
                matches += 1

        jaccard = matches / max(len(ref_surnames), len(db_surnames))

        # Composite score
        if first_author_match:
            score = 0.50 + 0.50 * jaccard
        elif first_author_in_db:
            score = 0.35 + 0.45 * jaccard
        else:
            score = 0.30 * jaccard

        return round(float(np.clip(score, 0.0, 1.0)), 4)

    def calculate_year_match(self, ref_year: Optional[int], db_year: Optional[Any]) -> Tuple[bool, float, float]:
        """Returns (is_exact_match, year_difference, similarity_score)."""
        if not ref_year or not db_year:
            return False, 0.0, 0.75  # Neutral score if year not specified in one of them

        try:
            db_y = int(str(db_year).split("-")[0].strip())
        except (ValueError, TypeError):
            return False, 0.0, 0.75

        diff = abs(ref_year - db_y)

        if diff == 0:
            return True, 0.0, 1.0
        elif diff == 1:
            # Common difference for preprints / online-first / conference proceedings publication date
            return False, 1.0, 0.85
        elif diff == 2:
            return False, 2.0, 0.50
        else:
            return False, float(diff), 0.10

    def expand_venue(self, venue_text: Optional[str]) -> str:
        norm = self.normalize_text(venue_text)
        for acronym, full_name in self.VENUE_ACRONYMS.items():
            if acronym in norm.split():
                norm += f" {full_name}"
        return norm

    def calculate_venue_similarity(self, ref_venue: Optional[str], db_venue: Optional[str]) -> float:
        if not ref_venue or not db_venue:
            return 0.70  # Neutral if one is missing

        expanded_ref = self.expand_venue(ref_venue)
        expanded_db = self.expand_venue(db_venue)

        if not expanded_ref or not expanded_db:
            return 0.70

        token_set = fuzz.token_set_ratio(expanded_ref, expanded_db) / 100.0
        token_sort = fuzz.token_sort_ratio(expanded_ref, expanded_db) / 100.0

        sim = max(token_set, token_sort)
        return round(float(sim), 4)

    def verify_doi_match(self, ref_doi: Optional[str], db_doi: Optional[str]) -> Tuple[bool, str]:
        """Returns (is_match, status_str: MATCH | MISMATCH | INVALID | NONE)."""
        if not ref_doi:
            return False, "NONE"
        if not db_doi:
            return False, "NOT_IN_DB"

        clean_ref = normalize_doi(ref_doi)
        clean_db = normalize_doi(db_doi)

        if clean_ref == clean_db:
            return True, "MATCH"
        else:
            return False, "MISMATCH"

similarity_engine = SimilarityEngine()
