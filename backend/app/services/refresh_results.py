"""Refresh persisted derived findings after an individual reference changes."""
from collections import Counter
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.models.paper import Paper
from app.models.reference import Reference
from app.models.citation import CitationOccurrence
from app.models.issue import PaperIssue
from app.schemas.reference import ReferenceDetail
from app.services.issue_detector import issue_detector
from app.services.health_scorer import health_scorer
from app.services.semantic_validator import semantic_validator


async def refresh_paper_results(paper_id, db):
    refs = (await db.execute(select(Reference).where(Reference.paper_id == paper_id).options(selectinload(Reference.verification_result)))).scalars().all()
    occurrences = (await db.execute(select(CitationOccurrence).where(CitationOccurrence.paper_id == paper_id))).scalars().all()
    existing = (await db.execute(select(PaperIssue).where(PaperIssue.paper_id == paper_id))).scalars().all()
    records = []
    for ref in refs:
        data = ReferenceDetail.model_validate(ref).model_dump()
        records.append({'reference': data, 'verification': data['verification_result'] or {}})
    cited = {c.reference_id for c in occurrences}
    orphans = [i.details for i in existing if i.issue_type == 'ORPHAN_CITATION']
    unused = [r['reference'] for r in records if r['reference']['id'] not in cited]
    coverage = 100 * len(cited) / len(refs) if refs else 0
    findings = issue_detector.detect_all_issues(paper_id, records, {'orphan_citations': orphans, 'unused_references': unused}, '')
    preserve = {'POTENTIAL_MISSING_CITATION', 'EXTRACTION_LIMITATION', 'MALFORMED_CITATION_RANGE', 'AMBIGUOUS_CITATION'}
    await db.execute(delete(PaperIssue).where(PaperIssue.paper_id == paper_id, PaperIssue.issue_type.not_in(preserve)))
    by_id = {r['reference']['id']: r['verification'] for r in records}
    for occurrence in occurrences:
        ver = by_id.get(occurrence.reference_id, {})
        accepted = ver.get('status') in {'VERIFIED', 'VERIFIED WITH METADATA ISSUES'}
        assessment = semantic_validator.evaluate_citation_claim(occurrence.sentence, ver.get('matched_title') if accepted else None, ver.get('matched_abstract') if accepted else None)
        occurrence.semantic_status = assessment['status']
        occurrence.semantic_relevance_score = assessment['relevance_score']
        occurrence.explanation = assessment['explanation']
        if assessment['status'] == 'LOW RELEVANCE':
            findings.append({'reference_id': occurrence.reference_id, 'issue_type': 'CONTEXT_MISMATCH', 'severity': 'INFO', 'title': 'Preliminary citation relevance concern', 'description': assessment['explanation'], 'details': {'sentence': occurrence.sentence, 'source_url': ver.get('matched_url'), 'confidence': 0.4, 'recommended_action': 'Read the full cited source to assess support.'}})
    for finding in findings:
        db.add(PaperIssue(paper_id=paper_id, reference_id=finding.get('reference_id'), issue_type=finding['issue_type'], severity=finding['severity'], title=finding['title'], description=finding['description'], details=finding.get('details', {})))
    counts = Counter(r['verification'].get('status', 'NOT FOUND') for r in records)
    score = health_scorer.calculate_health_score(total_references=len(refs), verified_count=counts['VERIFIED'], metadata_issues_count=counts['VERIFIED WITH METADATA ISSUES'], possible_matches_count=counts['POSSIBLE MATCH'], not_found_count=counts['NOT FOUND'], invalid_doi_count=counts['INVALID DOI'], duplicate_count=sum(f['issue_type'] == 'DUPLICATE_REFERENCE' for f in findings), orphan_count=len(orphans), unused_count=len(unused), citation_coverage_pct=coverage, semantic_relevance_pct=0)
    paper = await db.get(Paper, paper_id)
    paper.health_score = score['health_score']
    paper.health_rating = score['health_rating']
    paper.score_breakdown = score['breakdown']
    paper.paper_stats = {**(paper.paper_stats or {}), 'verification_coverage_pct': round(100 * (counts['VERIFIED'] + counts['VERIFIED WITH METADATA ISSUES']) / len(refs), 1) if refs else 0}
    await db.commit()
