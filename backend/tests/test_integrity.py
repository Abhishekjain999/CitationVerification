import pytest
import pymupdf
from app.services.normalization import normalize_doi, normalize_reference_id
from app.services.reference_detector import reference_detector
from app.services.citation_context import citation_context_extractor as citations
from app.services.pdf_extractor import pdf_extractor
from app.services.metadata_extractor import metadata_extractor
from app.services.verification_engine import verification_engine
from app.services.semantic_validator import semantic_validator
from app.services.health_scorer import health_scorer
from app.services.issue_detector import issue_detector


@pytest.mark.parametrize('value', [2, '02', '[2]', '(2)', '2.'])
def test_reference_identifier(value):
    assert normalize_reference_id(value) == 2


@pytest.mark.parametrize('value', ['0', 'abc', None, '-1'])
def test_invalid_identifier(value):
    assert normalize_reference_id(value) is None


def test_doi_normalization():
    assert normalize_doi(' DOI:10.1234/ABC. ') == '10.1234/abc'
    assert normalize_doi('https://doi.org/10.1234/test(foo)') == '10.1234/test(foo)'
    assert normalize_doi('http://dx.doi.org/10.1234/ABC)') == '10.1234/abc'


def analyze(text, refs):
    return citations.extract_citations([{'page_number': 1, 'text': text}], text, refs, [])


def test_previous_orphan_bug_one_through_eight():
    text = 'Prior work [2], [3] and [4] describes these methods.\nReferences\n' + '\n'.join(f'[{i}] Smith, J. (2020). Research method {i}. Journal of Science.' for i in range(1, 9))
    refs = reference_detector.extract_raw_references(text, [])
    assert [r['reference_number'] for r in refs] == list(range(1, 9))
    assert all(r['raw_text'].count(f"[{r['reference_number']}]") == 1 for r in refs)
    result = analyze(text, refs)
    assert result['orphan_citations'] == []
    assert len(result['occurrences']) == 3
    assert len(result['unused_references']) == 5


def test_gaps_and_string_ids():
    text = 'Results [2–4, 8] agree.\nReferences\n[2] Smith. A useful study. 2020.\n[4] Jones. Another useful study. 2021.'
    refs = reference_detector.extract_raw_references(text, [])
    assert [r['reference_number'] for r in refs] == [2, 4]
    refs[0]['reference_number'] = '[02]'
    result = analyze(text, refs)
    assert [o['citation_marker'] for o in result['orphan_citations']] == ['[3]', '[8]']


@pytest.mark.parametrize('text, expected', [('2–5, 7', [2, 3, 4, 5, 7]), ('2-4;4', [2, 3, 4]), ('5-2', []), ('1-999999', []), ('2 5', [])])
def test_ranges(text, expected):
    assert citations._expand_number_range(text) == expected


def test_author_year_and_narrative_orphan():
    refs = [{'id': 'smith', 'reference_number': 1, 'authors': ['Smith, J.'], 'year': 2022, 'raw_text': 'Smith, J. (2022). Methods.'}]
    result = analyze('Smith (2022) describes this. Related work (Smith, 2022) agrees. Jones (2021) disagrees.', refs)
    assert len(result['occurrences']) == 2
    assert result['unused_references'] == []
    assert result['orphan_citations'][0]['citation_marker'] == 'Jones (2021)'


def test_bibliography_not_counted_on_same_page():
    result = analyze('No citations here.\nReferences\n[1] Smith (2022). A study.', [{'reference_number': 1}])
    assert not result['occurrences']
    assert len(result['unused_references']) == 1


def test_bad_range_is_reported():
    result = analyze('Results [5-2] are discussed.', [])
    assert len(result['malformed_ranges']) == 1


def test_no_heading_is_inconclusive():
    assert reference_detector.extract_raw_references('A paper without a bibliography. It cites [2].', []) == []


def test_single_multiline_reference():
    refs = reference_detector.extract_raw_references('References\n[8] Smith, J. (2022). A long\nreference title. Journal of Science.', [])
    assert len(refs) == 1 and refs[0]['reference_number'] == 8


