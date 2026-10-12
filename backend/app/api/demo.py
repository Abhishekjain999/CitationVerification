from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.paper import Paper
from app.models.reference import Reference
from app.models.verification import VerificationResult
from app.models.citation import CitationOccurrence
from app.models.issue import PaperIssue
from app.demo_data.demo_papers import get_demo_paper_payload
from app.schemas.paper import PaperDetail

router = APIRouter(prefix="/demo", tags=["demo"])

@router.post("/load", response_model=PaperDetail)
async def load_demo_paper(db: AsyncSession = Depends(get_db)):
    payload = get_demo_paper_payload()
    paper_dict = payload["paper"]
    p_id = paper_dict["id"]

    # Delete existing demo records if present
    existing = await db.get(Paper, p_id)
    if existing:
        await db.delete(existing)
    await db.commit()

    # Create Paper
    paper = Paper(
        id=paper_dict["id"],
        filename=paper_dict["filename"],
        file_path=paper_dict["file_path"],
        file_size_bytes=paper_dict["file_size_bytes"],
        page_count=paper_dict["page_count"],
        title=paper_dict["title"],
        authors=paper_dict["authors"],
        corresponding_author=paper_dict["corresponding_author"],
        publication_date=paper_dict["publication_date"],
        publication_year=paper_dict["publication_year"],
        journal=paper_dict["journal"],
        conference=paper_dict["conference"],
        venue=paper_dict["venue"],
        publisher=paper_dict["publisher"],
        doi=paper_dict["doi"],
        url=paper_dict["url"],
        isbn_issn=paper_dict["isbn_issn"],
        volume=paper_dict["volume"],
        issue=paper_dict["issue"],
        pages=paper_dict["pages"],
        article_type=paper_dict["article_type"],
        open_access=paper_dict["open_access"],
        citation_count=paper_dict["citation_count"],
        abstract=paper_dict["abstract"],
        ai_summary=paper_dict["ai_summary"],
        keywords=paper_dict["keywords"],
        sections=paper_dict["sections"],
        paper_stats={**paper_dict["paper_stats"], 'demo': True},
        health_score=paper_dict["health_score"],
        health_rating=paper_dict["health_rating"],
        score_breakdown=paper_dict["score_breakdown"],
        processing_status=paper_dict["processing_status"],
        progress_stage=paper_dict["progress_stage"],
        error_message=paper_dict["error_message"],
    )
    db.add(paper)
    await db.commit()

    # Create References & Verifications
    for r_data in payload["references"]:
        ref = Reference(
            id=r_data["id"],
            paper_id=p_id,
            reference_number=r_data["reference_number"],
            raw_text=r_data["raw_text"],
            title=r_data["title"],
            authors=r_data["authors"],
            year=r_data["year"],
            venue=r_data["venue"],
            journal=r_data["journal"],
            conference=r_data["conference"],
            publisher=r_data["publisher"],
            doi=r_data["doi"],
            url=r_data["url"],
            citation_format=r_data["citation_format"],
        )
        db.add(ref)

        ver_data = r_data["verification"]
        ver = VerificationResult(
            reference_id=ref.id,
            status=ver_data["status"],
            confidence=ver_data["confidence"],
            overall_score=ver_data["overall_score"],
            title_similarity=ver_data["title_similarity"],
            author_similarity=ver_data["author_similarity"],
            year_match=ver_data["year_match"],
            year_difference=ver_data["year_difference"],
            venue_similarity=ver_data["venue_similarity"],
            doi_match=ver_data["doi_match"],
            doi_status=ver_data["doi_status"],
            matched_title=ver_data["matched_title"],
            matched_authors=ver_data["matched_authors"],
            matched_year=ver_data["matched_year"],
            matched_venue=ver_data["matched_venue"],
            matched_publisher=ver_data["matched_publisher"],
            matched_doi=ver_data["matched_doi"],
            matched_url=ver_data["matched_url"],
            matched_abstract=ver_data["matched_abstract"],
            citation_count=ver_data["citation_count"],
            verification_sources=ver_data["verification_sources"],
            explanation=ver_data["explanation"],
            metadata_mismatches=ver_data["metadata_mismatches"],
        )
        db.add(ver)

    # Create Citation Occurrences
    for c_data in payload["citations"]:
        cit = CitationOccurrence(
            id=c_data["id"],
            paper_id=p_id,
            reference_id=c_data["reference_id"],
            citation_marker=c_data["citation_marker"],
            page_number=c_data["page_number"],
            sentence=c_data["sentence"],
            section=c_data["section"],
            claim_text=c_data["claim_text"],
            semantic_relevance_score=c_data["semantic_relevance_score"],
            semantic_status='STRONGLY RELATED' if c_data["semantic_status"] == 'SUPPORTED' else c_data["semantic_status"],
            explanation='Demonstration assessment from curated sample data; not a live verification. Abstract similarity does not establish claim support.',
        )
        db.add(cit)

    # Create Issues
    for i_data in payload["issues"]:
        iss = PaperIssue(
            id=i_data["id"],
            paper_id=p_id,
            reference_id=i_data["reference_id"],
            issue_type=i_data["issue_type"],
            severity=i_data["severity"],
            title=i_data["title"],
            description=i_data["description"],
            details=i_data["details"],
        )
        db.add(iss)

    await db.commit()
    await db.refresh(paper)
    return paper
