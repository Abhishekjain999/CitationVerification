import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class VerificationResult(Base):
    __tablename__ = "verification_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    reference_id = Column(String(36), ForeignKey("references.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Status: 'VERIFIED', 'VERIFIED WITH METADATA ISSUES', 'POSSIBLE MATCH', 'NOT FOUND', 'DUPLICATE', 'INVALID DOI'
    status = Column(String(50), nullable=False, default="NOT FOUND")
    confidence = Column(Float, default=0.0)  # 0 to 100
    overall_score = Column(Float, default=0.0)  # 0 to 100

    # Similarity breakdown (0.0 to 1.0)
    title_similarity = Column(Float, default=0.0)
    author_similarity = Column(Float, default=0.0)
    year_match = Column(Boolean, default=False)
    year_difference = Column(Float, default=0.0)  # difference in years
    venue_similarity = Column(Float, default=0.0)
    doi_match = Column(Boolean, default=False)
    doi_status = Column(String(50), default="NONE")  # 'MATCH', 'MISMATCH', 'INVALID', 'NONE'

    # Matched record details
    matched_title = Column(String(512), nullable=True)
    matched_authors = Column(JSON, default=list)
    matched_year = Column(String(50), nullable=True)
    matched_venue = Column(String(255), nullable=True)
    matched_publisher = Column(String(255), nullable=True)
    matched_doi = Column(String(255), nullable=True)
    matched_url = Column(String(512), nullable=True)
    matched_abstract = Column(Text, nullable=True)
    citation_count = Column(Float, default=0.0)

    # Verification Sources details
    verification_sources = Column(JSON, default=list)  # e.g., ["OpenAlex", "Crossref", "Semantic Scholar"]
    openalex_match = Column(JSON, nullable=True)
    crossref_match = Column(JSON, nullable=True)
    semantic_scholar_match = Column(JSON, nullable=True)

    # Human-readable explanation and metadata mismatch details
    explanation = Column(Text, nullable=True)
    metadata_mismatches = Column(JSON, default=list)  # list of {field: str, reference_value: str, db_value: str, explanation: str}

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    reference = relationship("Reference", back_populates="verification_result")
