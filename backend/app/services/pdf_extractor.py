import pymupdf as fitz
from pathlib import Path
from typing import Dict, List, Any
import re
import unicodedata
from threading import Lock

class PDFExtractor:
    """Extracts text, layout structure, font metadata, and sections from PDF research papers."""

    _lock = Lock()

    def extract_paper_content(self, file_path: str | Path) -> Dict[str, Any]:
        # PyMuPDF must not be used concurrently across worker threads.
        with self._lock:
            return self._extract_paper_content(file_path)

    def _extract_paper_content(self, file_path: str | Path) -> Dict[str, Any]:
        doc = fitz.open(stream=Path(file_path).read_bytes(), filetype='pdf')
        if doc.needs_pass:
            doc.close()
            raise ValueError("Password-protected PDFs are not supported. Upload an unlocked copy.")
        page_count = len(doc)
        pages_text: List[Dict[str, Any]] = []
        all_blocks: List[Dict[str, Any]] = []
        full_text_list: List[str] = []

        for page_num in range(page_count):
            page = doc[page_num]
            # Extract text blocks with font details
            text_dict = page.get_text("dict")
            ordered_lines = self._reading_order(text_dict, page.rect.width, page.rect.height)
            page_text = '\n'.join(line['text'] for line in ordered_lines)
            page_text = re.sub(r'(?<=\w)-\n(?=[a-z])', '', page_text)
            full_text_list.append(page_text)

            blocks_on_page = []
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    block_text = ""
                    font_sizes = []
                    font_flags = []
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            block_text += span.get("text", "") + " "
                            font_sizes.append(span.get("size", 10.0))
                            font_flags.append(span.get("flags", 0))

                    clean_text = block_text.strip()
                    if clean_text:
                        avg_font = sum(font_sizes) / len(font_sizes) if font_sizes else 10.0
                        max_font = max(font_sizes) if font_sizes else 10.0
                        blocks_on_page.append({
                            "page": page_num + 1,
                            "text": unicodedata.normalize('NFKC', clean_text),
                            "lines": [{'text': unicodedata.normalize('NFKC', ''.join(s.get('text', '') for s in line.get('spans', []))), 'bbox': line.get('bbox', [])} for line in block['lines']],
                            "bbox": block.get("bbox", [0, 0, 0, 0]),
                            "avg_font_size": avg_font,
                            "max_font_size": max_font,
                            "is_bold": any(f & 16 != 0 for f in font_flags),
                        })
            
            pages_text.append({
                "page_number": page_num + 1,
                "text": page_text,
                "blocks": blocks_on_page,
                "lines": ordered_lines
            })
            all_blocks.extend(blocks_on_page)

        full_text = "\n\n".join(full_text_list)
        
        # Calculate general stats
        words = full_text.split()
        word_count = len(words)
        char_count = len(full_text)
        reading_time_min = round(word_count / 200, 1)  # average 200 WPM

        # Estimate tables and figures
        figures_count = len(re.findall(r'\b(Figure|Fig\.)\s+\d+', full_text, re.IGNORECASE))
        tables_count = len(re.findall(r'\bTable\s+\d+', full_text, re.IGNORECASE))

        stats = {
            "page_count": page_count,
            "word_count": word_count,
            "character_count": char_count,
            "reading_time_minutes": reading_time_min,
            "figures_count": figures_count,
            "tables_count": tables_count,
        }

        # Extract embedded metadata if any
        meta = doc.metadata or {}
        embedded_metadata = {
            "title": meta.get("title", ""),
            "author": meta.get("author", ""),
            "subject": meta.get("subject", ""),
            "keywords": meta.get("keywords", ""),
            "creator": meta.get("creator", ""),
            "producer": meta.get("producer", ""),
            "creation_date": meta.get("creationDate", ""),
        }

        doc.close()
        if not full_text.strip():
            raise ValueError("This PDF has no extractable text. Scanned documents require OCR before upload.")

        return {
            "full_text": full_text,
            "pages": pages_text,
            "blocks": all_blocks,
            "stats": stats,
            "embedded_metadata": embedded_metadata,
        }

    @staticmethod
    def _reading_order(text_dict, width, height):
        lines = []
        for block in text_dict.get('blocks', []):
            for line in block.get('lines', []):
                text = unicodedata.normalize('NFKC', ''.join(s.get('text', '') for s in line.get('spans', []))).strip()
                bbox = line.get('bbox', [0, 0, width, height])
                if text and not (bbox[1] > height * .9 and text.isdigit()):
                    lines.append({'text': text, 'bbox': bbox})
        # A clear central gutter identifies two-column body text. Full-width
        # title/author lines precede the columns; each column reads top to bottom.
        mid = width / 2
        left = [l for l in lines if l['bbox'][0] < mid and l['bbox'][2] < mid + 3]
        right = [l for l in lines if l['bbox'][0] >= mid]
        if len(left) >= 8 and len(right) >= 8:
            others = [l for l in lines if l not in left and l not in right]
            top = min(l['bbox'][1] for l in right)
            headers = [l for l in others if l['bbox'][1] < top]
            tail = [l for l in others if l not in headers]
            ordered = sorted(headers, key=lambda l: (round(l['bbox'][1] / 2), l['bbox'][0])) + sorted(left, key=lambda l: (round(l['bbox'][1] / 2), l['bbox'][0])) + sorted(right, key=lambda l: (round(l['bbox'][1] / 2), l['bbox'][0])) + sorted(tail, key=lambda l: (round(l['bbox'][1] / 2), l['bbox'][0]))
        else:
            ordered = sorted(lines, key=lambda l: (round(l['bbox'][1] / 2), l['bbox'][0]))
        merged = []
        for line in ordered:
            if merged and abs(line['bbox'][1] - merged[-1]['bbox'][1]) < 2 and 0 <= line['bbox'][0] - merged[-1]['bbox'][2] < 25:
                merged[-1]['text'] += ' ' + line['text']
                merged[-1]['bbox'] = [merged[-1]['bbox'][0], min(merged[-1]['bbox'][1], line['bbox'][1]), line['bbox'][2], max(merged[-1]['bbox'][3], line['bbox'][3])]
            else:
                merged.append(dict(line))
        return merged

pdf_extractor = PDFExtractor()
