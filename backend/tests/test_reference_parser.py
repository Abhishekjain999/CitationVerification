from app.services.reference_parser import reference_parser

def test_parse_ieee_reference():
    raw = "[1] D. Bahdanau, K. Cho, and Y. Bengio, \"Neural machine translation by jointly learning to align and translate,\" in ICLR 2015, 2015. doi:10.48550/arXiv.1409.0473"
    parsed = reference_parser.parse_reference(raw, ref_number=1)
    
    assert parsed["reference_number"] == 1
    assert "Neural machine translation" in (parsed["title"] or "")
    assert parsed["year"] == 2015
    assert parsed["doi"] == "10.48550/arxiv.1409.0473"
    assert len(parsed["authors"]) >= 2

def test_parse_apa_reference():
    raw = "Vaswani, A., Shazeer, N., & Parmar, N. (2017). Attention is all you need. Advances in Neural Information Processing Systems, 30, 5998-6008."
    parsed = reference_parser.parse_reference(raw, ref_number=2)
    
    assert parsed["year"] == 2017
    assert "Attention is all you need" in (parsed["title"] or "")
    assert len(parsed["authors"]) >= 1

def test_parse_doi_and_url_extraction():
    raw = "3. Devlin, J. et al. (2019). BERT: Pre-training of Deep Bidirectional Transformers. NAACL. https://doi.org/10.18653/v1/N19-1423"
    parsed = reference_parser.parse_reference(raw, ref_number=3)
    
    assert parsed["doi"] == "10.18653/v1/n19-1423"
    assert parsed["year"] == 2019
