import re
from app.services.normalization import normalize_doi, normalize_reference_id
from typing import Dict, List, Any, Optional, Tuple

class ReferenceParser:
    """Parses raw reference citations into structured academic metadata."""

    DOI_REGEX = re.compile(r'(?:https?://(?:dx\.)?doi\.org/|doi:\s*|DOI:\s*)?(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)', re.IGNORECASE)
    URL_REGEX = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+', re.IGNORECASE)
    YEAR_REGEX = re.compile(r'\b(18\d{2}|19\d{2}|20\d{2})(?=[a-z]?\b)')
    PAGES_REGEX = re.compile(r'\b(?:pp\.?|pages|p\.)\s*(\d+[\s–\-]+\d+|\d+)', re.IGNORECASE)
    VOLUME_ISSUE_REGEX = re.compile(r'\b(\d+)\s*\(([\d\-]+)\)|\bvol\.?\s*(\d+)(?:,\s*no\.?\s*(\d+))?', re.IGNORECASE)

    def parse_reference(self, raw_text: str, ref_number: int = 1) -> Dict[str, Any]:
        text = raw_text.strip()
        
        # 1. Strip leading reference marker e.g., "[1]", "1.", "(1)"
        cleaned_text = re.sub(r'^(?:\[\d+\]|\d+\.|\(\d+\))\s*', '', text)

        # 2. Extract DOI and URL
        doi_match = self.DOI_REGEX.search(cleaned_text)
        doi = normalize_doi(doi_match.group(1)) if doi_match else None

        url_match = self.URL_REGEX.search(cleaned_text)
        url = url_match.group(0).rstrip('.,;)') if url_match else None
        if not url and doi:
            url = f"https://doi.org/{doi}"

        # 3. Extract Year
        year = None
        # Priority 1: Year in parentheses e.g. (2017)
        year_paren_match = re.search(r'\((19\d{2}|20\d{2})[a-z]?\)', cleaned_text)
        if year_paren_match:
            year = int(year_paren_match.group(1))
        else:
            leading_year = re.search(r'^.{3,500}?\.\s*((?:19|20)\d{2})[a-z]?\.\s+', cleaned_text)
            # Priority 2: Any 4 digit year
            all_years = self.YEAR_REGEX.findall(cleaned_text)
            if all_years:
                valid_years = [int(y) for y in all_years if 1800 <= int(y) <= 2030]
                if valid_years:
                    year = int(leading_year.group(1)) if leading_year else valid_years[-1]

        # 4. Extract Pages, Volume, Issue
        pages = None
        pages_match = self.PAGES_REGEX.search(cleaned_text)
        if pages_match:
            pages = pages_match.group(1).replace(' ', '')

        volume = None
        issue = None
        vol_match = self.VOLUME_ISSUE_REGEX.search(cleaned_text)
        if vol_match:
            if vol_match.group(1):
                volume = vol_match.group(1)
                issue = vol_match.group(2)
            elif vol_match.group(3):
                volume = vol_match.group(3)
                issue = vol_match.group(4)

        # 5. Extract Title and Authors
        title, authors, venue, journal, conference, publisher = self._extract_title_authors_venue(cleaned_text, year)

        # 6. Detect citation format
        citation_format = self._detect_format(text)

        return {
            "reference_number": normalize_reference_id(ref_number),
            "raw_text": text,
            "title": title,
            "authors": authors,
            "year": year,
            "year_suffix": (re.search(rf'\b{year}([a-z])\b', cleaned_text).group(1) if year and re.search(rf'\b{year}([a-z])\b', cleaned_text) else ''),
            "venue": venue,
            "journal": journal,
            "conference": conference,
            "publisher": publisher,
            "volume": volume,
            "issue": issue,
            "pages": pages,
            "doi": doi,
            "url": url,
            "citation_format": citation_format,
        }

    def _extract_title_authors_venue(self, text: str, year: Optional[int]) -> Tuple[Optional[str], List[str], Optional[str], Optional[str], Optional[str], Optional[str]]:
        title = None
        authors = []
        venue = None
        journal = None
        conference = None
        publisher = None

        # Strategy A: Check for quoted title: "Title..." or “Title...” or «Title»
        quoted_title_match = re.search(r'["“«]([^"”»]{5,250})["”»]', text)
        if quoted_title_match:
            title = quoted_title_match.group(1).strip()
            # Everything before the quote is authors
            pre_quote = text[:quoted_title_match.start()].strip(" ,.")
            authors = self._parse_authors_list(pre_quote)
            # Everything after the quote is venue/proceedings/pages/year
            post_quote = text[quoted_title_match.end():].strip(" ,.")
            venue, journal, conference, publisher = self._parse_venue_string(post_quote)
            return title, authors, venue, journal, conference, publisher

        # Strategy B: APA / Harvard format: Authors (Year). Title. Venue...
        acl_match = re.match(r'^(.+?)\.\s*((?:19|20)\d{2})[a-z]?\.\s+(.+)$', text)
        if acl_match:
            authors = self._parse_authors_list(acl_match.group(1))
            parts = re.split(r'(?:\.\s+(?=[A-Z])|[.?]\s+(?=(?:arXiv|CoRR|In\s)))', acl_match.group(3), maxsplit=1)
            title = parts[0].rstrip('.')
            venue, journal, conference, publisher = self._parse_venue_string(parts[1] if len(parts) > 1 else '')
            return title, authors, venue, journal, conference, publisher
        if year:
            year_pattern = rf'\({year}[a-z]?\)'
            year_match = re.search(year_pattern, text)
            if year_match:
                author_part = text[:year_match.start()].strip(" ,.")
                authors = self._parse_authors_list(author_part)
                rest = text[year_match.end():].strip(" .:,-")
                # Title is usually before the next period or comma + italicized venue
                parts = re.split(r'\.\s+', rest, maxsplit=1)
                if parts:
                    title = parts[0].strip()
                    if len(parts) > 1:
                        venue, journal, conference, publisher = self._parse_venue_string(parts[1])
                    return title, authors, venue, journal, conference, publisher

        # Strategy C: Standard IEEE / ACM delimiter approach (Authors. Title. Venue, Year.)
        segments = [s.strip() for s in re.split(r'\.\s+', text) if s.strip()]
        if len(segments) >= 3:
            # Segment 0: Authors
            authors = self._parse_authors_list(segments[0])
            # Segment 1: Title
            title = segments[1]
            # Remaining segments: Venue, publisher, etc.
            venue_str = ". ".join(segments[2:])
            venue, journal, conference, publisher = self._parse_venue_string(venue_str)
            return title, authors, venue, journal, conference, publisher
        elif len(segments) == 2:
            authors = self._parse_authors_list(segments[0])
            title = segments[1]
            return title, authors, None, None, None, None

        # Strategy D: Fallback to entire text or basic heuristic
        title = text
        return title, ["Unknown Author"], None, None, None, None

    def _parse_authors_list(self, author_str: str) -> List[str]:
        if not author_str:
            return ["Unknown Author"]
        # Remove "et al."
        cleaned = re.sub(r'\bet\s+al\.?', '', author_str, flags=re.IGNORECASE)
        # Split by 'and', '&', semicolons, or commas (handling initials like 'Vaswani, A.')
        parts = re.split(r'[,;]|\band\b|&', cleaned)
        authors = []
        buffer = ""
        for p in parts:
            item = p.strip()
            if not item:
                continue
            # If item is just an initial or short token, combine with buffer
            if len(item) <= 3 and buffer:
                buffer += ", " + item
                authors.append(buffer)
                buffer = ""
            elif len(item.split()) == 1 and not buffer and len(authors) > 0 and len(item) <= 3:
                # Initial belonging to previous surname
                authors[-1] += ", " + item
            else:
                if buffer:
                    authors.append(buffer)
                buffer = item
        if buffer:
            authors.append(buffer)

        cleaned_authors = []
        for a in authors:
            c = re.sub(r'[\d\*†‡§\^]', '', a).strip(" ,.")
            if len(c) >= 2 and not any(k in c.lower() for k in ["proceedings", "conference", "arxiv", "journal", "in:"]):
                cleaned_authors.append(c)

        return cleaned_authors if cleaned_authors else ["Unknown Author"]

    def _parse_venue_string(self, venue_str: str) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        if not venue_str:
            return None, None, None, None
        
        # Remove DOI, URLs, page numbers, years
        cleaned = self.DOI_REGEX.sub('', venue_str)
        cleaned = self.URL_REGEX.sub('', cleaned)
        cleaned = self.PAGES_REGEX.sub('', cleaned)
        cleaned = re.sub(r'\b(19\d{2}|20\d{2})\b', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip(" ,.;:")

        journal = None
        conference = None
        publisher = None

        if re.search(r'\b(In\s+Proceedings|Proc\.|Conference|Symposium|Workshop|NeurIPS|ICML|CVPR|ICLR|ACL|EMNLP|KDD|AAAI)\b', cleaned, re.IGNORECASE):
            conference = cleaned
        elif re.search(r'\b(Journal|Transactions|Trans\.|Letters|Nature|Science|Review|Communications)\b', cleaned, re.IGNORECASE):
            journal = cleaned

        if re.search(r'\b(IEEE|ACM|Springer|Elsevier|Wiley|Nature Publishing|AAAS|MIT Press)\b', cleaned, re.IGNORECASE):
            publisher = re.search(r'\b(IEEE|ACM|Springer|Elsevier|Wiley|Nature Publishing|AAAS|MIT Press)\b', cleaned, re.IGNORECASE).group(0)

        return (cleaned if cleaned else None), journal, conference, publisher

    def _detect_format(self, text: str) -> str:
        if text.startswith("[") and re.match(r'^\[\d+\]', text):
            return "IEEE"
        elif re.match(r'^\d+\.', text):
            return "numbered"
        elif re.search(r'\([12]\d{3}\)', text):
            return "APA"
        elif re.search(r'["“][^"”]+["”]', text):
            return "MLA"
        return "numbered"

reference_parser = ReferenceParser()
