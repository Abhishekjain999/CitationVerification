from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from pathlib import Path

def create_sample_paper():
    output_dir = Path(__file__).resolve().parent.parent / "sample_papers"
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / "Attention_Transformer_Sample.pdf"

    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=1,
        spaceAfter=12
    )

    author_style = ParagraphStyle(
        'DocAuthor',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        alignment=1,
        spaceAfter=14
    )

    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        spaceAfter=8
    )

    elements = []

    # Title
    elements.append(Paragraph("Attention Is All You Need", title_style))
    elements.append(Paragraph("Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin<br/>Google Brain, Google Research, University of Toronto", author_style))
    elements.append(Spacer(1, 10))

    # Abstract
    elements.append(Paragraph("<b>Abstract</b>", heading_style))
    elements.append(Paragraph(
        "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over existing results. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs.",
        body_style
    ))
    elements.append(Spacer(1, 10))

    # Section 1: Introduction
    elements.append(Paragraph("1. Introduction", heading_style))
    elements.append(Paragraph(
        "Recurrent neural networks, long short-term memory [4] and gated recurrent neural networks have been firmly established as state of the art approaches in sequence modeling and transduction problems such as language modeling and machine translation. Subsequent work has continued to push the boundaries of recurrent language models and encoder-decoder architectures.",
        body_style
    ))
    elements.append(Paragraph(
        "Attention mechanisms have become an integral part of compelling sequence modeling and transduction models in various tasks, allowing modeling of dependencies without regard to their distance in the input or output sequences [1]. In this work we propose the Transformer, a model architecture eschewing recurrence and instead relying entirely on an attention mechanism to draw global dependencies between input and output.",
        body_style
    ))
    elements.append(Spacer(1, 10))

    # Section 2: Background
    elements.append(Paragraph("2. Background", heading_style))
    elements.append(Paragraph(
        "The goal of reducing sequential computation also forms the foundation of the Extended Neural GPU, ByteNet and ConvS2S, all of which use convolutional neural networks as basic building blocks. In these models, the number of operations required to relate signals from two arbitrary input or output positions grows in the distance between positions. Self-attention, sometimes called intra-attention, is an attention mechanism relating different positions of a single sequence in order to compute a representation of the sequence [2]. Residual connections [3] are utilized across each sub-layer to facilitate stable training across deeper horizons.",
        body_style
    ))
    elements.append(Spacer(1, 10))

    # Section 3: Model Architecture
    elements.append(Paragraph("3. Model Architecture", heading_style))
    elements.append(Paragraph(
        "Most competitive neural sequence transduction models have an encoder-decoder structure. Here, the encoder maps an input sequence of symbol representations to a sequence of continuous representations. Given z, the decoder then generates an output sequence of symbols one element at a time. At each step the model is auto-regressive, consuming the previously generated symbols as additional input when generating the next.",
        body_style
    ))
    elements.append(Paragraph(
        "An attention function can be described as mapping a query and a set of key-value pairs to an output, where the query, keys, values, and output are all vectors. The output is computed as a weighted sum of the values, where the weight assigned to each value is computed by a compatibility function of the query with the corresponding key.",
        body_style
    ))
    elements.append(Spacer(1, 10))

    # Section 4: References
    elements.append(Paragraph("References", heading_style))
    elements.append(Paragraph(
        "[1] Bahdanau, D., Cho, K., and Bengio, Y. Neural machine translation by jointly learning to align and translate. In ICLR 2015, 2015. doi:10.48550/arXiv.1409.0473",
        body_style
    ))
    elements.append(Paragraph(
        "[2] Devlin, J., Chang, M. W., Lee, K., and Toutanova, K. BERT: Pre-training of deep bidirectional transformers for language understanding. In NAACL 2018, 2018. doi:10.18653/v1/N19-1423",
        body_style
    ))
    elements.append(Paragraph(
        "[3] He, K., Zhang, X., Ren, S., and Sun, J. Deep residual learning for image recognition. In CVPR, pp. 770-778, 2016. doi:10.1109/CVPR.2016.90",
        body_style
    ))
    elements.append(Paragraph(
        "[4] Hochreiter, S., and Schmidhuber, J. Long short-term memory. Neural Computation, 9(8):1735-1780, 1997. doi:10.1162/neco.1997.9.8.1735",
        body_style
    ))
    elements.append(Paragraph(
        "[5] Brown, T., Mann, B., Ryder, N., et al. Language Models are Few-Shot Learners. arXiv preprint arXiv:2005.14165, 2020.",
        body_style
    ))

    doc.build(elements)
    print(f"Sample research paper generated at: {pdf_path}")

if __name__ == "__main__":
    create_sample_paper()
