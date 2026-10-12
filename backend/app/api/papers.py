import uuid
import asyncio
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Query
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, case, update
from sqlalchemy.orm import selectinload

from app.core.database import get_db, AsyncSessionLocal
from app.services.pdf_extractor import pdf_extractor
import logging
from app.core.config import settings
from app.models.paper import Paper
from app.models.reference import Reference
from app.models.verification import VerificationResult
from app.models.citation import CitationOccurrence
from app.models.issue import PaperIssue
from app.schemas.paper import PaperSummary, PaperDetail, PaperStatistics, AnalysisAccepted
from app.schemas.reference import ReferenceDetail
from app.schemas.citation import CitationOccurrenceDetail
from app.schemas.issue import PaperIssueDetail
from app.services.pipeline import analysis_pipeline
from app.services.report_generator import report_generator

router = APIRouter(prefix="/papers", tags=["papers"])

@router.post("/upload", response_model=PaperDetail)
async def upload_paper(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}_{Path(file.filename).name}"
    file_path = settings.UPLOAD_DIR / safe_filename

    file_size = 0
    try:
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                file_size += len(chunk)
                if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                    raise HTTPException(413, f"PDF exceeds {settings.MAX_FILE_SIZE_MB} MB limit.")
                buffer.write(chunk)
        if file_size == 0:
            raise HTTPException(400, "PDF is empty.")
        await asyncio.to_thread(pdf_extractor.extract_paper_content, file_path)
    except HTTPException:
        file_path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        file_path.unlink(missing_ok=True)
        raise HTTPException(422, f"Cannot process PDF: {exc}") from exc
    finally:
        await file.close()

    # Create Paper record
    paper = Paper(
        id=file_id,
        filename=file.filename,
        file_path=str(file_path),
        file_size_bytes=file_size,
        title=Path(file.filename).stem.replace("_", " ").replace("-", " ").title(),
        processing_status="pending",
        progress_stage="Uploaded",
    )
    db.add(paper)
    try:
        await db.commit()
    except Exception:
        file_path.unlink(missing_ok=True)
        raise
    await db.refresh(paper)

    return paper

async def run_analysis_job(paper_id: str):
    async with AsyncSessionLocal() as session:
        try:
            await analysis_pipeline.run_pipeline(paper_id, session)
        except Exception:
            logging.getLogger(__name__).exception("Analysis failed for %s", paper_id)


@router.post("/{paper_id}/analyze", status_code=202, response_model=AnalysisAccepted)
async def analyze_paper(
    paper_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Paper).where(Paper.id == paper_id)
    res = await db.execute(stmt)
    paper = res.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")

    claimed = await db.execute(update(Paper).where(Paper.id == paper_id, Paper.processing_status != "processing").values(processing_status="processing", progress_stage="Queued", error_message=None, health_score=0, health_rating='Pending'))
    if claimed.rowcount:
        await db.commit()
        background_tasks.add_task(run_analysis_job, paper_id)
    return {"paper_id": paper_id, "processing_status": "processing", "status_url": f"/api/papers/{paper_id}"}

@router.get("", response_model=List[PaperSummary])
async def list_papers(db: AsyncSession = Depends(get_db)):
    stmt = select(Paper).order_by(desc(Paper.created_at))
    res = await db.execute(stmt)
    papers = res.scalars().all()

    summaries = []
    for p in papers:
        # Count references and issues
        ref_count_stmt = select(func.count(Reference.id)).where(Reference.paper_id == p.id)
        ref_count = (await db.execute(ref_count_stmt)).scalar() or 0

        verified_stmt = select(func.count(VerificationResult.id)).join(Reference).where(
            Reference.paper_id == p.id,
            VerificationResult.status == "VERIFIED"
        )
        verified_count = (await db.execute(verified_stmt)).scalar() or 0

        issue_stmt = select(func.count(PaperIssue.id)).where(PaperIssue.paper_id == p.id)
        issue_count = (await db.execute(issue_stmt)).scalar() or 0

        summaries.append(PaperSummary(
            id=p.id,
            filename=p.filename,
            title=p.title,
            authors=p.authors or [],
            publication_year=p.publication_year,
            journal=p.journal,
            conference=p.conference,
            doi=p.doi,
            health_score=p.health_score,
            health_rating=p.health_rating,
            processing_status=p.processing_status,
            progress_stage=p.progress_stage,
            total_references=ref_count,
            verified_references=verified_count,
            issue_count=issue_count,
            created_at=p.created_at
        ))

    return summaries

