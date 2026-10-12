from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.reference import Reference
from app.models.verification import VerificationResult
from app.schemas.reference import ReferenceDetail
from app.services.scholarly.search_service import scholarly_search_service
from app.services.verification_engine import verification_engine
from app.services.refresh_results import refresh_paper_results
from app.models.paper import Paper
from datetime import datetime, timezone

router = APIRouter(prefix="/references", tags=["references"])

@router.post("/{reference_id}/verify", response_model=ReferenceDetail)
async def reverify_reference(
    reference_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Reference)
        .options(selectinload(Reference.verification_result))
        .where(Reference.id == reference_id)
    )
    res = await db.execute(stmt)
    ref = res.scalar_one_or_none()
    if not ref:
        raise HTTPException(status_code=404, detail="Reference not found.")
    paper = await db.get(Paper, ref.paper_id)
    if paper.processing_status == 'processing':
        raise HTTPException(409, 'Analysis is already running.')
    if (paper.paper_stats or {}).get('demo'):
        raise HTTPException(409, 'Demo records are curated examples. Upload a PDF for live verification.')

    p_ref = {
        "title": ref.title,
        "authors": ref.authors or [],
        "year": ref.year,
        "venue": ref.venue or ref.journal or ref.conference,
        "doi": ref.doi,
        "raw_text": ref.raw_text,
    }

    candidates = await scholarly_search_service.search_reference(p_ref)
    ver_data = verification_engine.verify_reference(p_ref, candidates)

    # Update or create VerificationResult
    ver_obj = ref.verification_result
    if not ver_obj:
        ver_obj = VerificationResult(reference_id=ref.id)
        db.add(ver_obj)

    ver_obj.status = ver_data["status"]
    ver_obj.confidence = ver_data["confidence"]
    ver_obj.overall_score = ver_data["overall_score"]
    ver_obj.title_similarity = ver_data["title_similarity"]
    ver_obj.author_similarity = ver_data["author_similarity"]
    ver_obj.year_match = ver_data["year_match"]
    ver_obj.year_difference = ver_data["year_difference"]
    ver_obj.venue_similarity = ver_data["venue_similarity"]
    ver_obj.doi_match = ver_data["doi_match"]
    ver_obj.doi_status = ver_data["doi_status"]
    ver_obj.matched_title = ver_data["matched_title"]
    ver_obj.matched_authors = ver_data["matched_authors"]
    ver_obj.matched_year = ver_data["matched_year"]
    ver_obj.matched_venue = ver_data["matched_venue"]
    ver_obj.matched_publisher = ver_data["matched_publisher"]
    ver_obj.matched_doi = ver_data["matched_doi"]
    ver_obj.matched_url = ver_data["matched_url"]
    ver_obj.matched_abstract = ver_data["matched_abstract"]
    ver_obj.citation_count = ver_data["citation_count"]
    ver_obj.verification_sources = ver_data["verification_sources"]
    ver_obj.openalex_match = ver_data["openalex_match"]
    ver_obj.crossref_match = ver_data["crossref_match"]
    ver_obj.semantic_scholar_match = ver_data["semantic_scholar_match"]
    ver_obj.explanation = ver_data["explanation"]
    ver_obj.metadata_mismatches = ver_data["metadata_mismatches"]
    ver_obj.created_at = datetime.now(timezone.utc).replace(tzinfo=None)

    await db.commit()
    await refresh_paper_results(ref.paper_id, db)
    await db.refresh(ref)
    return ref
