from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from app.schemas.verification import VerificationResultDetail

class ReferenceBase(BaseModel):
    reference_number: int
    raw_text: str
    title: Optional[str] = None
    authors: List[Any] = Field(default_factory=list)
    year: Optional[int] = None
    journal: Optional[str] = None
    conference: Optional[str] = None
    venue: Optional[str] = None
    publisher: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    citation_format: str = "numbered"

class ReferenceCreate(ReferenceBase):
    paper_id: str

class ReferenceDetail(ReferenceBase):
    id: str
    paper_id: str
    created_at: datetime
    verification_result: Optional[VerificationResultDetail] = None

    model_config = ConfigDict(from_attributes=True)
