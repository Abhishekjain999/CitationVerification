from pathlib import Path
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from datetime import datetime
from zoneinfo import ZoneInfo
from html import escape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def report_fonts():
    """Embed available Unicode fonts so author names survive PDF rendering."""
    options = [
        (Path('C:/Windows/Fonts'), ('arial.ttf', 'arialbd.ttf', 'ariali.ttf', 'arialbi.ttf')),
        (Path('/usr/share/fonts/truetype/dejavu'), ('DejaVuSans.ttf', 'DejaVuSans-Bold.ttf', 'DejaVuSans-Oblique.ttf', 'DejaVuSans-BoldOblique.ttf')),
    ]
    names = ('RG', 'RG-Bold', 'RG-Italic', 'RG-BoldItalic')
    for directory, files in options:
        if all((directory / file).exists() for file in files):
            for name, file in zip(names, files):
                if name not in pdfmetrics.getRegisteredFontNames():
                    pdfmetrics.registerFont(TTFont(name, str(directory / file)))
            pdfmetrics.registerFontFamily('RG', normal=names[0], bold=names[1], italic=names[2], boldItalic=names[3])
            return names[0], names[1], names[2]
    return 'Helvetica', 'Helvetica-Bold', 'Helvetica-Oblique'

class ReportGenerator:
    """Generates a publication-grade PDF integrity and reference verification report."""

    def generate_pdf_report(self, paper_data: Dict[str, Any], output_path: Path) -> Path:
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        regular_font, bold_font, italic_font = report_fonts()
        
        # Custom palette
        PRIMARY = colors.HexColor("#1e293b")   # Slate 800
        ACCENT = colors.HexColor("#2563eb")    # Blue 600
        BG_LIGHT = colors.HexColor("#f8fafc")  # Slate 50
        BORDER_COLOR = colors.HexColor("#e2e8f0")

        # Custom Typography
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName=bold_font,
            fontSize=22,
            leading=26,
            textColor=PRIMARY,
        )

        sub_style = ParagraphStyle(
            'SubTitle',
            parent=styles['Normal'],
            fontName=regular_font,
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#64748b"),
        )

        section_heading = ParagraphStyle(
            'SecHeading',
            parent=styles['Heading2'],
            fontName=bold_font,
            fontSize=14,
            leading=18,
            textColor=PRIMARY,
            spaceBefore=12,
            spaceAfter=6,
        )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName=regular_font,
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#334155"),
        )

        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontName=italic_font,
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#64748b"),
        )

        elements = []
        def safe(value):
            return escape(str(value or ''))

        # 1. Header Banner
        header_table_data = [
            [
                Paragraph("<b>RESEARCHGUARD</b><br/><font size=9 color='#64748b'>Academic Research Paper & Reference Integrity Verification Report</font>", title_style),
                Paragraph(f"<b>Generated:</b> {datetime.now(ZoneInfo('Asia/Calcutta')).strftime('%B %d, %Y')}<br/><b>Status:</b> Completed", sub_style)
            ]
        ]
        header_table = Table(header_table_data, colWidths=[380, 160])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceBefore=4, spaceAfter=14))

        # 2. Paper Metadata Card
        p_title = safe(paper_data.get("title") or "Untitled Paper")
        p_authors = safe(", ".join(str(a) for a in paper_data.get("authors", []))) if paper_data.get("authors") else "Author(s) not listed"
        p_year = str(paper_data.get("publication_year") or "N/A")
        p_venue = safe(paper_data.get("venue") or paper_data.get("journal") or paper_data.get("conference") or "N/A")
        p_doi = safe(paper_data.get("doi") or "N/A")

        meta_rows = [
            [Paragraph("<b>Paper Title:</b>", body_style), Paragraph(f"<b>{p_title}</b>", body_style)],
            [Paragraph("<b>Authors:</b>", body_style), Paragraph(p_authors, body_style)],
            [Paragraph("<b>Venue / Journal:</b>", body_style), Paragraph(p_venue, body_style)],
            [Paragraph("<b>Publication Year:</b>", body_style), Paragraph(p_year, body_style)],
            [Paragraph("<b>DOI:</b>", body_style), Paragraph(p_doi, body_style)],
        ]
        meta_table = Table(meta_rows, colWidths=[110, 430])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
            ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('PADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 14))
        elements.append(Paragraph('Score components: ' + '; '.join(f"{key.replace('_', ' ')} {value}" for key, value in paper_data.get('score_breakdown', {}).items()), body_style))
        elements.append(Paragraph('Score weights: verification 40, metadata 20, coverage 15, citation consistency 15, bibliography hygiene 10. Unverified checks reduce evidence coverage, not a finding of misconduct. Abstract relevance does not change this score.', disclaimer_style))
        if paper_data.get('demo'):
            elements.append(Paragraph('<b>DEMONSTRATION:</b> Curated sample findings. This report is not live verification.', body_style))
        elements.append(Spacer(1, 12))

        # 3. Health Score & Key Statistics
        score = paper_data.get("health_score", 0.0)
        rating = paper_data.get("health_rating", "Pending")
        score_label = 'Not rated' if rating == 'Inconclusive' else f'{score}/100'
        stats = paper_data.get("statistics", {})

        stat_summary_data = [
            [
                Paragraph(f"<font size=16 color='#2563eb'><b>{score_label}</b></font><br/><b>Health Score</b><br/>{safe(rating)}", ParagraphStyle('Score', parent=body_style, leading=19)),
                Paragraph(f"<font size=14 color='#16a34a'><b>{stats.get('verified_count', 0)}</b></font><br/>Verified References", body_style),
                Paragraph(f"<font size=14 color='#d97706'><b>{stats.get('metadata_issues_count', 0)}</b></font><br/>Metadata Issues", body_style),
                Paragraph(f"<font size=14 color='#dc2626'><b>{stats.get('not_found_count', 0)}</b></font><br/>Not Found", body_style),
                Paragraph(f"<font size=14 color='#2563eb'><b>{stats.get('citation_coverage_pct', 100):.0f}%</b></font><br/>Citation Coverage", body_style),
            ]
        ]
        stat_table = Table(stat_summary_data, colWidths=[110, 105, 110, 105, 110])
        stat_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
            ('BOX', (0,0), (-1,-1), 1.0, ACCENT),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('PADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(stat_table)
        elements.append(Spacer(1, 14))

        # 4. AI Executive Summary & Abstract
        ai_summary = paper_data.get("ai_summary")
        if ai_summary:
            elements.append(Paragraph("<b>AI Executive Summary</b>", section_heading))
            elements.append(Paragraph(safe(ai_summary), body_style))
            elements.append(Spacer(1, 10))

        # 5. Detected Issues Section
        issues = paper_data.get("issues", [])
        if issues:
            elements.append(Paragraph("<b>Detected Integrity & Metadata Issues</b>", section_heading))
            issue_rows = [
                [Paragraph("<b>Severity</b>", body_style), Paragraph("<b>Issue</b>", body_style), Paragraph("<b>Description</b>", body_style)]
            ]
            for iss in issues:
                sev = iss.get("severity", "WARNING")
                sev_color = "#dc2626" if sev == "CRITICAL" else ("#d97706" if sev == "WARNING" else "#2563eb")
                issue_rows.append([
                    Paragraph(f"<font color='{sev_color}'><b>{sev}</b></font>", body_style),
                    Paragraph(safe(iss.get("title", "")), body_style),
                    Paragraph(safe(iss.get("description", "")), body_style),
                ])
            issue_table = Table(issue_rows, colWidths=[70, 150, 320], repeatRows=1)
            issue_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
                ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
                ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
                ('PADDING', (0,0), (-1,-1), 4),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ]))
            elements.append(issue_table)
            elements.append(Spacer(1, 14))

        # 6. Detailed Reference Table
        elements.append(Paragraph("<b>Reference Verification Roster</b>", section_heading))
        ref_rows = [
            [
                Paragraph("<b>#</b>", body_style),
                Paragraph("<b>Reference Citation / Matched Work</b>", body_style),
                Paragraph("<b>Status</b>", body_style),
                Paragraph("<b>Match<br/>score</b>", body_style),
                Paragraph("<b>Sources</b>", body_style),
            ]
        ]

        refs = paper_data.get("references", [])
        for r in refs:
            r_num = r.get("reference_number", 1)
            raw = r.get("raw_text", "")
            ver = r.get("verification_result") or {}
            status_text = ver.get("status", "NOT FOUND")
            conf = f"{ver.get('confidence', 0):.0f}%"
            matched_title = ver.get("matched_title") or r.get("title") or raw[:60]
            sources = ", ".join(ver.get("verification_sources", [])) or "None"

            st_color = "#16a34a" if status_text == "VERIFIED" else ("#d97706" if "METADATA" in status_text else ("#dc2626" if status_text in ["NOT FOUND", "INVALID DOI"] else "#2563eb"))

            ref_rows.append([
                Paragraph(f"<b>[{r_num}]</b>", body_style),
                Paragraph(f"<b>{safe(matched_title)}</b><br/><font size=7.5 color='#64748b'>{safe(raw[:800])}</font><br/>{safe((ver.get('explanation') or '')[:800])}<br/>Evidence: {safe(ver.get('matched_url'))}" + ('<br/>Full text is available in the JSON report.' if len(raw) > 800 or len(ver.get('explanation') or '') > 800 else ''), body_style),
                Paragraph(f"<font color='{st_color}'><b>{status_text}</b></font>", body_style),
                Paragraph(conf, body_style),
                Paragraph(safe(sources), body_style),
            ])

        ref_table = Table(ref_rows, colWidths=[28, 275, 110, 57, 70], repeatRows=1)
        ref_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
            ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('PADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(ref_table)
        elements.append(Spacer(1, 16))

        # 7. Academic Disclaimer Footer
        elements.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceBefore=8, spaceAfter=8))
        elements.append(Paragraph(
            "<b>Academic Disclaimer:</b> ResearchGuard provides automated metadata and semantic verification based on available scholarly sources "
            "(OpenAlex, Crossref, Semantic Scholar). A 'Not Found' result does not prove that a publication is fabricated, as works may exist in specialized archives. "
            "Results should be reviewed by a human researcher before making academic, publication, or integrity-related decisions.",
            disclaimer_style
        ))

        # Build Document
        doc.build(elements)
        return output_path

report_generator = ReportGenerator()
