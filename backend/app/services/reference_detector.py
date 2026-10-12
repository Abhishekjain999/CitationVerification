import re
from typing import List, Dict, Any, Tuple

class ReferenceDetector:
    """Detects and segments reference sections from academic papers."""

    REF_SECTION_HEADERS = [
        r'(?:^|\n)\s*(?:(?:\d+|[IVXLCDM]+)\.?\s+)?(?:REFERENCES|BIBLIOGRAPHY|LITERATURE CITED|WORKS CITED|REFERENCES AND NOTES)\b',
    ]

    def extract_raw_references(self, full_text: str, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        layout_entries = self._layout_entries(pages)
        if layout_entries:
            return [{'reference_number': i, 'marker': f'#{i}', 'raw_text': self._clean_reference_text(text)} for i, text in enumerate(layout_entries, 1)]
        # 1. Locate start of reference section
        ref_start_idx = -1
        for header_pat in self.REF_SECTION_HEADERS:
            matches = list(re.finditer(header_pat, full_text, re.IGNORECASE))
            if matches:
                # Take the last major match (since papers have references at the end)
                ref_start_idx = matches[-1].end()
                break

        if ref_start_idx == -1:
            # Fallback: search in last 30% of text
            start_search_idx = int(len(full_text) * 0.6)
            match = re.search(r'\b(?:References|Bibliography)\b', full_text[start_search_idx:], re.IGNORECASE)
            if match:
                ref_start_idx = start_search_idx + match.end()
            else:
                return []  # No reliable bibliography boundary; do not parse the body as references.

        references_text = full_text[ref_start_idx:].strip()
        references_text = re.split(r'(?im)^\s*(?:Appendix\b|[A-Z](?:\.\d+)?\s+(?:Additional|Implementation|Experiments))', references_text)[0]

        # 2. Segment individual reference entries
        raw_entries = self._segment_entries(references_text)

        # 3. Clean and structure references
        structured_refs: List[Dict[str, Any]] = []
        for idx, (marker, raw_content) in enumerate(raw_entries, 1):
            clean_text = self._clean_reference_text(raw_content)
            if len(clean_text) >= 15:  # filter noise
                structured_refs.append({
                    "reference_number": int(re.search(r'\d+', marker).group()) if re.fullmatch(r'[\[(]?\d+[\]).]?', marker) else idx,
                    "marker": marker,
                    "raw_text": clean_text,
                })

        return structured_refs

    def _segment_entries(self, text: str) -> List[Tuple[str, str]]:
        """Segments text into individual reference items based on marker patterns."""
        # Consume the actual marker instead of a capturing lookahead, which duplicates
        # markers and can create empty fragments at newline boundaries.
        numbered = list(re.finditer(r'(?m)^\s*(\[\d+\]|\d{1,3}\.\s+|\(\d+\))', text))
        if numbered:
            return [(m.group(1).strip(), text[m.start():numbered[i + 1].start() if i + 1 < len(numbered) else len(text)].strip()) for i, m in enumerate(numbered)]
        author_year = list(re.finditer(r'(?m)^\s*[A-Z][^\n]{1,100}?\((?:19|20)\d{2}[a-z]?\)', text))
        if author_year:
            return [(f'#{i + 1}', text[m.start():author_year[i + 1].start() if i + 1 < len(author_year) else len(text)].strip()) for i, m in enumerate(author_year)]
        # Pattern 1: [1], [2], [3]...
        bracket_pattern = r'(?=(?:^|\n)\s*\[(\d+)\])'
        splits_bracket = re.split(bracket_pattern, text)
        if len(splits_bracket) > 3:
            entries = []
            # splits_bracket has [initial_junk, num1, text1, num2, text2, ...]
            for i in range(1, len(splits_bracket), 2):
                num = splits_bracket[i]
                body = splits_bracket[i+1] if i+1 < len(splits_bracket) else ""
                entries.append((f"[{num}]", f"[{num}] {body}".strip()))
            return entries

        # Pattern 2: 1. , 2. , 3. at line starts
        dot_num_pattern = r'(?=(?:^|\n)\s*(\d{1,3})\.\s+[A-Z])'
        splits_dot = re.split(dot_num_pattern, text)
        if len(splits_dot) > 3:
            entries = []
            for i in range(1, len(splits_dot), 2):
                num = splits_dot[i]
                body = splits_dot[i+1] if i+1 < len(splits_dot) else ""
                entries.append((f"{num}.", f"{num}. {body}".strip()))
            return entries

        # Pattern 3: (1), (2), (3)
        paren_num_pattern = r'(?=(?:^|\n)\s*\((\d{1,3})\)\s+[A-Z])'
        splits_paren = re.split(paren_num_pattern, text)
        if len(splits_paren) > 3:
            entries = []
            for i in range(1, len(splits_paren), 2):
                num = splits_paren[i]
                body = splits_paren[i+1] if i+1 < len(splits_paren) else ""
                entries.append((f"({num})", f"({num}) {body}".strip()))
            return entries

        # Pattern 4: Author-Year references (e.g., "Vaswani, A. et al. (2017)" or "Smith, J. (2020)")
        author_year_pattern = r'(?=(?:^|\n)\s*([A-Z][a-zA-Z\s\.\,\-]+(?:\([12]\d{3}\)|[12]\d{3}\b)))'
        splits_ay = re.split(author_year_pattern, text)
        if len(splits_ay) > 3:
            entries = []
            for i in range(1, len(splits_ay), 2):
                marker = splits_ay[i]
                body = splits_ay[i+1] if i+1 < len(splits_ay) else ""
                entries.append((marker[:20], f"{marker} {body}".strip()))
            return entries

        # Pattern 5: Line by line grouping if formatted with paragraph breaks
        paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 20]
        if len(paragraphs) >= 2:
            return [(f"#{i+1}", p) for i, p in enumerate(paragraphs)]

        # Fallback single block or lines
        lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 25]
        return [(f"#{i+1}", l) for i, l in enumerate(lines)]

    def _layout_entries(self, pages):
        active = False
        entries = []
        current = []
        hanging = 0
        for page in pages:
            lines = page.get('lines', [])
            if not lines:
                continue
            # Determine the left edge of each text column on this page.
            xs = sorted(l['bbox'][0] for l in lines if len(l['text']) > 20)
            if not xs:
                continue
            left = xs[0]
            right_xs = [x for x in xs if x > left + 160]
            right = min(right_xs) if right_xs else None
            for line in lines:
                text = line['text']
                if re.fullmatch(r'(?:\d+\.?\s+)?(?:References|Bibliography|Works Cited)', text, re.I):
                    active = True
                    continue
                if not active:
                    continue
                if re.match(r'^(?:Appendix\b|[A-Z](?:\.\d+)?\s+(?:Additional|Implementation|Experiments))', text):
                    if current:
                        entries.append('\n'.join(current))
                    return entries if hanging >= 3 else []
                x = line['bbox'][0]
                margin = right if right is not None and x >= right - 2 else left
                indented = x - margin > 5
                hanging += int(indented)
                starts = not indented and bool(re.match(r'^[A-Z][A-Za-z .\-]+', text))
                if starts and current:
                    entries.append('\n'.join(current))
                    current = []
                current.append(text)
        if current:
            entries.append('\n'.join(current))
        return entries if hanging >= 3 and len(entries) >= 2 else []

    def _clean_reference_text(self, text: str) -> str:
        # Un-hyphenate words broken across lines (e.g., "atten-\ntion" -> "attention")
        cleaned = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        # Collapse newlines and whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        # Remove trailing page numbers/footers if detected
        cleaned = re.sub(r'\s+\d+\s*$', '', cleaned)
        return cleaned.strip()

reference_detector = ReferenceDetector()
