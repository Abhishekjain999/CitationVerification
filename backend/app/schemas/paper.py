from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class PaperBase(BaseModel):
    title: Optional[str] = None
    authors: List[Any] = Field(default_factory=list)
    corresponding_author: Optional[str] = None
    publication_date: Optional[str] = None
    publication_year: Optional[int] = None
    journal: Optional[str] = None
    conference: Optional[str] = None
    venue: Optional[str] = None
    publisher: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    isbn_issn: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    article_type: Optional[str] = None
    open_access: bool = False
    citation_count: int = 0
    abstract: Optional[str] = None
    ai_summary: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    sections: List[Dict[str, Any]] = Field(default_factory=list)
    paper_stats: Dict[str, Any] = Field(default_factory=dict)

class PaperCreate(PaperBase):
    filename: str
    file_path: str
    file_size_bytes: int = 0
    page_count: int = 0

class PaperUpdate(BaseModel):
    title: Optional[str] = None
    authors: Optional[List[Any]] = None
    abstract: Optional[str] = None
    ai_summary: Optional[str] = None
    keywords: Optional[List[str]] = None
    processing_status: Optional[str] = None
    progress_stage: Optional[str] = None
    health_score: Optional[float] = None
    health_rating: Optional[str] = None
    score_breakdown: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class PaperSummary(BaseModel):
    id: str
    filename: str
    title: Optional[str] = None
    authors: List[Any] = Field(default_factory=list)
    publication_year: Optional[int] = None
    journal: Optional[str] = None
    conference: Optional[str] = None
    doi: Optional[str] = None
    health_score: float = 0.0
    health_rating: str = "Pending"
    processing_status: str = "pending"
    progress_stage: str = "Initialized"
    total_references: int = 0
    verified_references: int = 0
    issue_count: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaperDetail(PaperBase):
    id: str
    filename: str
    file_size_bytes: int = 0
    page_count: int = 0
    health_score: float = 0.0
    health_rating: str = "Pending"
    score_breakdown: Dict[str, Any] = Field(default_factory=dict)
    processing_status: str = "pending"
    progress_stage: str = "Initialized"
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaperStatistics(BaseModel):
    total_references: int = 0
    verified_count: int = 0
    metadata_issues_count: int = 0
    possible_matches_count: int = 0
    not_found_count: int = 0
    duplicates_count: int = 0
    invalid_doi_count: int = 0
    citation_coverage_pct: float = 0.0
    semantic_relevance_pct: float = 0.0
    orphan_citations_count: int = 0
    unused_references_count: int = 0
    total_issues_count: int = 0
    critical_issues_count: int = 0
    warning_issues_count: int = 0
    info_issues_count: int = 0
    sources_distribution: Dict[str, int] = Field(default_factory=dict)
    confidence_distribution: Dict[str, int] = Field(default_factory=dict)
    health_score: float = 0.0
    health_rating: str = "Pending"
    score_breakdown: Dict[str, Any] = Field(default_factory=dict)


class AnalysisAccepted(BaseModel):
    paper_id: str
    processing_status: str
    status_url: str
