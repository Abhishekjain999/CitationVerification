import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Reference(Base):
    __tablename__ = "references"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    paper_id = Column(String(36), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    reference_number = Column(Integer, nullable=False)  # 1, 2, 3...
    raw_text = Column(Text, nullable=False)

    # Parsed metadata
    title = Column(String(512), nullable=True)
    authors = Column(JSON, default=list)  # list of author strings: ["Vaswani, A.", "Shazeer, N."]
    year = Column(Integer, nullable=True)
    journal = Column(String(255), nullable=True)
    conference = Column(String(255), nullable=True)
    venue = Column(String(255), nullable=True)
    publisher = Column(String(255), nullable=True)
    volume = Column(String(50), nullable=True)
    issue = Column(String(50), nullable=True)
    pages = Column(String(50), nullable=True)
    doi = Column(String(255), nullable=True)
    url = Column(String(512), nullable=True)
    citation_format = Column(String(50), default="numbered")  # 'IEEE', 'APA', 'MLA', 'ACM', 'Chicago', 'numbered', 'author-year'

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    paper = relationship("Paper", back_populates="references")
    verification_result = relationship("VerificationResult", back_populates="reference", uselist=False, cascade="all, delete-orphan")
    citation_occurrences = relationship("CitationOccurrence", back_populates="reference")
    issues = relationship("PaperIssue", back_populates="reference")
