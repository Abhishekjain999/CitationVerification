import re
from typing import List, Dict, Any, Tuple
from rapidfuzz import fuzz

class IssueDetector:
    """Detects academic citation issues, mismatches, duplicates, orphan citations, and missing citations."""

    EMPIRICAL_CLAIM_PATTERNS = [
        re.compile(r'\b(?:reduced|increased|improved|decreased|outperformed|achieved|surpassed)\b.*?\b(?:\d+%\s*|\d+\.\d+\s*%|\d+x\b|\d+\s*times)\b', re.IGNORECASE),
        re.compile(r'\b(?:state-of-the-art|SOTA|previous studies|prior work has demonstrated|existing literature shows)\b', re.IGNORECASE),
        re.compile(r'\b(?:according to recent benchmarks|empirical evaluations reveal)\b', re.IGNORECASE),
    ]

    def detect_all_issues(
        self,
        paper_id: str,
        references_with_verifications: List[Dict[str, Any]],
        citation_analysis: Dict[str, Any],
        full_text: str
    ) -> List[Dict[str, Any]]:
        
        issues: List[Dict[str, Any]] = []
        for marker in citation_analysis.get('malformed_ranges', []):
            issues.append({'issue_type': 'MALFORMED_CITATION_RANGE', 'severity': 'WARNING', 'title': 'Citation range cannot be expanded safely', 'description': 'A reversed or oversized citation range was skipped. Review its original marker.', 'details': marker})
        for marker in citation_analysis.get('ambiguous_citations', []):
            issues.append({'issue_type': 'AMBIGUOUS_CITATION', 'severity': 'INFO', 'title': 'Author-year citation is ambiguous', 'description': 'Multiple bibliography entries share this author and year. Add a year suffix or clarify which source is intended.', 'details': marker})

        # 1. Detect Duplicate References in Bibliography
        duplicate_pairs = self._find_duplicate_references(references_with_verifications)
        for ref1, ref2, similarity in duplicate_pairs:
            issues.append({
                "paper_id": paper_id,
                "reference_id": ref1.get("id"),
                "issue_type": "DUPLICATE_REFERENCE",
                "severity": "INFO",
                "title": f"Duplicate Reference Entry (Ref #{ref1.get('reference_number')} & Ref #{ref2.get('reference_number')})",
                "description": f"Reference #{ref1.get('reference_number')} and Reference #{ref2.get('reference_number')} appear to refer to the same scholarly work ('{ref1.get('title')}').",
                "details": {
                    "ref1_number": ref1.get("reference_number"),
                    "ref2_number": ref2.get("reference_number"),
                    "similarity": similarity,
                }
            })

        # 2. Detect Verification & Metadata Issues per Reference
        for ref_data in references_with_verifications:
            ref = ref_data.get("reference", {})
            ver = ref_data.get("verification", {})
            status = ver.get("status")
            mismatches = ver.get("metadata_mismatches", [])

            if status == "INVALID DOI":
                issues.append({
                    "paper_id": paper_id,
                    "reference_id": ref.get("id"),
                    "issue_type": "INVALID_DOI",
                    "severity": "CRITICAL",
                    "title": f"Critical DOI Mismatch in Ref #{ref.get('reference_number')}",
                    "description": ver.get("explanation") or f"The DOI in Reference #{ref.get('reference_number')} points to an unrelated publication.",
                    "details": {"doi": ref.get("doi"), "matched_title": ver.get("matched_title")},
                })
            elif status == "NOT FOUND":
                issues.append({
                    "paper_id": paper_id,
                    "reference_id": ref.get("id"),
                    "issue_type": "NOT_FOUND",
                    "severity": "WARNING",
                    "title": f"Unverified Reference (Ref #{ref.get('reference_number')})",
                    "description": ver.get('explanation') or 'No sufficiently matching scholarly record was retrieved; the result is inconclusive.',
                    "details": {"raw_text": ref.get("raw_text")},
                })
            elif status == "POSSIBLE MATCH":
                issues.append({
                    "paper_id": paper_id,
                    "reference_id": ref.get("id"),
                    "issue_type": "POSSIBLE_UNMATCHED",
                    "severity": "WARNING",
                    "title": f"Low Confidence Match (Ref #{ref.get('reference_number')})",
                    "description": ver.get("explanation") or f"Candidate found for Reference #{ref.get('reference_number')} but confidence is moderate ({ver.get('confidence')}%).",
                    "details": {"matched_title": ver.get("matched_title"), "confidence": ver.get("confidence")},
                })
            elif mismatches:
                for m in mismatches:
                    issues.append({
                        "paper_id": paper_id,
                        "reference_id": ref.get("id"),
                        "issue_type": "METADATA_MISMATCH",
                        "severity": "WARNING",
                        "title": f"Metadata Mismatch: {m.get('field')} in Ref #{ref.get('reference_number')}",
                        "description": m.get("explanation"),
                        "details": m,
                    })

        # 3. Detect Orphan Citations (cited in text, missing in references)
        orphans = citation_analysis.get("orphan_citations", [])
        for orphan in orphans:
            issues.append({
                "paper_id": paper_id,
                "reference_id": None,
                "issue_type": "ORPHAN_CITATION",
                "severity": "WARNING",
                "title": f"Orphan In-Text Citation {orphan.get('citation_marker')}",
                "description": f"Citation {orphan.get('citation_marker')} appears in the paper on Page {orphan.get('page_number')} ({orphan.get('section')}), but no corresponding entry exists in the bibliography.",
                "details": orphan,
            })

        # 4. Detect Unused References (in bibliography, never cited in text)
        unused = citation_analysis.get("unused_references", [])
        for u_ref in unused:
            issues.append({
                "paper_id": paper_id,
                "reference_id": u_ref.get("id"),
                "issue_type": "UNUSED_REFERENCE",
                "severity": "INFO",
                "title": f"Unused Reference (Ref #{u_ref.get('reference_number')})",
                "description": f"Reference #{u_ref.get('reference_number')} ('{u_ref.get('title')}') is listed in the bibliography but is never referenced anywhere in the main body text.",
                "details": {"reference_number": u_ref.get("reference_number"), "title": u_ref.get("title")},
            })

        # 5. Detect Potential Missing Citations (factual claims without in-text citation)
        missing_claims = self._detect_missing_citations(full_text)
        for claim in missing_claims[:4]:  # limit to top 4 salient claims
            issues.append({
                "paper_id": paper_id,
                "reference_id": None,
                "issue_type": "POTENTIAL_MISSING_CITATION",
                "severity": "INFO",
                "title": "Potentially Requires Citation",
                "description": f"Statement appears to state an empirical or literature claim without an explicit citation nearby: \"{claim.get('sentence')}\"",
                "details": claim,
            })

        for ref_data in references_with_verifications:
            ref = ref_data['reference']
            if not ref.get('title') or not ref.get('year') or not ref.get('authors') or ref.get('authors') == ['Unknown Author']:
                issues.append({'reference_id': ref.get('id'), 'issue_type': 'INCOMPLETE_METADATA', 'severity': 'INFO', 'title': 'Incomplete reference metadata', 'description': 'Title, author or year could not be confidently parsed.', 'details': {'raw_text': ref.get('raw_text')}})
        numbers = [r['reference'].get('reference_number') for r in references_with_verifications]
        if len(numbers) != len(set(numbers)) or (numbers and sorted(set(numbers)) != list(range(1, max(numbers) + 1))):
            issues.append({'issue_type': 'NUMBERING_INCONSISTENCY', 'severity': 'WARNING', 'title': 'Bibliography numbering needs review', 'description': 'Bibliography identifiers contain gaps or duplicates. Matching preserves the original identifiers.', 'details': {'identifiers': numbers}})
        for issue in issues:
            details = issue.setdefault('details', {})
            details.setdefault('confidence', 0.5 if issue['issue_type'] in {'NOT_FOUND', 'POTENTIAL_MISSING_CITATION', 'INCOMPLETE_METADATA'} else 0.9)
            details.setdefault('recommended_action', 'Compare the original bibliography and cited source; correct metadata or add the missing citation where appropriate.')
        return issues

    def _find_duplicate_references(self, references: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], Dict[str, Any], float]]:
        duplicates = []
        n = len(references)
        for i in range(n):
            ref1 = references[i].get("reference", {})
            t1 = (ref1.get("title") or "").strip().lower()
            doi1 = (ref1.get("doi") or "").strip().lower()
            if not t1 and not doi1:
                continue

            for j in range(i + 1, n):
                ref2 = references[j].get("reference", {})
                t2 = (ref2.get("title") or "").strip().lower()
                doi2 = (ref2.get("doi") or "").strip().lower()

                # Check exact DOI match
                if doi1 and doi2 and doi1 == doi2:
                    duplicates.append((ref1, ref2, 1.0))
                    continue

                # Check Title Similarity
                if t1 and t2:
                    ratio = fuzz.token_sort_ratio(t1, t2) / 100.0
                    if ratio >= 0.90:
                        duplicates.append((ref1, ref2, round(ratio, 2)))

        return duplicates

    def _detect_missing_citations(self, full_text: str) -> List[Dict[str, Any]]:
        # Take text before References
        ref_header_match = re.search(r'(?:^|\n)\s*(?:(?:\d+|[IVXLCDM]+)\.?\s+)?(?:REFERENCES|BIBLIOGRAPHY)\b', full_text, re.IGNORECASE)
        body_text = full_text[:ref_header_match.start()] if ref_header_match else full_text[:8000]

        sentences = re.split(r'(?<=[.!?])\s+', body_text)
        potential_claims = []

        for s in sentences:
            clean_s = s.strip()
            if len(clean_s) < 30 or len(clean_s) > 250:
                continue
            
            # Check if sentence already has a citation
            has_citation = bool(re.search(r'\[\d+[^\]]*\]|\b[A-Z][A-Za-z]+(?:\s+et al\.?)?\s*\(\d{4}\)|\([^)]*,\s*\d{4}\)', clean_s))
            if has_citation:
                continue

            # Check if sentence matches empirical claim pattern
            for pat in self.EMPIRICAL_CLAIM_PATTERNS:
                if pat.search(clean_s):
                    potential_claims.append({
                        "sentence": clean_s,
                        "confidence": 84.0,
                    })
                    break

        return potential_claims

issue_detector = IssueDetector()