@router.get("/{paper_id}", response_model=PaperDetail)
async def get_paper(paper_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Paper).where(Paper.id == paper_id)
    res = await db.execute(stmt)
    paper = res.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
    return paper

@router.get("/{paper_id}/references", response_model=List[ReferenceDetail])
async def get_paper_references(
    paper_id: str,
    status: Optional[str] = Query(None, description="Filter by status: ALL, VERIFIED, METADATA_ISSUES, POSSIBLE_MATCH, NOT_FOUND, DUPLICATE, INVALID_DOI"),
    search: Optional[str] = Query(None, description="Search query in title or author"),
    sort_by: str = Query("number", description="Sort by: number, confidence, status, title"),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Reference)
        .options(selectinload(Reference.verification_result))
        .where(Reference.paper_id == paper_id)
    )

    res = await db.execute(stmt)
    references = res.scalars().all()

    # Filter by Status
    filtered = []
    for r in references:
        v_status = r.verification_result.status if r.verification_result else "NOT FOUND"
        
        if status and status.upper() != "ALL":
            target_status = status.upper().replace("_", " ")
            if target_status == "METADATA ISSUES" and "METADATA" in v_status:
                pass
            elif target_status != v_status:
                continue

        # Search filter
        if search:
            q = search.lower()
            t_match = r.title and q in r.title.lower()
            a_match = r.authors and any(q in str(a).lower() for a in r.authors)
            r_match = q in r.raw_text.lower()
            if not (t_match or a_match or r_match):
                continue

        filtered.append(r)

    # Sort
    if sort_by == "confidence":
        filtered.sort(key=lambda r: (r.verification_result.confidence if r.verification_result else 0.0), reverse=True)
    elif sort_by == "status":
        filtered.sort(key=lambda r: (r.verification_result.status if r.verification_result else "ZZZ"))
    elif sort_by == "title":
        filtered.sort(key=lambda r: (r.title or "ZZZ").lower())
    else:
        filtered.sort(key=lambda r: r.reference_number)

    return filtered

@router.get("/{paper_id}/references/{reference_id}", response_model=ReferenceDetail)
async def get_reference_detail(
    paper_id: str,
    reference_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Reference)
        .options(selectinload(Reference.verification_result))
        .where(Reference.paper_id == paper_id, Reference.id == reference_id)
    )
    res = await db.execute(stmt)
    ref = res.scalar_one_or_none()
    if not ref:
        raise HTTPException(status_code=404, detail="Reference not found.")
    return ref

@router.get("/{paper_id}/citations", response_model=List[CitationOccurrenceDetail])
async def get_paper_citations(
    paper_id: str,
    db: AsyncSession = Depends(get_db)
):
    await get_paper(paper_id, db)
    stmt = (
        select(CitationOccurrence)
        .options(selectinload(CitationOccurrence.reference))
        .where(CitationOccurrence.paper_id == paper_id)
        .order_by(CitationOccurrence.page_number, CitationOccurrence.citation_marker)
    )
    res = await db.execute(stmt)
    occurrences = res.scalars().all()

    details = []
    for occ in occurrences:
        ref_title = occ.reference.title if occ.reference else None
        ref_authors = occ.reference.authors if occ.reference else None
        ref_year = occ.reference.year if occ.reference else None

        details.append(CitationOccurrenceDetail(
            id=occ.id,
            paper_id=occ.paper_id,
            reference_id=occ.reference_id,
            reference_title=ref_title,
            reference_authors=ref_authors,
            reference_year=ref_year,
            citation_marker=occ.citation_marker,
            page_number=occ.page_number,
            sentence=occ.sentence,
            section=occ.section,
            claim_text=occ.claim_text,
            semantic_relevance_score=occ.semantic_relevance_score,
            semantic_status={'SUPPORTED': 'STRONGLY RELATED', 'PARTIALLY SUPPORTED': 'RELATED', 'POSSIBLY UNSUPPORTED': 'LOW RELEVANCE'}.get(occ.semantic_status, occ.semantic_status),
            explanation=(occ.explanation or '') + (' Legacy abstract relevance assessment; this does not establish claim support.' if occ.semantic_status in {'SUPPORTED', 'PARTIALLY SUPPORTED', 'POSSIBLY UNSUPPORTED'} else ''),
            created_at=occ.created_at,
        ))

    return details

