import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class CitationOccurrence(Base):
    __tablename__ = "citation_occurrences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    paper_id = Column(String(36), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    reference_id = Column(String(36), ForeignKey("references.id", ondelete="SET NULL"), nullable=True)

    citation_marker = Column(String(50), nullable=False)  # e.g., "[12]", "[1, 3]", "Vaswani et al. (2017)"
    page_number = Column(Integer, default=1)
    sentence = Column(Text, nullable=False)
    section = Column(String(100), default="Main Body")
    claim_text = Column(Text, nullable=True)

    # Semantic citation evaluation
    semantic_relevance_score = Column(Float, default=0.0)  # 0 to 100
    semantic_status = Column(String(50), default="INSUFFICIENT EVIDENCE")
    # Statuses: 'SUPPORTED', 'PARTIALLY SUPPORTED', 'WEAKLY RELATED', 'POSSIBLY UNSUPPORTED', 'INSUFFICIENT EVIDENCE'
    explanation = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    paper = relationship("Paper", back_populates="citation_occurrences")
    reference = relationship("Reference", back_populates="citation_occurrences")
