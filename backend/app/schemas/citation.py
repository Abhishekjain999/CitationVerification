from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class CitationOccurrenceBase(BaseModel):
    citation_marker: str
    page_number: int = 1
    sentence: str
    section: str = "Main Body"
    claim_text: Optional[str] = None
    semantic_relevance_score: float = 0.0
    semantic_status: str = "INSUFFICIENT EVIDENCE"
    explanation: Optional[str] = None

class CitationOccurrenceDetail(CitationOccurrenceBase):
    id: str
    paper_id: str
    reference_id: Optional[str] = None
    reference_title: Optional[str] = None
    reference_authors: Optional[list] = None
    reference_year: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
