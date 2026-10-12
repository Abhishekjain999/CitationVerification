from app.services.similarity_engine import similarity_engine

def test_title_similarity():
    t1 = "Attention Is All You Need"
    t2 = "Attention is all you need."
    sim = similarity_engine.calculate_title_similarity(t1, t2)
    assert sim >= 0.95

    t3 = "BERT: Pre-training of Deep Bidirectional Transformers"
    sim_diff = similarity_engine.calculate_title_similarity(t1, t3)
    assert sim_diff < 0.40

def test_author_similarity():
    a1 = ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"]
    a2 = ["A. Vaswani", "N. Shazeer", "N. Parmar"]
    sim = similarity_engine.calculate_author_similarity(a1, a2)
    assert sim >= 0.85

def test_venue_acronym_expansion():
    v1 = "NeurIPS"
    v2 = "Advances in Neural Information Processing Systems"
    sim = similarity_engine.calculate_venue_similarity(v1, v2)
    assert sim >= 0.80

def test_year_match():
    is_match, diff, score = similarity_engine.calculate_year_match(2017, 2017)
    assert is_match is True
    assert diff == 0.0
    assert score == 1.0

    is_match_1y, diff_1y, score_1y = similarity_engine.calculate_year_match(2018, 2017)
    assert is_match_1y is False
    assert diff_1y == 1.0
    assert score_1y >= 0.80