@router.get("/{paper_id}/issues", response_model=List[PaperIssueDetail])
async def get_paper_issues(
    paper_id: str,
    severity: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    await get_paper(paper_id, db)
    stmt = (
        select(PaperIssue)
        .options(selectinload(PaperIssue.reference))
        .where(PaperIssue.paper_id == paper_id)
        .order_by(
            case(
                (PaperIssue.severity == "CRITICAL", 1),
                (PaperIssue.severity == "WARNING", 2),
                else_=3
            )
        )
    )
    if severity:
        stmt = stmt.where(PaperIssue.severity == severity.upper())

    res = await db.execute(stmt)
    issues = res.scalars().all()

    details = []
    for iss in issues:
        ref_num = iss.reference.reference_number if iss.reference else None
        ref_title = iss.reference.title if iss.reference else None

        details.append(PaperIssueDetail(
            id=iss.id,
            paper_id=iss.paper_id,
            reference_id=iss.reference_id,
            reference_number=ref_num,
            reference_title=ref_title,
            issue_type=iss.issue_type,
            severity=iss.severity,
            title=iss.title,
            description=iss.description,
            details=iss.details or {},
            created_at=iss.created_at,
        ))

    return details

@router.get("/{paper_id}/statistics", response_model=PaperStatistics)
async def get_paper_statistics(
    paper_id: str,
    db: AsyncSession = Depends(get_db)
):
    # Fetch paper
    p_stmt = select(Paper).where(Paper.id == paper_id)
    paper = (await db.execute(p_stmt)).scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")

    # References and verification results
    ref_stmt = (
        select(Reference)
        .options(selectinload(Reference.verification_result))
        .where(Reference.paper_id == paper_id)
    )
    references = (await db.execute(ref_stmt)).scalars().all()

    total_refs = len(references)
    verified_count = 0
    meta_issues_count = 0
    possible_matches_count = 0
    not_found_count = 0
    invalid_doi_count = 0
    duplicates_count = 0

    sources_distribution = {"OpenAlex": 0, "Crossref": 0, "Semantic Scholar": 0}
    confidence_buckets = {"90-100%": 0, "70-89%": 0, "50-69%": 0, "0-49%": 0}

    for r in references:
        ver = r.verification_result
        if not ver:
            not_found_count += 1
            confidence_buckets["0-49%"] += 1
            continue

        st = ver.status
        if st == "VERIFIED":
            verified_count += 1
        elif "METADATA" in st:
            meta_issues_count += 1
        elif st == "POSSIBLE MATCH":
            possible_matches_count += 1
        elif st == "INVALID DOI":
            invalid_doi_count += 1
        elif st == "DUPLICATE":
            duplicates_count += 1
        else:
            not_found_count += 1

        # Confidence distribution
        conf = ver.confidence
        if conf >= 90.0:
            confidence_buckets["90-100%"] += 1
        elif conf >= 70.0:
            confidence_buckets["70-89%"] += 1
        elif conf >= 50.0:
            confidence_buckets["50-69%"] += 1
        else:
            confidence_buckets["0-49%"] += 1

        # Sources distribution
        for src in ver.verification_sources or []:
            if src in sources_distribution:
                sources_distribution[src] += 1

    # In-text citation statistics
    cit_stmt = select(CitationOccurrence).where(CitationOccurrence.paper_id == paper_id)
    citations = (await db.execute(cit_stmt)).scalars().all()

    cited_ref_ids = set(c.reference_id for c in citations if c.reference_id)
    citation_coverage_pct = round((len(cited_ref_ids) / max(total_refs, 1)) * 100.0, 1)

    sem_scores = [c.semantic_relevance_score for c in citations if c.semantic_status != "INSUFFICIENT EVIDENCE"]
    avg_sem_relevance = round(sum(sem_scores) / len(sem_scores), 1) if sem_scores else 0.0

    # Issues statistics
    iss_stmt = select(PaperIssue).where(PaperIssue.paper_id == paper_id)
    issues = (await db.execute(iss_stmt)).scalars().all()

    critical_count = len([i for i in issues if i.severity == "CRITICAL"])
    warning_count = len([i for i in issues if i.severity == "WARNING"])
    info_count = len([i for i in issues if i.severity == "INFO"])
    orphan_count = len([i for i in issues if i.issue_type == "ORPHAN_CITATION"])
    unused_count = len([i for i in issues if i.issue_type == "UNUSED_REFERENCE"])
    dup_issues_count = len([i for i in issues if i.issue_type == "DUPLICATE_REFERENCE"])

    return PaperStatistics(
        total_references=total_refs,
        verified_count=verified_count,
        metadata_issues_count=meta_issues_count,
        possible_matches_count=possible_matches_count,
        not_found_count=not_found_count,
        duplicates_count=dup_issues_count,
        invalid_doi_count=invalid_doi_count,
        citation_coverage_pct=citation_coverage_pct,
        semantic_relevance_pct=avg_sem_relevance,
        orphan_citations_count=orphan_count,
        unused_references_count=unused_count,
        total_issues_count=len(issues),
        critical_issues_count=critical_count,
        warning_issues_count=warning_count,
        info_issues_count=info_count,
        sources_distribution=sources_distribution,
        confidence_distribution=confidence_buckets,
        health_score=paper.health_score,
        health_rating=paper.health_rating,
        score_breakdown=paper.score_breakdown or {}
    )

@router.get("/{paper_id}/report")
async def download_report(
    paper_id: str,
    format: str = Query('pdf', pattern='^(pdf|json)$'),
    db: AsyncSession = Depends(get_db)
):
    # Fetch paper with all relations
    p_stmt = (
        select(Paper)
        .options(
            selectinload(Paper.references).selectinload(Reference.verification_result),
            selectinload(Paper.issues),
            selectinload(Paper.citation_occurrences)
        )
        .where(Paper.id == paper_id)
    )
    paper = (await db.execute(p_stmt)).scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
    if paper.processing_status != 'completed':
        raise HTTPException(409, 'Report is available after analysis completes.')
    if format == 'json':
        return JSONResponse(content={
            'paper': PaperDetail.model_validate(paper).model_dump(mode='json'),
            'statistics': (await get_paper_statistics(paper_id, db)).model_dump(mode='json'),
            'references': [ReferenceDetail.model_validate(r).model_dump(mode='json') for r in paper.references],
            'citations': [c.model_dump(mode='json') for c in await get_paper_citations(paper_id, db)],
            'issues': [i.model_dump(mode='json') for i in await get_paper_issues(paper_id, db=db)],
            'limitations': 'Metadata verification and preliminary abstract relevance are not an academic integrity certification. Inconclusive results do not prove misconduct.',
        }, headers={'Content-Disposition': f'attachment; filename="ResearchGuard_Report_{paper.id}.json"'})

    # Build paper dictionary for PDF generator
    stats_data = await get_paper_statistics(paper_id, db)
    
    paper_dict = {
        "title": paper.title,
        "demo": (paper.paper_stats or {}).get('demo', False),
        "authors": paper.authors,
        "publication_year": paper.publication_year,
        "venue": paper.venue or paper.journal or paper.conference,
        "doi": paper.doi,
        "abstract": paper.abstract,
        "ai_summary": paper.ai_summary,
        "health_score": paper.health_score,
        "health_rating": paper.health_rating,
        "score_breakdown": paper.score_breakdown,
        "statistics": stats_data.model_dump(),
        "issues": [
            {
                "severity": i.severity,
                "title": i.title,
                "description": i.description,
            }
            for i in paper.issues
        ],
        "references": [
            {
                "reference_number": r.reference_number,
                "raw_text": r.raw_text,
                "title": r.title,
                "verification_result": ReferenceDetail.model_validate(r).model_dump(mode='json').get('verification_result')
            }
            for r in paper.references
        ]
    }

    report_filename = f"ResearchGuard_Report_{paper.id}.pdf"
    report_path = settings.REPORTS_DIR / report_filename

    report_generator.generate_pdf_report(paper_dict, report_path)

    return FileResponse(
        path=str(report_path),
        filename=f"ResearchGuard_Report_{Path(paper.filename).stem}.pdf",
        media_type="application/pdf"
    )

@router.delete("/{paper_id}")
async def delete_paper(
    paper_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Paper).where(Paper.id == paper_id)
    paper = (await db.execute(stmt)).scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")

    # Remove file on disk if exists
    if paper.processing_status == "processing":
        raise HTTPException(409, "Wait for analysis to finish before deleting this paper.")
    try:
        p = Path(paper.file_path)
        if p.exists():
            p.unlink()
    except Exception:
        pass

    await db.delete(paper)
    await db.commit()

    return {"status": "success", "message": "Paper deleted successfully."}
