from datetime import datetime, timezone
from typing import Dict, Any

def get_demo_paper_payload() -> Dict[str, Any]:
    paper_id = "demo-paper-attention-transformer"

    paper_data = {
        "id": paper_id,
        "filename": "Attention_Is_All_You_Need_ResearchGuard_Demo.pdf",
        "file_path": "uploads/demo_attention_paper.pdf",
        "file_size_bytes": 2211840,
        "page_count": 15,
        "title": "Attention Is All You Need: Architectural Advances in Transformer Models",
        "authors": [
            "Ashish Vaswani",
            "Noam Shazeer",
            "Niki Parmar",
            "Jakob Uszkoreit",
            "Llion Jones",
            "Aidan N. Gomez",
            "Łukasz Kaiser",
            "Illia Polosukhin"
        ],
        "corresponding_author": "avaswani@google.com",
        "publication_date": "2017-12-06",
        "publication_year": 2017,
        "journal": "Advances in Neural Information Processing Systems",
        "conference": "NeurIPS 2017",
        "venue": "NeurIPS (Advances in Neural Information Processing Systems)",
        "publisher": "Curran Associates, Inc.",
        "doi": "10.48550/arXiv.1706.03762",
        "url": "https://arxiv.org/abs/1706.03762",
        "isbn_issn": "9781510860964",
        "volume": "30",
        "issue": None,
        "pages": "5998–6008",
        "article_type": "Conference Paper",
        "open_access": True,
        "citation_count": 134200,
        "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles, by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature.",
        "ai_summary": "The paper introduces the Transformer architecture, completely replacing recurrent and convolutional neural networks with self-attention mechanisms. The model demonstrates superior translation performance on WMT 2014 benchmarks while offering massive parallelization and significant reductions in training computation.",
        "keywords": [
            "Transformer Architecture",
            "Self-Attention",
            "Sequence Transduction",
            "Natural Language Processing",
            "Neural Machine Translation",
            "Multi-Head Attention",
            "Deep Learning"
        ],
        "sections": [
            {"title": "Abstract", "start_page": 1, "raw_heading": "Abstract"},
            {"title": "Introduction", "start_page": 1, "raw_heading": "1 Introduction"},
            {"title": "Background", "start_page": 2, "raw_heading": "2 Background"},
            {"title": "Model Architecture", "start_page": 3, "raw_heading": "3 Model Architecture"},
            {"title": "Why Self-Attention", "start_page": 5, "raw_heading": "4 Why Self-Attention"},
            {"title": "Training", "start_page": 7, "raw_heading": "5 Training"},
            {"title": "Results", "start_page": 8, "raw_heading": "6 Results"},
            {"title": "Conclusion", "start_page": 10, "raw_heading": "7 Conclusion"},
            {"title": "References", "start_page": 11, "raw_heading": "References"}
        ],
        "paper_stats": {
            "page_count": 15,
            "word_count": 5240,
            "character_count": 34120,
            "reading_time_minutes": 26.2,
            "figures_count": 5,
            "tables_count": 4
        },
        "health_score": 88.5,
        "health_rating": "Excellent",
        "score_breakdown": {
            "verification_score": 36.8,
            "metadata_score": 17.5,
            "coverage_score": 13.8,
            "consistency_score": 13.2,
            "hygiene_score": 7.2
        },
        "processing_status": "completed",
        "progress_stage": "Analysis Completed Successfully",
        "error_message": None,
        "created_at": datetime.now(timezone.utc).replace(tzinfo=None),
        "updated_at": datetime.now(timezone.utc).replace(tzinfo=None)
    }

    # Structured references with rich cases: Verified, Metadata Mismatches, Invalid DOI, Unindexed, Duplicate
    references = [
        {
            "id": f"ref-1-{paper_id}",
            "reference_number": 1,
            "raw_text": "[1] Bahdanau, D., Cho, K., and Bengio, Y. Neural machine translation by jointly learning to align and translate. In ICLR 2015, 2015.",
            "title": "Neural machine translation by jointly learning to align and translate",
            "authors": ["Dzmitry Bahdanau", "Kyunghyun Cho", "Yoshua Bengio"],
            "year": 2015,
            "venue": "ICLR 2015",
            "journal": None,
            "conference": "International Conference on Learning Representations",
            "publisher": None,
            "doi": "10.48550/arXiv.1409.0473",
            "url": "https://arxiv.org/abs/1409.0473",
            "citation_format": "IEEE",
            "verification": {
                "status": "VERIFIED",
                "confidence": 98.5,
                "overall_score": 97.8,
                "title_similarity": 0.99,
                "author_similarity": 1.0,
                "year_match": True,
                "year_difference": 0.0,
                "venue_similarity": 0.95,
                "doi_match": True,
                "doi_status": "MATCH",
                "matched_title": "Neural Machine Translation by Jointly Learning to Align and Translate",
                "matched_authors": ["Dzmitry Bahdanau", "Kyunghyun Cho", "Yoshua Bengio"],
                "matched_year": "2015",
                "matched_venue": "International Conference on Learning Representations (ICLR)",
                "matched_publisher": "ICLR",
                "matched_doi": "10.48550/arXiv.1409.0473",
                "matched_url": "https://arxiv.org/abs/1409.0473",
                "matched_abstract": "Neural machine translation is a recently proposed approach to machine translation. Unlike traditional statistical phrase-based translation system which consists of many small sub-components that are tuned separately, neural machine translation attempts to build and train a single, large neural network that reads a sentence and outputs a correct translation.",
                "citation_count": 32400,
                "verification_sources": ["OpenAlex", "Crossref", "Semantic Scholar"],
                "explanation": "Strong evidence confirms this reference matches 'Neural Machine Translation by Jointly Learning to Align and Translate' across all 3 scholarly sources.",
                "metadata_mismatches": []
            }
        },
        {
            "id": f"ref-2-{paper_id}",
            "reference_number": 2,
            "raw_text": "[2] Devlin, J., Chang, M. W., Lee, K., and Toutanova, K. BERT: Pre-training of deep bidirectional transformers for language understanding. In NAACL 2018, 2018. doi:10.18653/v1/N19-1423",
            "title": "BERT: Pre-training of deep bidirectional transformers for language understanding",
            "authors": ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
            "year": 2018,  # Deliberate metadata issue: published in 2019
            "venue": "NAACL 2018",
            "journal": None,
            "conference": "NAACL",
            "publisher": "ACL",
            "doi": "10.18653/v1/N19-1423",
            "url": "https://doi.org/10.18653/v1/N19-1423",
            "citation_format": "IEEE",
            "verification": {
                "status": "VERIFIED WITH METADATA ISSUES",
                "confidence": 92.4,
                "overall_score": 91.0,
                "title_similarity": 0.99,
                "author_similarity": 1.0,
                "year_match": False,
                "year_difference": 1.0,
                "venue_similarity": 0.92,
                "doi_match": True,
                "doi_status": "MATCH",
                "matched_title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
                "matched_authors": ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
                "matched_year": "2019",
                "matched_venue": "Proceedings of NAACL-HLT 2019",
                "matched_publisher": "Association for Computational Linguistics",
                "matched_doi": "10.18653/v1/n19-1423",
                "matched_url": "https://doi.org/10.18653/v1/n19-1423",
                "matched_abstract": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers.",
                "citation_count": 98500,
                "verification_sources": ["OpenAlex", "Crossref", "Semantic Scholar"],
                "explanation": "The referenced scholarly work was identified, but publication year differs: Reference indicates 2018, but official NAACL proceedings were published in 2019.",
                "metadata_mismatches": [
                    {
                        "field": "Year",
                        "reference_value": "2018",
                        "db_value": "2019",
                        "explanation": "Publication year differs: Reference indicates 2018, but scholarly records show 2019."
                    }
                ]
            }
        },
        {
            "id": f"ref-3-{paper_id}",
            "reference_number": 3,
            "raw_text": "[3] He, K., Zhang, X., Ren, S., and Sun, J. Deep residual learning for image recognition. In CVPR, pp. 770-778, 2016. doi:10.1109/CVPR.2016.90",
            "title": "Deep residual learning for image recognition",
            "authors": ["Kaiming He", "Xiangyu Zhang", "Shaoqing Ren", "Jian Sun"],
            "year": 2016,
            "venue": "CVPR",
            "journal": None,
            "conference": "IEEE Conference on Computer Vision and Pattern Recognition",
            "publisher": "IEEE",
            "doi": "10.1109/CVPR.2016.90",
            "url": "https://doi.org/10.1109/CVPR.2016.90",
            "citation_format": "IEEE",
            "verification": {
                "status": "VERIFIED",
                "confidence": 99.0,
                "overall_score": 99.2,
                "title_similarity": 1.0,
                "author_similarity": 1.0,
                "year_match": True,
                "year_difference": 0.0,
                "venue_similarity": 0.98,
                "doi_match": True,
                "doi_status": "MATCH",
                "matched_title": "Deep Residual Learning for Image Recognition",
                "matched_authors": ["Kaiming He", "Xiangyu Zhang", "Shaoqing Ren", "Jian Sun"],
                "matched_year": "2016",
                "matched_venue": "2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR)",
                "matched_publisher": "IEEE",
                "matched_doi": "10.1109/cvpr.2016.90",
                "matched_url": "https://doi.org/10.1109/cvpr.2016.90",
                "matched_abstract": "Deeper neural networks are more difficult to train. We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously. We explicitly reformulate the layers as learning residual functions with reference to the layer inputs, instead of learning unreferenced functions.",
                "citation_count": 182000,
                "verification_sources": ["OpenAlex", "Crossref", "Semantic Scholar"],
                "explanation": "Strong evidence confirms this reference matches 'Deep Residual Learning for Image Recognition' across OpenAlex, Crossref, and Semantic Scholar.",
                "metadata_mismatches": []
            }
        },
        {
            "id": f"ref-4-{paper_id}",
            "reference_number": 4,
            "raw_text": "[4] Sutskever, I., Vinyals, O., and Le, Q. V. Sequence to sequence learning with neural networks. In NIPS, 2014. doi:10.1038/nature14539",
            "title": "Sequence to sequence learning with neural networks",
            "authors": ["Ilya Sutskever", "Oriol Vinyals", "Quoc V. Le"],
            "year": 2014,
            "venue": "NIPS",
            "journal": None,
            "conference": "Advances in Neural Information Processing Systems",
            "publisher": "Curran Associates",
            "doi": "10.1038/nature14539",  # Deliberate critical DOI mismatch: nature DOI pointing to DeepMind Nature paper
            "url": "https://doi.org/10.1038/nature14539",
            "citation_format": "IEEE",
            "verification": {
                "status": "INVALID DOI",
                "confidence": 35.0,
                "overall_score": 38.0,
                "title_similarity": 0.22,
                "author_similarity": 0.40,
                "year_match": False,
                "year_difference": 1.0,
                "venue_similarity": 0.20,
                "doi_match": False,
                "doi_status": "MISMATCH",
                "matched_title": "Human-level control through deep reinforcement learning",
                "matched_authors": ["Volodymyr Mnih", "Koray Kavukcuoglu", "David Silver"],
                "matched_year": "2015",
                "matched_venue": "Nature",
                "matched_publisher": "Nature Publishing Group",
                "matched_doi": "10.1038/nature14539",
                "matched_url": "https://doi.org/10.1038/nature14539",
                "matched_abstract": "An artificial agent is developed that learns policies end-to-end directly from high-dimensional sensory inputs using reinforcement learning with deep neural networks.",
                "citation_count": 24000,
                "verification_sources": ["Crossref", "OpenAlex"],
                "explanation": "CRITICAL DOI MISMATCH: The DOI specified in Reference #4 (10.1038/nature14539) resolves to 'Human-level control through deep reinforcement learning' (Nature 2015) which is a completely different work.",
                "metadata_mismatches": [
                    {
                        "field": "DOI",
                        "reference_value": "10.1038/nature14539",
                        "db_value": "10.1038/nature14539 (Resolves to different article)",
                        "explanation": "The specified DOI resolves to 'Human-level control through deep reinforcement learning' rather than 'Sequence to sequence learning with neural networks'."
                    }
                ]
            }
        },
        {
            "id": f"ref-5-{paper_id}",
            "reference_number": 5,
            "raw_text": "[5] Brown, T., Mann, B., Ryder, N., et al. Language Models are Few-Shot Learners. arXiv preprint arXiv:2005.14165, 2020.",
            "title": "Language Models are Few-Shot Learners",
            "authors": ["Tom B. Brown", "Benjamin Mann", "Nick Ryder", "Melanie Subbiah", "Jared Kaplan"],
            "year": 2020,
            "venue": "NeurIPS 2020",
            "journal": None,
            "conference": "Advances in Neural Information Processing Systems",
            "publisher": None,
            "doi": "10.48550/arXiv.2005.14165",
            "url": "https://arxiv.org/abs/2005.14165",
            "citation_format": "IEEE",
            "verification": {
                "status": "VERIFIED",
                "confidence": 98.0,
                "overall_score": 97.4,
                "title_similarity": 1.0,
                "author_similarity": 0.95,
                "year_match": True,
                "year_difference": 0.0,
                "venue_similarity": 0.90,
                "doi_match": True,
                "doi_status": "MATCH",
                "matched_title": "Language Models are Few-Shot Learners",
                "matched_authors": ["Tom B. Brown", "Benjamin Mann", "Nick Ryder", "Melanie Subbiah"],
                "matched_year": "2020",
                "matched_venue": "Advances in Neural Information Processing Systems (NeurIPS 2020)",
                "matched_publisher": "NeurIPS",
                "matched_doi": "10.48550/arXiv.2005.14165",
                "matched_url": "https://arxiv.org/abs/2005.14165",
                "matched_abstract": "Recent work has demonstrated substantial gains on many NLP tasks and benchmarks by pre-training on a large corpus of text followed by fine-tuning on a specific task. We demonstrate that scaling up language models greatly improves task-agnostic, few-shot performance.",
                "citation_count": 34500,
                "verification_sources": ["OpenAlex", "Crossref", "Semantic Scholar"],
                "explanation": "Strong evidence confirms this reference matches 'Language Models are Few-Shot Learners' across OpenAlex, Crossref, and Semantic Scholar.",
                "metadata_mismatches": []
            }
        },
        {
            "id": f"ref-6-{paper_id}",
            "reference_number": 6,
            "raw_text": "[6] Brown, T. B., Mann, B., and Ryder, N. Language Models Are Few-Shot Learners (GPT-3). NeurIPS, 2020.",
            "title": "Language Models Are Few-Shot Learners (GPT-3)",
            "authors": ["Tom B. Brown", "Benjamin Mann", "Nick Ryder"],
            "year": 2020,
            "venue": "NeurIPS",
            "journal": None,
            "conference": "NeurIPS",
            "publisher": None,
            "doi": None,
            "url": None,
            "citation_format": "IEEE",
            "verification": {
                "status": "VERIFIED",
                "confidence": 94.0,
                "overall_score": 93.5,
                "title_similarity": 0.94,
                "author_similarity": 0.95,
                "year_match": True,
                "year_difference": 0.0,
                "venue_similarity": 0.92,
                "doi_match": False,
                "doi_status": "NONE",
                "matched_title": "Language Models are Few-Shot Learners",
                "matched_authors": ["Tom B. Brown", "Benjamin Mann", "Nick Ryder"],
                "matched_year": "2020",
                "matched_venue": "NeurIPS 2020",
                "matched_publisher": None,
                "matched_doi": "10.48550/arXiv.2005.14165",
                "matched_url": "https://arxiv.org/abs/2005.14165",
                "matched_abstract": "We demonstrate that scaling up language models greatly improves task-agnostic, few-shot performance, sometimes even reaching competitiveness with prior state-of-the-art fine-tuning approaches.",
                "citation_count": 34500,
                "verification_sources": ["OpenAlex", "Semantic Scholar"],
                "explanation": "Matched 'Language Models are Few-Shot Learners'. (Note: This is a duplicate bibliography entry for Reference #5).",
                "metadata_mismatches": []
            }
        },
        {
            "id": f"ref-7-{paper_id}",
            "reference_number": 7,
            "raw_text": "[7] Reynolds, J., and Harrison, M. Quantum Entanglement Optimizations in Neural Transduction Layers. Journal of Advanced Synthetic Computation, 2023.",
            "title": "Quantum Entanglement Optimizations in Neural Transduction Layers",
            "authors": ["J. Reynolds", "M. Harrison"],
            "year": 2023,
            "venue": "Journal of Advanced Synthetic Computation",
            "journal": "Journal of Advanced Synthetic Computation",
            "conference": None,
            "publisher": None,
            "doi": None,
            "url": None,
            "citation_format": "IEEE",
            "verification": {
                "status": "NOT FOUND",
                "confidence": 12.0,
                "overall_score": 14.5,
                "title_similarity": 0.15,
                "author_similarity": 0.10,
                "year_match": False,
                "year_difference": 0.0,
                "venue_similarity": 0.10,
                "doi_match": False,
                "doi_status": "NONE",
                "matched_title": None,
                "matched_authors": [],
                "matched_year": None,
                "matched_venue": None,
                "matched_publisher": None,
                "matched_doi": None,
                "matched_url": None,
                "matched_abstract": None,
                "citation_count": 0,
                "verification_sources": [],
                "explanation": "No matching record was found in the searched scholarly databases (OpenAlex, Crossref, Semantic Scholar). The paper may exist in specialized or unindexed archives.",
                "metadata_mismatches": []
            }
        },
        {
            "id": f"ref-8-{paper_id}",
            "reference_number": 8,
            "raw_text": "[8] Hochreiter, S., and Schmidhuber, J. Long short-term memory. Neural Computation, 9(8):1735–1780, 1997. doi:10.1162/neco.1997.9.8.1735",
            "title": "Long short-term memory",
            "authors": ["Sepp Hochreiter", "Jürgen Schmidhuber"],
            "year": 1997,
            "venue": "Neural Computation",
            "journal": "Neural Computation",
            "conference": None,
            "publisher": "MIT Press",
            "doi": "10.1162/neco.1997.9.8.1735",
            "url": "https://doi.org/10.1162/neco.1997.9.8.1735",
            "citation_format": "IEEE",
            "verification": {
                "status": "VERIFIED",
                "confidence": 99.5,
                "overall_score": 99.8,
                "title_similarity": 1.0,
                "author_similarity": 1.0,
                "year_match": True,
                "year_difference": 0.0,
                "venue_similarity": 1.0,
                "doi_match": True,
                "doi_status": "MATCH",
                "matched_title": "Long Short-Term Memory",
                "matched_authors": ["Sepp Hochreiter", "Jürgen Schmidhuber"],
                "matched_year": "1997",
                "matched_venue": "Neural Computation",
                "matched_publisher": "MIT Press",
                "matched_doi": "10.1162/neco.1997.9.8.1735",
                "matched_url": "https://doi.org/10.1162/neco.1997.9.8.1735",
                "matched_abstract": "Learning to store information over extended time intervals by recurrent backpropagation takes a very long time, mostly because of insufficient, decaying error backflow. We propose LSTM, a novel recurrent network architecture addressing the vanishing gradient problem.",
                "citation_count": 89000,
                "verification_sources": ["OpenAlex", "Crossref", "Semantic Scholar"],
                "explanation": "Strong evidence confirms this reference matches 'Long Short-Term Memory' across OpenAlex, Crossref, and Semantic Scholar.",
                "metadata_mismatches": []
            }
        }
    ]

    # In-text citation occurrences
    citation_occurrences = [
        {
            "id": f"cit-1-{paper_id}",
            "reference_id": f"ref-1-{paper_id}",
            "reference_number": 1,
            "citation_marker": "[1]",
            "page_number": 1,
            "sentence": "Attention mechanisms have become an integral part of compelling sequence modeling and transduction models in various tasks [1].",
            "section": "1. Introduction",
            "claim_text": "Attention mechanisms have become an integral part of compelling sequence modeling and transduction models in various tasks.",
            "semantic_relevance_score": 94.2,
            "semantic_status": "SUPPORTED",
            "explanation": "The referenced work directly discusses neural attention alignment mechanisms for sequence translation tasks."
        },
        {
            "id": f"cit-2-{paper_id}",
            "reference_id": f"ref-2-{paper_id}",
            "reference_number": 2,
            "citation_marker": "[2]",
            "page_number": 2,
            "sentence": "Pre-trained deep bidirectional representations [2] have demonstrated unprecedented transfer performance across syntactic and semantic evaluation suites.",
            "section": "2. Background",
            "claim_text": "Pre-trained deep bidirectional representations have demonstrated unprecedented transfer performance across syntactic and semantic evaluation suites.",
            "semantic_relevance_score": 91.0,
            "semantic_status": "SUPPORTED",
            "explanation": "The referenced work directly introduces BERT and deep bidirectional pre-training for language representations."
        },
        {
            "id": f"cit-3-{paper_id}",
            "reference_id": f"ref-3-{paper_id}",
            "reference_number": 3,
            "citation_marker": "[3]",
            "page_number": 4,
            "sentence": "We employ residual connections [3] around each of the two sub-layers, followed by layer normalization.",
            "section": "3. Model Architecture",
            "claim_text": "We employ residual connections around each of the two sub-layers, followed by layer normalization.",
            "semantic_relevance_score": 96.5,
            "semantic_status": "SUPPORTED",
            "explanation": "The referenced work explicitly invented deep residual learning and skip connections."
        },
        {
            "id": f"cit-4-{paper_id}",
            "reference_id": f"ref-4-{paper_id}",
            "reference_number": 4,
            "citation_marker": "[4]",
            "page_number": 1,
            "sentence": "Recurrent neural networks, long short-term memory [8] and gated recurrent neural networks have been firmly established as state of the art approaches in sequence modeling [4].",
            "section": "1. Introduction",
            "claim_text": "Recurrent neural networks have been firmly established as state of the art approaches in sequence modeling.",
            "semantic_relevance_score": 88.0,
            "semantic_status": "SUPPORTED",
            "explanation": "The referenced work establishes sequence to sequence learning with multi-layered LSTM networks."
        },
        {
            "id": f"cit-5-{paper_id}",
            "reference_id": f"ref-5-{paper_id}",
            "reference_number": 5,
            "citation_marker": "[5]",
            "page_number": 5,
            "sentence": "Scaling up parameter capacity enables few-shot in-context learning capabilities without fine-tuning [5].",
            "section": "4. Why Self-Attention",
            "claim_text": "Scaling up parameter capacity enables few-shot in-context learning capabilities without fine-tuning.",
            "semantic_relevance_score": 93.0,
            "semantic_status": "SUPPORTED",
            "explanation": "The referenced work directly studies few-shot capabilities in scaled language models."
        },
        {
            "id": f"cit-6-{paper_id}",
            "reference_id": f"ref-8-{paper_id}",
            "reference_number": 8,
            "citation_marker": "[8]",
            "page_number": 1,
            "sentence": "In particular, Long Short-Term Memory networks [8] mitigate the vanishing gradient dilemma for historical token horizons.",
            "section": "1. Introduction",
            "claim_text": "Long Short-Term Memory networks mitigate the vanishing gradient dilemma for historical token horizons.",
            "semantic_relevance_score": 97.0,
            "semantic_status": "SUPPORTED",
            "explanation": "The foundational LSTM paper which introduced memory cells and constant error carousels."
        }
    ]

    # Issues
    issues = [
        {
            "id": f"iss-1-{paper_id}",
            "reference_id": f"ref-4-{paper_id}",
            "reference_number": 4,
            "issue_type": "INVALID_DOI",
            "severity": "CRITICAL",
            "title": "Critical DOI Mismatch in Ref #4",
            "description": "The DOI in Reference #4 (10.1038/nature14539) resolves to 'Human-level control through deep reinforcement learning' (Nature) which is an entirely different publication.",
            "details": {
                "reference_number": 4,
                "doi": "10.1038/nature14539",
                "resolved_title": "Human-level control through deep reinforcement learning"
            }
        },
        {
            "id": f"iss-2-{paper_id}",
            "reference_id": f"ref-2-{paper_id}",
            "reference_number": 2,
            "issue_type": "METADATA_MISMATCH",
            "severity": "WARNING",
            "title": "Metadata Mismatch: Year in Ref #2",
            "description": "Publication year differs: Reference indicates 2018, but official NAACL scholarly records show 2019.",
            "details": {
                "reference_number": 2,
                "field": "Year",
                "ref_value": "2018",
                "db_value": "2019"
            }
        },
        {
            "id": f"iss-3-{paper_id}",
            "reference_id": f"ref-7-{paper_id}",
            "reference_number": 7,
            "issue_type": "NOT_FOUND",
            "severity": "WARNING",
            "title": "Unindexed Reference (Ref #7)",
            "description": "No matching record for Reference #7 ('Quantum Entanglement Optimizations in Neural Transduction Layers') was identified in OpenAlex, Crossref, or Semantic Scholar.",
            "details": {
                "reference_number": 7,
                "raw_text": "[7] Reynolds, J., and Harrison, M. Quantum Entanglement Optimizations..."
            }
        },
        {
            "id": f"iss-4-{paper_id}",
            "reference_id": None,
            "reference_number": None,
            "issue_type": "ORPHAN_CITATION",
            "severity": "WARNING",
            "title": "Orphan In-Text Citation [19]",
            "description": "Citation [19] appears in the text on Page 3 ('Section 3. Model Architecture'), but no corresponding Reference #19 exists in the bibliography roster.",
            "details": {
                "citation_marker": "[19]",
                "page_number": 3,
                "section": "3. Model Architecture"
            }
        },
        {
            "id": f"iss-5-{paper_id}",
            "reference_id": f"ref-6-{paper_id}",
            "reference_number": 6,
            "issue_type": "DUPLICATE_REFERENCE",
            "severity": "INFO",
            "title": "Duplicate Reference Entry (Ref #5 & Ref #6)",
            "description": "Reference #5 and Reference #6 both point to 'Language Models are Few-Shot Learners' by Tom Brown et al. (NeurIPS 2020).",
            "details": {
                "ref1_number": 5,
                "ref2_number": 6,
                "similarity": 0.94
            }
        },
        {
            "id": f"iss-6-{paper_id}",
            "reference_id": f"ref-7-{paper_id}",
            "reference_number": 7,
            "issue_type": "UNUSED_REFERENCE",
            "severity": "INFO",
            "title": "Unused Reference (Ref #7)",
            "description": "Reference #7 is listed in the bibliography but is never cited in the body of the paper.",
            "details": {
                "reference_number": 7,
                "title": "Quantum Entanglement Optimizations in Neural Transduction Layers"
            }
        },
        {
            "id": f"iss-7-{paper_id}",
            "reference_id": None,
            "reference_number": None,
            "issue_type": "POTENTIAL_MISSING_CITATION",
            "severity": "INFO",
            "title": "Potentially Requires Citation",
            "description": "Empirical claim statement without an explicit citation nearby: \"Our model improves over previous best results by over 2 BLEU while training in 3.5 days on 8 GPUs.\"",
            "details": {
                "sentence": "Our model improves over previous best results by over 2 BLEU while training in 3.5 days on 8 GPUs.",
                "confidence": 84.0
            }
        }
    ]

    return {
        "paper": paper_data,
        "references": references,
        "citations": citation_occurrences,
        "issues": issues
    }
