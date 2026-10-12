import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class PaperIssue(Base):
    __tablename__ = "issues"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    paper_id = Column(String(36), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    reference_id = Column(String(36), ForeignKey("references.id", ondelete="CASCADE"), nullable=True)

    # issue_type: 'INVALID_DOI', 'METADATA_MISMATCH', 'POSSIBLE_UNMATCHED', 'NOT_FOUND', 'DUPLICATE_REFERENCE', 'ORPHAN_CITATION', 'UNUSED_REFERENCE', 'POTENTIAL_MISSING_CITATION', 'SEMANTIC_MISMATCH'
    issue_type = Column(String(64), nullable=False)
    # severity: 'CRITICAL', 'WARNING', 'INFO'
    severity = Column(String(20), nullable=False, default="WARNING")
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    details = Column(JSON, default=dict)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    paper = relationship("Paper", back_populates="issues")
    reference = relationship("Reference", back_populates="issues")
