import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, JSON, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class Paper(Base):
    __tablename__ = "papers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    page_count = Column(Integer, default=0)

    # Basic Paper Information
    title = Column(String(512), nullable=True)
    authors = Column(JSON, default=list)  # list of author names or objects
    corresponding_author = Column(String(255), nullable=True)
    publication_date = Column(String(50), nullable=True)
    publication_year = Column(Integer, nullable=True)
    journal = Column(String(255), nullable=True)
    conference = Column(String(255), nullable=True)
    venue = Column(String(255), nullable=True)
    publisher = Column(String(255), nullable=True)
    doi = Column(String(255), nullable=True)
    url = Column(String(512), nullable=True)
    isbn_issn = Column(String(100), nullable=True)
    volume = Column(String(50), nullable=True)
    issue = Column(String(50), nullable=True)
    pages = Column(String(50), nullable=True)
    article_type = Column(String(100), nullable=True)  # e.g., 'Journal Article', 'Conference Paper', 'Preprint'
    open_access = Column(Boolean, default=False)
    citation_count = Column(Integer, default=0)

    # Abstract & NLP fields
    abstract = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    keywords = Column(JSON, default=list)  # list of strings
    sections = Column(JSON, default=list)  # list of section objects [{title, start_page, text_length}]
    paper_stats = Column(JSON, default=dict)  # {word_count, reading_time_min, figures_count, tables_count, etc.}

    # Overall ResearchGuard Scoring
    health_score = Column(Float, default=0.0)  # 0 to 100
    health_rating = Column(String(50), default="Pending")  # 'Excellent', 'Good', 'Needs Review', 'Poor'
    score_breakdown = Column(JSON, default=dict)

    # Status tracking
    processing_status = Column(String(50), default="pending")  # 'pending', 'processing', 'completed', 'failed'
    progress_stage = Column(String(100), default="Initialized")
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    references = relationship("Reference", back_populates="paper", cascade="all, delete-orphan", order_by="Reference.reference_number")
    citation_occurrences = relationship("CitationOccurrence", back_populates="paper", cascade="all, delete-orphan")
    issues = relationship("PaperIssue", back_populates="paper", cascade="all, delete-orphan")
