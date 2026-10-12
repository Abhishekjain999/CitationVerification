from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class PaperIssueBase(BaseModel):
    issue_type: str
    severity: str = "WARNING"
    title: str
    description: str
    details: Dict[str, Any] = Field(default_factory=dict)

class PaperIssueDetail(PaperIssueBase):
    id: str
    paper_id: str
    reference_id: Optional[str] = None
    reference_number: Optional[int] = None
    reference_title: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
