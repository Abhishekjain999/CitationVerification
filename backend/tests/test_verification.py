from app.services.verification_engine import verification_engine

def test_verify_valid_reference():
    parsed_ref = {
        "title": "Attention Is All You Need",
        "authors": ["Ashish Vaswani", "Noam Shazeer"],
        "year": 2017,
        "venue": "NeurIPS",
        "doi": "10.48550/arXiv.1706.03762",
    }
    candidate = {
        "title": "Attention is all you need",
        "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
        "publication_year": 2017,
        "venue": "Advances in Neural Information Processing Systems",
        "doi": "10.48550/arXiv.1706.03762",
        "all_sources": ["OpenAlex", "Crossref"],
        "source_records": {},
    }
    result = verification_engine.verify_reference(parsed_ref, [candidate])
    assert result["status"] == "VERIFIED"
    assert result["confidence"] >= 90.0

def test_verify_metadata_mismatch():
    parsed_ref = {
        "title": "BERT: Pre-training of Deep Bidirectional Transformers",
        "authors": ["Jacob Devlin"],
        "year": 2018,  # mismatch with 2019
        "venue": "NAACL",
        "doi": None,
    }
    candidate = {
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "authors": ["Jacob Devlin", "Ming-Wei Chang"],
        "publication_year": 2019,
        "venue": "NAACL-HLT 2019",
        "doi": "10.18653/v1/N19-1423",
        "all_sources": ["Crossref"],
        "source_records": {},
    }
    result = verification_engine.verify_reference(parsed_ref, [candidate])
    assert result["status"] == "VERIFIED WITH METADATA ISSUES"
    assert len(result["metadata_mismatches"]) >= 1

def test_verify_not_found():
    parsed_ref = {
        "title": "Unobtainium Flux Quantum Core",
        "authors": ["Fictional Author"],
        "year": 2099,
        "venue": "Journal of Fictional Studies",
        "doi": None,
    }
    result = verification_engine.verify_reference(parsed_ref, [])
    assert result["status"] == "NOT FOUND"
    assert result["confidence"] <= 30.0
