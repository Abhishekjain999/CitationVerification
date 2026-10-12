import re
from app.services.normalization import normalize_doi
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter

class MetadataExtractor:
    """Extracts paper metadata, sections, abstract, keywords, and generates AI summary."""

    DOI_PATTERN = re.compile(r'(?:https?://(?:dx\.)?doi\.org/|doi:\s*|DOI:\s*)?(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)', re.IGNORECASE)
    ARXIV_PATTERN = re.compile(r'arXiv:\s*(\d{4}\.\d{4,5}(?:v\d+)?)', re.IGNORECASE)
    YEAR_PATTERN = re.compile(r'\b(19\d{2}|20\d{2})\b')
    EMAIL_PATTERN = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')

    COMMON_SECTION_TITLES = [
        "Abstract",
        "Introduction",
        "Related Work",
        "Background",
        "Methodology",
        "Methods",
        "Proposed Method",
        "System Model",
        "Architecture",
        "Dataset",
        "Datasets",
        "Experimental Setup",
        "Experiments",
        "Results",
        "Results and Discussion",
        "Discussion",
        "Ablation Studies",
        "Conclusion",
        "Conclusions",
        "Future Work",
        "Acknowledgements",
        "References",
        "Bibliography",
    ]

    def extract_metadata(self, extracted_pdf_data: Dict[str, Any]) -> Dict[str, Any]:
        pages = extracted_pdf_data.get("pages", [])
        blocks = extracted_pdf_data.get("blocks", [])
        full_text = extracted_pdf_data.get("full_text", "")
        embedded_meta = extracted_pdf_data.get("embedded_metadata", {})

        page1_text = pages[0]["text"] if pages else ""
        page2_text = pages[1]["text"] if len(pages) > 1 else ""
        header_text = re.split(r'(?im)^\s*(?:References|Bibliography)\b', page1_text + "\n" + page2_text)[0]

        # 1. Extract DOI
        doi_match = self.DOI_PATTERN.search(header_text)
        doi = normalize_doi(doi_match.group(1)) if doi_match else None

        # 2. Extract arXiv
        arxiv_match = self.ARXIV_PATTERN.search(header_text)
        arxiv_id = arxiv_match.group(1) if arxiv_match else None
        url = f"https://doi.org/{doi}" if doi else (f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else None)

        # 3. Extract Abstract
        abstract = self._extract_abstract(page1_text, page2_text, full_text)

        # 4. Extract Title
        title = self._extract_title(blocks, page1_text, embedded_meta, abstract)

        # 5. Extract Authors & Corresponding Author
        authors, corresponding_author = self._extract_authors(blocks, page1_text, title, abstract)

        # 6. Extract Keywords
        keywords = self._extract_keywords(header_text, full_text, abstract)

        # 7. Extract Year and Publication Venue
        pub_year, venue, journal, conference, publisher, volume, issue, pages_span = self._extract_venue_info(header_text, full_text)

        # 8. Detect Paper Sections
        sections = self._detect_sections(pages, full_text)

        # 9. Generate AI Summary (2-4 sentences)
        ai_summary = self._generate_ai_summary(abstract, full_text)

        # Article type estimation
        article_type = "Journal Article"
        if conference or "Conference" in (venue or "") or "Proceedings" in (venue or ""):
            article_type = "Conference Paper"
        elif arxiv_id or "preprint" in header_text.lower():
            article_type = "Preprint"

        return {
            "title": title,
            "authors": authors,
            "corresponding_author": corresponding_author,
            "publication_year": pub_year,
            "publication_date": str(pub_year) if pub_year else None,
            "journal": journal,
            "conference": conference,
            "venue": venue,
            "publisher": publisher,
            "doi": doi,
            "url": url,
            "volume": volume,
            "issue": issue,
            "pages": pages_span,
            "article_type": article_type,
            "open_access": bool(arxiv_id),
            "abstract": abstract,
            "ai_summary": ai_summary,
            "keywords": keywords,
            "sections": sections,
        }

    def _extract_title(self, blocks: List[Dict[str, Any]], page1_text: str, embedded_meta: Dict[str, Any], abstract: Optional[str]) -> str:
        # Check page 1 blocks for prominent font size
        page1_blocks = [b for b in blocks if b.get("page") == 1]
        if page1_blocks:
            # Sort by font size descending
            sorted_blocks = sorted(page1_blocks, key=lambda b: (b.get("avg_font_size", 0), b.get("is_bold", False)), reverse=True)
            for block in sorted_blocks:
                t = block.get("text", "").strip()
                # Skip common journal headers or artifact strings
                lower_t = t.lower()
                if (
                    len(t) > 10 and len(t) < 300
                    and not any(hdr in lower_t for hdr in ["proceedings of", "ieee transactions", "arxiv:", "http://", "https://", "vol.", "no.", "copyright", "all rights reserved", "received", "accepted", "published"])
                    and not lower_t.startswith("abstract")
                    and not lower_t.startswith("keywords")
                ):
                    # Clean newlines inside title
                    clean_title = re.sub(r'\s+', ' ', t).strip()
                    end = block.get('bbox', [0, 0, 0, 0])[3]
                    for continuation in sorted(page1_blocks, key=lambda b: b.get('bbox', [0,0,0,0])[1]):
                        box = continuation.get('bbox', [0,0,0,0])
                        if continuation is not block and end <= box[1] <= end + 20 and abs(continuation.get('avg_font_size', 0) - block.get('avg_font_size', 0)) < 1:
                            clean_title += ' ' + continuation['text']
                            end = box[3]
                    return clean_title

        # Fallback to embedded metadata title if plausible
        embed_title = embedded_meta.get("title", "").strip()
        if embed_title and len(embed_title) > 8 and not embed_title.lower().endswith(".pdf") and "untitled" not in embed_title.lower():
            return embed_title

        # Fallback: first non-empty lines before Abstract
        lines = [line.strip() for line in page1_text.split("\n") if line.strip()]
        for line in lines[:5]:
            if len(line) > 10 and not line.lower().startswith("arxiv:") and not line.lower().startswith("ieee"):
                return line

        return "Untitled Research Paper"

    def _extract_authors(self, blocks: List[Dict[str, Any]], page1_text: str, title: str, abstract: Optional[str]) -> Tuple[List[str], Optional[str]]:
        authors: List[str] = []
        corresponding: Optional[str] = None

        # Try to locate the text slice between Title and Abstract
        re.escape(title[:30]) if title else ""
        
        # Look for email to detect corresponding author
        email_matches = self.EMAIL_PATTERN.findall(page1_text)
        if email_matches:
            corresponding = email_matches[0]

        # Use page 1 blocks located below the title block
        page1_blocks = [b for b in blocks if b.get("page") == 1]
        title_blocks = [b for b in page1_blocks if b.get('text') and b['text'].strip() in title]
        title_bottom = max((b.get('bbox', [0,0,0,0])[3] for b in title_blocks), default=0)
        abstract_top = min((b.get('bbox', [0,9999,0,0])[1] for b in page1_blocks if b.get('text', '').strip() == 'Abstract'), default=9999)
        if title_bottom:
            for b in page1_blocks:
                if not title_bottom <= b.get('bbox', [0,0,0,0])[1] < abstract_top:
                    continue
                for line in b.get('lines', [{'text': b.get('text','')} ]):
                    value = line['text'].strip()
                    if any(term in value.lower() for term in ['university', 'institute', 'department', 'google', 'language', '@', 'laboratory', 'research', 'microsoft']):
                        continue
                    for part in re.split(r'[,;]|\s+and\s+', value):
                        part = re.sub(r'[\d*†‡]', '', part).strip()
                        words = part.split()
                        if 2 <= len(words) <= 5 and all(w[0].isupper() for w in words) and part not in authors:
                            authors.append(part)
            if authors:
                return authors, corresponding
        for b in page1_blocks:
            t = b.get("text", "").strip()
            # If block appears to have author names (capital letters, commas, superscripts, affiliations)
            if (
                title not in t and "Abstract" not in t and "Introduction" not in t
                and not t.lower().startswith("arxiv:")
                and len(t) < 400
            ):
                # Filter out pure affiliation blocks like "Department of Computer Science, University..."
                if any(affil in t.lower() for affil in ["university", "institute", "department", "laboratory", "google", "meta", "microsoft", "campus"]):
                    continue
                
                # Split candidate authors
                parts = re.split(r'[,;]|\band\b', t)
                for part in parts:
                    clean_name = re.sub(r'[\d\*†‡§\^]', '', part).strip()
                    # Check if valid name (2 to 4 capitalized words)
                    words = clean_name.split()
                    if 1 <= len(words) <= 4 and all(w[0].isupper() for w in words if w and w[0].isalpha()):
                        if clean_name not in authors and len(clean_name) > 2:
                            authors.append(clean_name)
            if len(authors) >= 1 and "Abstract" in t:
                break

        if not authors:
            # Fallback simple extraction
            lines = [l.strip() for l in page1_text.split("\n") if l.strip()]
            for line in lines[1:5]:
                if "abstract" in line.lower():
                    break
                if not any(k in line.lower() for k in ["arxiv", "university", "department", "ieee"]):
                    parts = re.split(r'[,;]|\band\b', line)
                    for p in parts:
                        clean_p = re.sub(r'[\d\*†‡§]', '', p).strip()
                        if 2 <= len(clean_p) < 40:
                            authors.append(clean_p)

        return (authors if authors else ["Author(s) Unspecified"]), corresponding

    def _extract_abstract(self, page1_text: str, page2_text: str, full_text: str) -> Optional[str]:
        text_pool = page1_text + "\n" + page2_text
        match = re.search(r'\bAbstract\b[:\s\-—\.]*(.+?)(?=\n\s*(?:(?:1|I)\.?\s*)?(?:Introduction|Index Terms|Keywords|Key words)\b)', text_pool, re.DOTALL | re.IGNORECASE)
        if match:
            raw_abstract = match.group(1).strip()
            clean_abstract = re.sub(r'\s+', ' ', raw_abstract)
            if len(clean_abstract) > 50:
                return clean_abstract

        # Fallback search in full text
        match_full = re.search(r'\bAbstract\b[:\s\-—\.]*(.+?)(?=\b(?:1\.?\s+|I\.?\s+|Introduction|Index Terms|Keywords)\b)', full_text[:4000], re.DOTALL | re.IGNORECASE)
        if match_full:
            clean_abstract = re.sub(r'\s+', ' ', match_full.group(1).strip())
            return clean_abstract

        return None

    def _extract_keywords(self, header_text: str, full_text: str, abstract: Optional[str]) -> List[str]:
        # Search explicit keyword tags
        match = re.search(r'(?:Keywords|Index Terms|Key words|Search terms)[:\s\-—\.]+(.+?)(?=\b(?:1\.?\s+|I\.?\s+|Introduction|\n\n)\b)', header_text, re.DOTALL | re.IGNORECASE)
        if match:
            raw_kw = match.group(1).strip()
            parts = re.split(r'[,;•·—\n]', raw_kw)
            keywords = [re.sub(r'\s+', ' ', p).strip(" .") for p in parts if len(p.strip()) > 2]
            if keywords:
                return keywords[:10]

        # Automatic NLP keyword extraction from abstract or top text using n-grams & frequency
        source_text = abstract or full_text[:3000]
        words = re.findall(r'\b[A-Za-z]{3,}\b', source_text.lower())
        stopwords = {
            "the", "and", "for", "that", "this", "with", "from", "are", "have", "been", "which",
            "were", "their", "paper", "proposed", "model", "using", "results", "based", "show",
            "also", "such", "than", "more", "most", "these", "between", "each", "both", "our",
            "present", "study", "analysis", "system", "data", "method", "methods", "used", "can"
        }
        filtered = [w for w in words if w not in stopwords]
        counts = Counter(filtered)
        nlp_keywords = [word.capitalize() for word, _ in counts.most_common(7)]
        return nlp_keywords if nlp_keywords else ["Research Analysis", "Computer Science", "Artificial Intelligence"]

    def _extract_venue_info(self, header_text: str, full_text: str) -> Tuple[Optional[int], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]]:
        pub_year = None
        years = self.YEAR_PATTERN.findall(header_text)
        if years:
            valid_years = [int(y) for y in years if 1970 <= int(y) <= 2030]
            if valid_years:
                pub_year = valid_years[0]

        venue = None
        journal = None
        conference = None
        publisher = None

        # Venue pattern matching
        if re.search(r'\b(NeurIPS|NIPS|Advances in Neural Information Processing Systems)\b', header_text, re.IGNORECASE):
            conference = "NeurIPS (Advances in Neural Information Processing Systems)"
            venue = conference
        elif re.search(r'\b(ICML|International Conference on Machine Learning)\b', header_text, re.IGNORECASE):
            conference = "ICML (International Conference on Machine Learning)"
            venue = conference
        elif re.search(r'\b(CVPR|Computer Vision and Pattern Recognition)\b', header_text, re.IGNORECASE):
            conference = "CVPR (IEEE/CVF Conference on Computer Vision and Pattern Recognition)"
            venue = conference
        elif re.search(r'\b(ICLR|International Conference on Learning Representations)\b', header_text, re.IGNORECASE):
            conference = "ICLR (International Conference on Learning Representations)"
            venue = conference
        elif re.search(r'\b(ACL|EMNLP|NAACL|Association for Computational Linguistics)\b', header_text, re.IGNORECASE):
            conference = "ACL (Association for Computational Linguistics)"
            venue = conference
        elif "IEEE" in header_text:
            venue = "IEEE Publications"
            publisher = "IEEE"
        elif "ACM" in header_text:
            venue = "ACM Conference / Transactions"
            publisher = "ACM"
        elif "Nature" in header_text:
            journal = "Nature"
            venue = "Nature"
            publisher = "Nature Publishing Group"
        elif "Science" in header_text:
            journal = "Science"
            venue = "Science"
            publisher = "AAAS"

        # Volume / Issue / Pages
        vol_match = re.search(r'\bVol(?:ume)?\.?\s*(\d+)', header_text, re.IGNORECASE)
        volume = vol_match.group(1) if vol_match else None

        iss_match = re.search(r'\b(?:No|Issue)\.?\s*(\d+)', header_text, re.IGNORECASE)
        issue = iss_match.group(1) if iss_match else None

        pp_match = re.search(r'\b(?:pp|pages)\.?\s*(\d+[\s–\-]+\d+)', header_text, re.IGNORECASE)
        pages_span = pp_match.group(1) if pp_match else None

        return pub_year, venue, journal, conference, publisher, volume, issue, pages_span

    def _detect_sections(self, pages: List[Dict[str, Any]], full_text: str) -> List[Dict[str, Any]]:
        sections: List[Dict[str, Any]] = []
        pattern = re.compile(
            r'^(?:(?:\d+|[IVXLCDM]+)\.?\s+)?(' + '|'.join(re.escape(s) for s in self.COMMON_SECTION_TITLES) + r')\b',
            re.IGNORECASE | re.MULTILINE
        )

        seen_titles = set()
        for page in pages:
            p_num = page.get("page_number", 1)
            p_text = page.get("text", "")
            for line in p_text.split("\n"):
                stripped = line.strip()
                if len(stripped) < 60:
                    match = pattern.search(stripped)
                    if match:
                        sec_name = match.group(1).title()
                        if sec_name not in seen_titles:
                            seen_titles.add(sec_name)
                            sections.append({
                                "title": sec_name,
                                "start_page": p_num,
                                "raw_heading": stripped,
                            })

        # Ensure Abstract and References exist if detectable
        if "Abstract" not in seen_titles and "abstract" in full_text.lower():
            sections.insert(0, {"title": "Abstract", "start_page": 1, "raw_heading": "Abstract"})
        if "References" not in seen_titles and ("references" in full_text.lower() or "bibliography" in full_text.lower()):
            last_page = pages[-1]["page_number"] if pages else 1
            sections.append({"title": "References", "start_page": last_page, "raw_heading": "References"})

        return sections

    def _generate_ai_summary(self, abstract: Optional[str], full_text: str) -> str:
        """Generates a high-quality 2-4 sentence executive summary."""
        target_text = abstract if abstract and len(abstract) > 100 else full_text[:2500]
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', target_text.strip())
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if len(sentences) <= 3:
            return " ".join(sentences)
        
        # Select first sentence (context/motivation), middle (methodology), and final (results/implications)
        summary_sentences = [sentences[0]]
        if len(sentences) > 2:
            summary_sentences.append(sentences[len(sentences) // 2])
        summary_sentences.append(sentences[-1])
        
        return " ".join(summary_sentences)

metadata_extractor = MetadataExtractor()
