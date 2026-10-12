from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class VerificationResultBase(BaseModel):
    status: str = "NOT FOUND"
    confidence: float = 0.0
    overall_score: float = 0.0
    title_similarity: float = 0.0
    author_similarity: float = 0.0
    year_match: bool = False
    year_difference: float = 0.0
    venue_similarity: float = 0.0
    doi_match: bool = False
    doi_status: str = "NONE"
    
    matched_title: Optional[str] = None
    matched_authors: List[Any] = Field(default_factory=list)
    matched_year: Optional[str] = None
    matched_venue: Optional[str] = None
    matched_publisher: Optional[str] = None
    matched_doi: Optional[str] = None
    matched_url: Optional[str] = None
    matched_abstract: Optional[str] = None
    citation_count: float = 0.0
    
    verification_sources: List[str] = Field(default_factory=list)
    openalex_match: Optional[Dict[str, Any]] = None
    crossref_match: Optional[Dict[str, Any]] = None
    semantic_scholar_match: Optional[Dict[str, Any]] = None
    
    explanation: Optional[str] = None
    metadata_mismatches: List[Dict[str, Any]] = Field(default_factory=list)

class VerificationResultDetail(VerificationResultBase):
    id: str
    reference_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
