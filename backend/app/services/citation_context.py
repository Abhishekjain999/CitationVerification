import re
import unicodedata
from app.services.normalization import normalize_reference_id
from typing import List, Dict, Any, Optional

class CitationContextExtractor:
    """Extracts in-text citation occurrences, binds them to bibliography references, and identifies orphan/unused references."""

    BRACKET_CITATION_REGEX = re.compile(r'\[(\d+(?:[\s,;–—\-]+\d+)*)\]')
    AUTHOR_YEAR_CITATION_REGEX = re.compile(r'\(([A-Z][a-zA-Z\s\.\,\-]+(?:et\s+al\.?)?,\s*(?:19\d{2}|20\d{2}))\)')
    NARRATIVE_CITATION_REGEX = re.compile(r'\b[A-Z][A-Za-z\-]+(?:\s+et\s+al\.?)?\s+\((?:19|20)\d{2}\)')

    def extract_citations(
        self,
        pages: List[Dict[str, Any]],
        full_text: str,
        references: List[Dict[str, Any]],
        sections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        
        # 1. Isolate main body text (before References section)
        ref_header_match = re.search(r'(?:^|\n)\s*(?:(?:\d+|[IVXLCDM]+)\.?\s+)?(?:REFERENCES|BIBLIOGRAPHY)\b', full_text, re.IGNORECASE)
        body_text_limit = ref_header_match.start() if ref_header_match else len(full_text)
        appendix = re.search(r'(?im)^\s*Appendix\b', full_text[ref_header_match.end():]) if ref_header_match else None
        bibliography_end = ref_header_match.end() + appendix.start() if appendix else len(full_text)
        
        # Map reference numbers to reference objects
        ref_by_num: Dict[int, Dict[str, Any]] = {
            normalize_reference_id(r["reference_number"]): r for r in references if normalize_reference_id(r.get("reference_number")) is not None
        }
        
        occurrences: List[Dict[str, Any]] = []
        cited_ref_numbers = set()
        orphan_markers: List[Dict[str, Any]] = []
        malformed_ranges = []
        ambiguous_citations = []

        # Process page by page
        char_offset = 0
        for page in pages:
            p_num = page.get("page_number", 1)
            p_text = page.get("text", "")
            
            # If this page starts past body_text_limit, stop or skip reference parts
            if ref_header_match:
                before = p_text[:max(0, body_text_limit - char_offset)] if char_offset < body_text_limit else ''
                after = p_text[max(0, bibliography_end - char_offset):] if char_offset + len(p_text) > bibliography_end else ''
                analysis_text = before + '\n' + after
            else:
                analysis_text = p_text

            # Split page text into sentences
            sentences = self._split_into_sentences(analysis_text)

            for sentence in sentences:
                clean_sentence = re.sub(r'\s+', ' ', sentence).strip()
                if not clean_sentence:
                    continue

                # Detect which section this sentence belongs to
                current_section = self._get_section_for_page(p_num, sections)

                # Search bracketed citations e.g. [1], [1, 2], [3-5]
                bracket_matches = self.BRACKET_CITATION_REGEX.finditer(clean_sentence)
                for match in bracket_matches:
                    match.group(0)
                    numbers_str = match.group(1)
                    parsed_numbers = self._expand_number_range(numbers_str)
                    for part in re.split(r'[,;]', numbers_str):
                        if re.search(r'[–—\-]', part) and not self._expand_number_range(part):
                            malformed_ranges.append({'citation_marker': match.group(0), 'sentence': clean_sentence, 'page_number': p_num})

                    for num in parsed_numbers:
                        if num in ref_by_num:
                            ref_obj = ref_by_num[num]
                            cited_ref_numbers.add(num)
                            occurrences.append({
                                "reference_id": ref_obj.get("id"),
                                "reference_number": num,
                                "citation_marker": f"[{num}]",
                                "page_number": p_num,
                                "sentence": clean_sentence,
                                "section": current_section,
                                "claim_text": clean_sentence,
                            })
                        else:
                            # Orphan citation: cited in body but does not exist in references
                            orphan_markers.append({
                                "citation_marker": f"[{num}]",
                                "page_number": p_num,
                                "sentence": clean_sentence,
                                "section": current_section,
                            })

                # Search Author-Year citations e.g. (Vaswani et al., 2017)
                for marker_str in self._author_year_markers(clean_sentence):
                    matches = self._author_year_candidates(marker_str, references)
                    matched_ref = matches[0] if len(matches) == 1 else None
                    if matched_ref:
                        num = normalize_reference_id(matched_ref.get("reference_number"))
                        cited_ref_numbers.add(num)
                        occurrences.append({
                            "reference_id": matched_ref.get("id"),
                            "reference_number": num,
                            "citation_marker": marker_str,
                            "page_number": p_num,
                            "sentence": clean_sentence,
                            "section": current_section,
                            "claim_text": clean_sentence,
                        })
                    else:
                        detail = {"citation_marker": marker_str, "page_number": p_num, "sentence": clean_sentence, "section": current_section}
                        if matches:
                            ambiguous_citations.append({**detail, 'candidate_references': [r['reference_number'] for r in matches]})
                        else:
                            orphan_markers.append(detail)

            char_offset += len(p_text) + 2  # PDFExtractor joins pages with two newlines.

        # Identify Unused References (in bibliography but not cited in text)
        unused_references = []
        for r_num, r_obj in ref_by_num.items():
            if r_num not in cited_ref_numbers:
                unused_references.append(r_obj)

        citation_coverage = (len(cited_ref_numbers) / len(references) * 100.0) if references else 100.0

        return {
            "occurrences": occurrences,
            "orphan_citations": orphan_markers,
            "unused_references": unused_references,
            "citation_coverage_pct": round(min(100.0, citation_coverage), 1),
            "total_in_text_citations": len(occurrences),
            "malformed_ranges": malformed_ranges,
            "ambiguous_citations": ambiguous_citations,
        }

    def _expand_number_range(self, numbers_str: str) -> List[int]:
        """Expands citation strings like '1, 3-5, 8' into [1, 3, 4, 5, 8]."""
        results = []
        parts = re.split(r'[,;]', numbers_str)
        for part in parts:
            part = part.strip()
            # Check for range: 3-5, 3–5
            range_match = re.match(r'^(\d+)\s*[–—\-]\s*(\d+)$', part)
            if range_match:
                start, end = int(range_match.group(1)), int(range_match.group(2))
                if 1 <= start <= end <= start + 25:  # safeguard against accidental massive range
                    results.extend(list(range(start, end + 1)))
            elif part.isdigit():
                results.append(int(part))
        return list(dict.fromkeys(results))

    def _match_author_year_to_reference(self, marker: str, references: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        matches = self._author_year_candidates(marker, references)
        return matches[0] if len(matches) == 1 else None

    def _author_year_candidates(self, marker, references):
        # Extract author surname and year from (Author et al., 2020)
        match = re.search(r'([A-Za-z][\w\s.,\-]*?)\s*[, (]\s*((?:18|19|20)\d{2})([a-z]?)', marker)
        if not match:
            return []
        author_text, year_str, suffix = match.group(1), match.group(2), match.group(3)
        author_text = re.sub(r'\bet\s+al\.?', '', author_text, flags=re.I)
        first = re.split(r'\s+and\s+|&|,', author_text)[0]
        def tokens(value):
            value = ''.join(c for c in unicodedata.normalize('NFKD', value.lower()) if not unicodedata.combining(c))
            return set(re.findall(r'\w+', value))
        required = tokens(first)
        year = int(year_str)
        matches = []
        for ref in references:
            ref_year = ref.get("year")
            ref_raw = ref.get("raw_text", "").lower()
            authors = ref.get('authors') or []
            first_author = str(authors[0]) if authors and authors != ['Unknown Author'] else re.split(r'\b(?:18|19|20)\d{2}', ref_raw)[0]
            ref_suffix = re.search(rf'\b{year}([a-z])\b', ref_raw)
            if str(ref_year) == str(year) and required and required.issubset(tokens(first_author)) and (not suffix or (ref_suffix and ref_suffix.group(1) == suffix)):
                matches.append(ref)
        return matches

    def _author_year_markers(self, sentence):
        markers = []
        for parenthetical in re.finditer(r'\(([^()]{1,400})\)', sentence):
            for part in parenthetical.group(1).split(';'):
                if re.match(r'\s*(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b', part, re.I):
                    continue
                if re.fullmatch(r'\s*[A-Z][\w\s.,&\-]*?,\s*(?:18|19|20)\d{2}[a-z]?\s*', part):
                    markers.append('(' + part.strip() + ')')
        narrative = re.compile(r'\b([A-Z][\w\-]*(?:\s+(?:and|Kim)\s+[A-Z][\w\-]*)?(?:\s+et\s+al\.?)?)\s*\(((?:18|19|20)\d{2}[a-z]?)\)')
        markers.extend(m.group(0) for m in narrative.finditer(sentence))
        return list(dict.fromkeys(markers))

    def _split_into_sentences(self, text: str) -> List[str]:
        # Handle abbreviations like e.g., i.e., Fig., Vol., et al.
        protected = text
        protected = re.sub(r'\b(e\.g\.|i\.e\.|et al\.|Fig\.|Table\.|Vol\.|No\.|Dr\.|Prof\.|vs\.)\s*', r'\1___', protected)
        sentences = re.split(r'(?<=[.!?])\s+', protected)
        return [s.replace('___', ' ') for s in sentences]

    def _get_section_for_page(self, page_number: int, sections: List[Dict[str, Any]]) -> str:
        if not sections:
            return "Main Body"
        active_sec = "Main Body"
        for sec in sections:
            if sec.get("start_page", 1) <= page_number:
                active_sec = sec.get("title", "Main Body")
            else:
                break
        return active_sec

citation_context_extractor = CitationContextExtractor()
