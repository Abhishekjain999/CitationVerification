import asyncio
from pathlib import Path
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.paper import Paper
from app.models.reference import Reference
from app.models.verification import VerificationResult
from app.models.citation import CitationOccurrence
from app.models.issue import PaperIssue

from app.services.pdf_extractor import pdf_extractor
from app.services.metadata_extractor import metadata_extractor
from app.services.reference_detector import reference_detector
from app.services.reference_parser import reference_parser
from app.services.scholarly.search_service import scholarly_search_service
from app.services.verification_engine import verification_engine
from app.services.citation_context import citation_context_extractor
from app.services.semantic_validator import semantic_validator
from app.services.issue_detector import issue_detector
from app.services.health_scorer import health_scorer
from app.core.config import settings

class AnalysisPipeline:
    """Coordinates the end-to-end PDF analysis, scholarly verification, and integrity evaluation pipeline."""

    async def run_pipeline(self, paper_id: str, db: AsyncSession) -> Paper:
        # Fetch paper from DB
        stmt = select(Paper).where(Paper.id == paper_id)
        result = await db.execute(stmt)
        paper = result.scalar_one_or_none()

        if not paper:
            raise ValueError(f"Paper with ID {paper_id} not found.")

        try:
            # Stage 1: Text extraction
            paper.processing_status = "processing"
            paper.progress_stage = "Extracting paper text and structure"
            await db.commit()

            file_path = Path(paper.file_path)
            extracted_pdf = await asyncio.to_thread(pdf_extractor.extract_paper_content, file_path)
            paper.page_count = extracted_pdf.get("stats", {}).get("page_count", 1)
            paper.paper_stats = extracted_pdf.get("stats", {})

            # Stage 2: Metadata extraction
            paper.progress_stage = "Detecting paper metadata & sections"
            await db.commit()

            meta = metadata_extractor.extract_metadata(extracted_pdf)
            paper.title = meta.get("title") or paper.title
            paper.authors = meta.get("authors") or []
            paper.corresponding_author = meta.get("corresponding_author")
            paper.publication_year = meta.get("publication_year")
            paper.publication_date = meta.get("publication_date")
            paper.journal = meta.get("journal")
            paper.venue = meta.get("venue")
            paper.conference = meta.get("conference")
            paper.publisher = meta.get("publisher")
            paper.doi = meta.get("doi")
            paper.url = meta.get("url")
            paper.volume = meta.get("volume")
            paper.issue = meta.get("issue")
            paper.pages = meta.get("pages")
            paper.article_type = meta.get("article_type")
            paper.open_access = meta.get("open_access", False)
            paper.abstract = meta.get("abstract")
            paper.ai_summary = meta.get("ai_summary")
            paper.keywords = meta.get("keywords", [])
            paper.sections = meta.get("sections", [])
            await db.commit()

            # Stage 3: Detect and segment references
            paper.progress_stage = "Detecting bibliography references"
            await db.commit()

            raw_refs = reference_detector.extract_raw_references(
                extracted_pdf.get("full_text", ""),
                extracted_pdf.get("pages", [])
            )

            # Stage 4: Parse references
            paper.progress_stage = "Parsing citations into structured metadata"
            await db.commit()

            parsed_refs_list = []
            for r in raw_refs:
                parsed = reference_parser.parse_reference(r["raw_text"], r["reference_number"])
                parsed_refs_list.append(parsed)

            # Clear existing references if re-running
            ref_ids = select(Reference.id).where(Reference.paper_id == paper_id)
            await db.execute(delete(CitationOccurrence).where(CitationOccurrence.paper_id == paper_id))
            await db.execute(delete(PaperIssue).where(PaperIssue.paper_id == paper_id))
            await db.execute(delete(VerificationResult).where(VerificationResult.reference_id.in_(ref_ids)))
            await db.execute(delete(Reference).where(Reference.paper_id == paper_id))
            await db.commit()

            # Persist Reference models
            ref_models = []
            for p_ref in parsed_refs_list:
                ref_obj = Reference(
                    paper_id=paper_id,
                    reference_number=p_ref["reference_number"],
                    raw_text=p_ref["raw_text"],
                    title=p_ref["title"],
                    authors=p_ref["authors"],
                    year=p_ref["year"],
                    journal=p_ref["journal"],
                    conference=p_ref["conference"],
                    venue=p_ref["venue"],
                    publisher=p_ref["publisher"],
                    volume=p_ref["volume"],
                    issue=p_ref["issue"],
                    pages=p_ref["pages"],
                    doi=p_ref["doi"],
                    url=p_ref["url"],
                    citation_format=p_ref["citation_format"],
                )
                db.add(ref_obj)
                ref_models.append((ref_obj, p_ref))
            await db.commit()

            # Stage 5 & 6: Search scholarly databases and verify references with controlled concurrency
            paper.progress_stage = "Searching scholarly databases (OpenAlex, Crossref, Semantic Scholar)"
            await db.commit()

            semaphore = asyncio.Semaphore(settings.CONCURRENCY_LIMIT)

            async def verify_single_ref(ref_model: Reference, p_ref: Dict[str, Any]):
                async with semaphore:
                    try:
                        candidates = await scholarly_search_service.search_reference(p_ref)
                        ver_data = verification_engine.verify_reference(p_ref, candidates)
                        return ref_model, ver_data
                    except Exception:
                        # Fallback state if query failed completely
                        fallback_ver = verification_engine.verify_reference(p_ref, [])
                        return ref_model, fallback_ver

            verification_tasks = [
                verify_single_ref(rm, pr) for rm, pr in ref_models
            ]
            verified_results = await asyncio.gather(*verification_tasks)

            # Persist VerificationResult models
            refs_with_verifs_for_issues = []
            counts = {
                "verified": 0,
                "metadata_issues": 0,
                "possible_matches": 0,
                "not_found": 0,
                "invalid_doi": 0,
            }

            for ref_model, ver_data in verified_results:
                ver_obj = VerificationResult(
                    reference_id=ref_model.id,
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
                    openalex_match=ver_data["openalex_match"],
                    crossref_match=ver_data["crossref_match"],
                    semantic_scholar_match=ver_data["semantic_scholar_match"],
                    explanation=ver_data["explanation"],
                    metadata_mismatches=ver_data["metadata_mismatches"],
                )
                db.add(ver_obj)

                # Update counts
                st = ver_data["status"]
                if st == "VERIFIED":
                    counts["verified"] += 1
                elif st == "VERIFIED WITH METADATA ISSUES":
                    counts["metadata_issues"] += 1
                elif st == "POSSIBLE MATCH":
                    counts["possible_matches"] += 1
                elif st == "INVALID DOI":
                    counts["invalid_doi"] += 1
                else:
                    counts["not_found"] += 1

                refs_with_verifs_for_issues.append({
                    "reference": {
                        "id": ref_model.id,
                        "reference_number": ref_model.reference_number,
                        "raw_text": ref_model.raw_text,
                        "title": ref_model.title,
                        "doi": ref_model.doi,
                        "year": ref_model.year,
                        "authors": ref_model.authors,
                    },
                    "verification": ver_data
                })

            await db.commit()

            # Stage 7 & 8: Citation Context Extraction & Semantic Claim Validation
            paper.paper_stats = {**(paper.paper_stats or {}), 'verification_limitations': sorted({message for _, parsed in ref_models for message in parsed.get('_provider_diagnostics', [])}), 'verification_coverage_pct': round(100 * (counts['verified'] + counts['metadata_issues']) / len(ref_models), 1) if ref_models else 0}
            paper.progress_stage = "Extracting in-text citations & evaluating semantic relevance"
            await db.commit()

            ref_dicts = [{"id": rm.id, "reference_number": rm.reference_number, "raw_text": rm.raw_text, "title": rm.title, "year": rm.year, "authors": rm.authors} for rm, _ in ref_models]
            citation_analysis = citation_context_extractor.extract_citations(
                extracted_pdf.get("pages", []),
                extracted_pdf.get("full_text", ""),
                ref_dicts,
                paper.sections or []
            )

            # Persist CitationOccurrences with Semantic Analysis
            sem_relevance_scores = []
            for occ in citation_analysis.get("occurrences", []):
                # Find matched abstract from verification results
                matched_ref_ver = next((r["verification"] for r in refs_with_verifs_for_issues if r["reference"]["id"] == occ.get("reference_id")), None)
                accepted = matched_ref_ver and matched_ref_ver.get("status") in {"VERIFIED", "VERIFIED WITH METADATA ISSUES"}
                ref_abstract = matched_ref_ver.get("matched_abstract") if accepted else None
                ref_title = matched_ref_ver.get("matched_title") if accepted else None

                sem_eval = semantic_validator.evaluate_citation_claim(occ["sentence"], ref_title, ref_abstract)
                if sem_eval["status"] != "INSUFFICIENT EVIDENCE":
                    sem_relevance_scores.append(sem_eval["relevance_score"])

                occ_obj = CitationOccurrence(
                    paper_id=paper_id,
                    reference_id=occ.get("reference_id"),
                    citation_marker=occ.get("citation_marker"),
                    page_number=occ.get("page_number", 1),
                    sentence=occ.get("sentence"),
                    section=occ.get("section", "Main Body"),
                    claim_text=occ.get("claim_text"),
                    semantic_relevance_score=sem_eval["relevance_score"],
                    semantic_status=sem_eval["status"],
                    explanation=sem_eval["explanation"],
                )
                db.add(occ_obj)
            await db.commit()

            avg_sem_relevance = sum(sem_relevance_scores) / len(sem_relevance_scores) if sem_relevance_scores else 0.0

            # Stage 9: Issue Detection (Duplicates, Orphans, Unused, Missing, Mismatches)
            paper.progress_stage = "Detecting citation issues and inconsistencies"
            await db.commit()

            all_issues = issue_detector.detect_all_issues(
                paper_id,
                refs_with_verifs_for_issues,
                citation_analysis,
                extracted_pdf.get("full_text", "")
            )
            if not raw_refs:
                all_issues.append({"issue_type": "EXTRACTION_LIMITATION", "severity": "WARNING", "title": "Bibliography extraction inconclusive", "description": "No bibliography entries were reliably extracted. Review PDF layout and reference headings; this does not imply missing references.", "details": {"recommended_action": "Use a text PDF with a clearly headed bibliography."}})
            for occ in citation_analysis.get("occurrences", []):
                ver = next((r['verification'] for r in refs_with_verifs_for_issues if r['reference']['id'] == occ.get('reference_id')), None)
                if ver and ver['status'] in {"VERIFIED", "VERIFIED WITH METADATA ISSUES"}:
                    assessment = semantic_validator.evaluate_citation_claim(occ['sentence'], ver.get('matched_title'), ver.get('matched_abstract'))
                    if assessment['status'] == 'LOW RELEVANCE':
                        all_issues.append({"reference_id": occ.get('reference_id'), "issue_type": "CONTEXT_MISMATCH", "severity": "INFO", "title": "Preliminary citation relevance concern", "description": assessment['explanation'], "details": {"sentence": occ['sentence'], "source_url": ver.get('matched_url'), "similarity_score": assessment['relevance_score'], "confidence": 0.4, "recommended_action": "Read the full cited source to assess support."}})

            # Persist Issues
            for iss in all_issues:
                iss_obj = PaperIssue(
                    paper_id=paper_id,
                    reference_id=iss.get("reference_id"),
                    issue_type=iss["issue_type"],
                    severity=iss["severity"],
                    title=iss["title"],
                    description=iss["description"],
                    details=iss.get("details", {}),
                )
                db.add(iss_obj)
            await db.commit()

            # Stage 10: Health Scoring
            paper.progress_stage = "Calculating ResearchGuard Health Score"
            await db.commit()

            duplicate_count = len([i for i in all_issues if i["issue_type"] == "DUPLICATE_REFERENCE"])
            orphan_count = len(citation_analysis.get("orphan_citations", []))
            unused_count = len(citation_analysis.get("unused_references", []))

            health_data = health_scorer.calculate_health_score(
                total_references=len(ref_models),
                verified_count=counts["verified"],
                metadata_issues_count=counts["metadata_issues"],
                possible_matches_count=counts["possible_matches"],
                not_found_count=counts["not_found"],
                invalid_doi_count=counts["invalid_doi"],
                duplicate_count=duplicate_count,
                orphan_count=orphan_count,
                unused_count=unused_count,
                citation_coverage_pct=citation_analysis.get("citation_coverage_pct", 100.0),
                semantic_relevance_pct=avg_sem_relevance,
            )

            paper.health_score = health_data["health_score"]
            paper.health_rating = health_data["health_rating"]
            paper.score_breakdown = health_data["breakdown"]

            # Finalize paper status
            paper.processing_status = "completed"
            paper.progress_stage = "Analysis Completed Successfully"
            paper.error_message = None
            await db.commit()
            await db.refresh(paper)

            return paper

        except Exception as e:
            await db.rollback()
            paper.processing_status = "failed"
            paper.progress_stage = "Failed during analysis"
            paper.error_message = str(e)
            await db.commit()
            raise e

analysis_pipeline = AnalysisPipeline()
