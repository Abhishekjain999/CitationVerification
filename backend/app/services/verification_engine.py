from typing import List, Dict, Any
from app.services.similarity_engine import similarity_engine
from app.core.config import settings

class VerificationEngine:
    """Evaluates candidate scholarly records and determines reference verification status and confidence."""

    def verify_reference(self, parsed_ref: Dict[str, Any], candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        ref_authors = parsed_ref.get("authors") or []
        ref_year = parsed_ref.get("year")
        ref_venue = parsed_ref.get("venue") or parsed_ref.get("journal") or parsed_ref.get("conference")
        ref_doi = parsed_ref.get("doi")

        if not candidates:
            return {
                "status": "NOT FOUND",
                "confidence": 0.0,
                "overall_score": 0.0,
                "title_similarity": 0.0,
                "author_similarity": 0.0,
                "year_match": False,
                "year_difference": 0.0,
                "venue_similarity": 0.0,
                "doi_match": False,
                "doi_status": "UNVERIFIED" if ref_doi else "NONE",
                "matched_title": None,
                "matched_authors": [],
                "matched_year": None,
                "matched_venue": None,
                "matched_publisher": None,
                "matched_doi": None,
                "matched_url": None,
                "matched_abstract": None,
                "citation_count": 0,
                "verification_sources": [],
                "openalex_match": None,
                "crossref_match": None,
                "semantic_scholar_match": None,
                "explanation": "Verification is inconclusive: no matching record was retrieved. This does not establish that the reference or DOI is invalid. " + ("Provider limitations: " + '; '.join(sorted(set(parsed_ref.get('_provider_diagnostics', [])))) if parsed_ref.get('_provider_diagnostics') else "The work may be unindexed or extraction may be incomplete."),
                "metadata_mismatches": [],
            }

        # Evaluate all candidates and rank by score
        evaluated_candidates = []
        for cand in candidates:
            score_data = self._score_candidate(parsed_ref, cand)
            evaluated_candidates.append({
                "candidate": cand,
                "scores": score_data
            })

        # Sort by overall score descending
        evaluated_candidates.sort(key=lambda x: x["scores"]["overall_score"], reverse=True)
        best = evaluated_candidates[0]
        best_cand = best["candidate"]
        scores = best["scores"]

        # Check for Critical DOI Mismatch:
        # If reference provided a DOI, but that DOI resolves to a completely different paper
        is_doi_mismatch = False
        doi_mismatch_desc = ""
        if ref_doi:
            # Check if any candidate came from DOI query
            doi_match, doi_status = similarity_engine.verify_doi_match(ref_doi, best_cand.get("doi"))
            if doi_match and best_cand.get("doi_lookup") and scores["title_similarity"] < 0.60:
                is_doi_mismatch = True
                doi_mismatch_desc = f"The provided DOI ({ref_doi}) resolves to '{best_cand.get('title')}' which is a completely different work."

        # Detect metadata mismatches
        mismatches = []
        if scores["title_similarity"] >= 0.70:
            if not scores["year_match"] and scores["year_diff"] >= 1:
                mismatches.append({
                    "field": "Year",
                    "reference_value": str(ref_year),
                    "db_value": str(best_cand.get("publication_year")),
                    "explanation": f"Publication year differs: Reference indicates {ref_year}, but scholarly records show {best_cand.get('publication_year')}."
                })
            if scores["author_similarity"] < 0.65:
                mismatches.append({
                    "field": "Authors",
                    "reference_value": ", ".join(ref_authors[:3]),
                    "db_value": ", ".join([str(a) for a in best_cand.get("authors", [])[:3]]),
                    "explanation": "Author list in reference is abbreviated, incomplete, or partially discordant with scholarly records."
                })
            if scores["venue_similarity"] < 0.40 and ref_venue:
                mismatches.append({
                    "field": "Venue",
                    "reference_value": str(ref_venue),
                    "db_value": str(best_cand.get("venue")),
                    "explanation": f"Venue/Journal differs: Reference lists '{ref_venue}', scholarly record lists '{best_cand.get('venue')}'."
                })
            if ref_doi and not scores["doi_match"]:
                mismatches.append({
                    "field": "DOI",
                    "reference_value": str(ref_doi),
                    "db_value": str(best_cand.get("doi")),
                    "explanation": "DOI specified in reference could not be validated or differs from registered DOI."
                })

        # Determine Verification Category
        overall_score = scores["overall_score"]
        title_sim = scores["title_similarity"]
        
        status = "NOT FOUND"
        explanation = ""

        if is_doi_mismatch:
            status = "INVALID DOI"
            explanation = doi_mismatch_desc
        elif overall_score >= settings.VERIFIED_SCORE and title_sim >= 0.78 and (scores["doi_match"] or (ref_authors and scores["author_similarity"] >= 0.65 and scores["year_match"])):
            if mismatches:
                status = "VERIFIED WITH METADATA ISSUES"
                explanation = f"The referenced scholarly work was successfully identified ({best_cand.get('title')}), but some metadata elements differ: " + "; ".join([m["explanation"] for m in mismatches])
            else:
                status = "VERIFIED"
                explanation = f"Strong evidence confirms this reference matches '{best_cand.get('title')}' across {len(best_cand.get('all_sources', []))} scholarly sources."
        elif overall_score >= settings.METADATA_MATCH_SCORE and title_sim >= 0.78 and mismatches and scores['author_similarity'] >= 0.65:
            status = "VERIFIED WITH METADATA ISSUES"
            explanation = f"Matched '{best_cand.get('title')}' with moderate confidence. Metadata discrepancies detected: " + ("; ".join([m["explanation"] for m in mismatches]) if mismatches else "minor variations in author or venue names.")
        elif overall_score >= settings.POSSIBLE_MATCH_SCORE or title_sim >= 0.60:
            status = "POSSIBLE MATCH"
            explanation = f"A possible match was found ('{best_cand.get('title')}'), but similarity confidence ({overall_score:.0f}%) is insufficient to verify conclusively."
        else:
            status = "NOT FOUND"
            explanation = "No convincing matching record was found in OpenAlex, Crossref, or Semantic Scholar. The reference may be unindexed or cited under a different title."

        # Compute Confidence Score (0-100)
        confidence = round(min(100.0, max(5.0, overall_score)), 1)
        if status == "NOT FOUND":
            confidence = round(min(30.0, overall_score), 1)

        source_records = best_cand.get("source_records", {})

        return {
            "status": status,
            "confidence": confidence,
            "overall_score": overall_score,
            "title_similarity": scores["title_similarity"],
            "author_similarity": scores["author_similarity"],
            "year_match": scores["year_match"],
            "year_difference": scores["year_diff"],
            "venue_similarity": scores["venue_similarity"],
            "doi_match": scores["doi_match"],
            "doi_status": scores["doi_status"],
            "matched_title": best_cand.get("title"),
            "matched_authors": best_cand.get("authors", []),
            "matched_year": str(best_cand.get("publication_year")) if best_cand.get("publication_year") else None,
            "matched_venue": best_cand.get("venue"),
            "matched_publisher": best_cand.get("publisher"),
            "matched_doi": best_cand.get("doi"),
            "matched_url": best_cand.get("url"),
            "matched_abstract": best_cand.get("abstract"),
            "citation_count": best_cand.get("citation_count", 0),
            "verification_sources": best_cand.get("all_sources", []),
            "openalex_match": source_records.get("OpenAlex"),
            "crossref_match": source_records.get("Crossref"),
            "semantic_scholar_match": source_records.get("Semantic Scholar"),
            "explanation": explanation,
            "metadata_mismatches": mismatches,
        }

    def _score_candidate(self, parsed_ref: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
        ref_title = parsed_ref.get("title")
        ref_authors = parsed_ref.get("authors") or []
        ref_year = parsed_ref.get("year")
        ref_venue = parsed_ref.get("venue") or parsed_ref.get("journal") or parsed_ref.get("conference")
        ref_doi = parsed_ref.get("doi")

        cand_title = candidate.get("title")
        cand_authors = candidate.get("authors") or []
        cand_year = candidate.get("publication_year")
        cand_venue = candidate.get("venue")
        cand_doi = candidate.get("doi")

        title_sim = similarity_engine.calculate_title_similarity(ref_title, cand_title)
        author_sim = similarity_engine.calculate_author_similarity(ref_authors, cand_authors)
        is_year_match, year_diff, year_sim = similarity_engine.calculate_year_match(ref_year, cand_year)
        venue_sim = similarity_engine.calculate_venue_similarity(ref_venue, cand_venue)
        is_doi_match, doi_status = similarity_engine.verify_doi_match(ref_doi, cand_doi)

        # Calculate weighted overall score
        if ref_doi:
            # Dynamic weights with DOI: Title 40%, Authors 25%, Year 10%, Venue 10%, DOI 15%
            doi_contrib = 1.0 if is_doi_match else (0.3 if doi_status == "NOT_IN_DB" else 0.0)
            overall = (
                0.40 * title_sim +
                0.25 * author_sim +
                0.10 * year_sim +
                0.10 * venue_sim +
                0.15 * doi_contrib
            ) * 100.0
        else:
            # Dynamic weights without DOI: Title 45%, Authors 30%, Year 15%, Venue 10%
            overall = (
                0.45 * title_sim +
                0.30 * author_sim +
                0.15 * year_sim +
                0.10 * venue_sim
            ) * 100.0

        # Multi-source confirmation bonus (up to +5% if verified across multiple sources)
        sources_count = len(candidate.get("all_sources", []))
        if sources_count >= 2 and title_sim >= 0.80:
            overall = min(100.0, overall + (sources_count - 1) * 2.5)

        return {
            "overall_score": round(float(overall), 2),
            "title_similarity": title_sim,
            "author_similarity": author_sim,
            "year_match": is_year_match,
            "year_diff": year_diff,
            "venue_similarity": venue_sim,
            "doi_match": is_doi_match,
            "doi_status": doi_status,
        }

verification_engine = VerificationEngine()
