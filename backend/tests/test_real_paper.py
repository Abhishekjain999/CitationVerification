"""Regression fixture from the public NAACL 2019 BERT PDF, ACL N19-1423."""
from pathlib import Path
from app.services.pdf_extractor import pdf_extractor
from app.services.reference_detector import reference_detector
from app.services.reference_parser import reference_parser
from app.services.metadata_extractor import metadata_extractor
from app.services.citation_context import citation_context_extractor
from app.services.health_scorer import health_scorer


PAPER = Path(__file__).resolve().parents[2] / 'sample_papers' / 'BERT_N19-1423.pdf'


def test_real_bert_extraction():
    data = pdf_extractor.extract_paper_content(PAPER)
    metadata = metadata_extractor.extract_metadata(data)
    assert metadata['title'] == 'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding'
    assert metadata['authors'] == ['Jacob Devlin', 'Ming-Wei Chang', 'Kenton Lee', 'Kristina Toutanova']
    assert 'SQuAD v2.0' in metadata['abstract']
    raw = reference_detector.extract_raw_references(data['full_text'], data['pages'])
    assert len(raw) == 56
    refs = [reference_parser.parse_reference(r['raw_text'], r['reference_number']) for r in raw]
    assert all(r['year'] for r in refs)
    assert not any('Question:' in r['raw_text'] for r in refs)
    assert {r['year_suffix'] for r in refs if 'contextual' in r['title'].lower()} >= {'a', 'b'}
    result = citation_context_extractor.extract_citations(data['pages'], data['full_text'], refs, [])
    assert not result['orphan_citations']
    assert result['citation_coverage_pct'] >= 90
    assert any(o['page_number'] > 12 for o in result['occurrences'])


def test_provider_outage_cannot_rate_integrity():
    result = health_scorer.calculate_health_score(total_references=56, verified_count=0, metadata_issues_count=0, possible_matches_count=0, not_found_count=56, invalid_doi_count=0, duplicate_count=0, orphan_count=0, unused_count=0, citation_coverage_pct=100, semantic_relevance_pct=0)
    assert result['health_rating'] == 'Inconclusive'


def test_compound_and_ambiguous_citations():
    refs = [{'id': str(i), 'reference_number': i, 'year': 2018, 'authors': [author], 'raw_text': f'{author}. 2018{suffix}. A title.'} for i, author, suffix in [(1, 'Matthew Peters', 'a'), (2, 'Matthew Peters', 'b'), (3, 'Alec Radford', '')]]
    text = 'Earlier work (Peters et al., 2018a; Radford et al., 2018) agrees. Peters (2018) is ambiguous.'
    data = citation_context_extractor.extract_citations([{'text': text, 'page_number': 1}], text, refs, [])
    assert len(data['occurrences']) == 2
    assert len(data['ambiguous_citations']) == 1
    assert not data['orphan_citations']