def test_author_year_bibliography():
    refs = reference_detector.extract_raw_references('References\nSmith, J. (2022). Methods for learning. Science.\nJones, R. (2023). Another\nmultiline title. Science.', [])
    assert len(refs) == 2


def make_pdf(path, text=None):
    with pymupdf.open() as doc:
        page = doc.new_page()
        if text:
            page.insert_text((40, 40), text)
        doc.save(path)


def test_pdf_and_metadata(tmp_path):
    path = tmp_path / 'paper.pdf'
    make_pdf(path, 'Research Methods and Evidence\nAlice Smith\nAbstract\nThis study explores evidence extraction.\nIntroduction\nA method.\nReferences\n[1] Jones. Study. doi:10.1234/source')
    data = pdf_extractor.extract_paper_content(path)
    assert data['stats']['page_count'] == 1
    assert data['pages'][0]['page_number'] == 1
    meta = metadata_extractor.extract_metadata(data)
    assert meta['title']
    assert meta['doi'] is None  # A reference DOI is not the uploaded paper's DOI.


def test_scanned_and_malformed_pdf(tmp_path):
    path = tmp_path / 'scan.pdf'
    make_pdf(path)
    with pytest.raises(ValueError, match='OCR'):
        pdf_extractor.extract_paper_content(path)
    path.write_bytes(b'not a PDF')
    with pytest.raises(Exception):
        pdf_extractor.extract_paper_content(path)


def test_failure_is_not_invalid_doi():
    result = verification_engine.verify_reference({'doi': '10.1234/test', '_provider_diagnostics': ['api.crossref.org: HTTP 429']}, [])
    assert result['doi_status'] == 'UNVERIFIED'
    assert '429' in result['explanation']


def test_unrelated_search_result_does_not_prove_doi_resolution():
    result = verification_engine.verify_reference({'title': 'Neural networks', 'doi': '10.1234/a'}, [{'title': 'Marine biology', 'doi': '10.1234/b'}])
    assert result['status'] != 'INVALID DOI'


def test_direct_doi_resolves_to_wrong_title():
    result = verification_engine.verify_reference({'title': 'Neural networks', 'doi': '10.1234/a'}, [{'title': 'Marine biology', 'doi': '10.1234/a', 'doi_lookup': True}])
    assert result['status'] == 'INVALID DOI'


def test_missing_abstract_not_support():
    result = semantic_validator.evaluate_citation_claim('Neural networks greatly improve learning [1].', 'Neural networks greatly improve learning', None)
    assert result['status'] == 'INSUFFICIENT EVIDENCE'


def test_relevance_never_proves_support():
    result = semantic_validator.evaluate_citation_claim('Neural networks improve language learning.', 'Neural networks', 'Neural networks improve language learning using training data.')
    assert result['status'] != 'SUPPORTED'
    assert 'does not prove' in result['explanation']


def test_score_deterministic_and_no_semantic_bonus():
    args = dict(total_references=8, verified_count=8, metadata_issues_count=0, possible_matches_count=0, not_found_count=0, invalid_doi_count=0, duplicate_count=0, orphan_count=0, unused_count=0, citation_coverage_pct=100, semantic_relevance_pct=0)
    score = health_scorer.calculate_health_score(**args)
    assert score['health_score'] == 100
    assert health_scorer.calculate_health_score(**{**args, 'semantic_relevance_pct': 100}) == score
    assert health_scorer.calculate_health_score(**{**args, 'total_references': 0})['health_score'] == 0


def test_duplicate_issue_and_recommendation():
    refs = [{'reference': {'id': str(i), 'title': 'Identical work', 'doi': '10.1234/a', 'reference_number': 1, 'year': 2020, 'authors': ['Smith']}, 'verification': {}} for i in range(2)]
    issues = issue_detector.detect_all_issues('paper', refs, {}, '')
    assert any(i['issue_type'] == 'DUPLICATE_REFERENCE' for i in issues)
    assert any(i['issue_type'] == 'NUMBERING_INCONSISTENCY' for i in issues)
    assert all('recommended_action' in i['details'] for i in issues)
