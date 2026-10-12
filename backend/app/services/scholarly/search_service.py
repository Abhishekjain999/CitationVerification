import asyncio
from typing import List, Dict, Any
import re
from app.services.scholarly.openalex import openalex_service
from app.services.scholarly.crossref import crossref_service
from app.services.scholarly.semantic_scholar import semantic_scholar_service
from app.services.normalization import normalize_doi
from app.services.scholarly.transport import diagnostics

class ScholarlySearchService:
    """Orchestrates multi-strategy asynchronous queries across OpenAlex, Crossref, and Semantic Scholar."""

    async def search_reference(self, parsed_ref: Dict[str, Any]) -> List[Dict[str, Any]]:
        messages = []
        diagnostics.set(messages)
        parsed_ref['_provider_diagnostics'] = messages
        title = parsed_ref.get("title")
        authors = parsed_ref.get("authors") or []
        year = parsed_ref.get("year")
        doi = normalize_doi(parsed_ref.get("doi"))
        raw_text = parsed_ref.get("raw_text", "")

        candidates: List[Dict[str, Any]] = []

        # 1. Strategy: Direct DOI lookup if DOI exists
        doi_candidates = []
        if doi:
            doi_candidates = await self._search_by_doi(doi)
            candidates.extend(doi_candidates)

        # If high-confidence DOI match found, return candidates immediately
        if candidates and any(c.get("doi") and c.get("doi").lower() == doi.lower() for c in candidates):
            # Continue to fetch additional candidates for cross-validation
            pass

        # 2. Strategy: Title queries across all 3 databases
        if title and len(title.strip()) > 4:
            clean_title = re.sub(r'[\"\'“”«»\(\)\[\]]', '', title).strip()
            
            # Formulate query variants
            queries = [clean_title]
            first_author = authors[0] if authors and authors[0] != "Unknown Author" else None
            if first_author:
                clean_author = first_author.split(",")[0].strip()
                queries.append(f"{clean_title} {clean_author}")
            if year:
                queries.append(f"{clean_title} {year}")

            # Run searches concurrently
            search_tasks = []
            # Primary: OpenAlex
            search_tasks.append(openalex_service.search_by_title(clean_title, limit=3))
            # Secondary: Crossref
            search_tasks.append(crossref_service.search_by_title(clean_title, limit=3))
            # Secondary: Crossref Bibliographic
            if len(raw_text) > 10:
                search_tasks.append(crossref_service.search_by_bibliographic(raw_text[:200], limit=3))
            # Third: Semantic Scholar
            search_tasks.append(semantic_scholar_service.search_by_title(clean_title, limit=3))

            results_list = await asyncio.gather(*search_tasks, return_exceptions=True)
            for res in results_list:
                if isinstance(res, list):
                    candidates.extend(res)

        # 3. Deduplicate and merge candidate papers by DOI or Normalized Title
        merged_candidates = self._merge_and_deduplicate(candidates)
        return merged_candidates

    async def _search_by_doi(self, doi: str) -> List[Dict[str, Any]]:
        tasks = [
            crossref_service.get_by_doi(doi),
            openalex_service.get_by_doi(doi),
            semantic_scholar_service.get_by_doi(doi),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        doi_candidates = []
        for res in results:
            if isinstance(res, dict) and res.get("title"):
                doi_candidates.append({**res, "doi_lookup": True})
        return doi_candidates

    def _merge_and_deduplicate(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicates candidates while tracking multi-source confirmations."""
        merged: Dict[str, Dict[str, Any]] = {}

        for c in candidates:
            if not c or not c.get("title"):
                continue

            doi = (c.get("doi") or "").lower().strip()
            norm_title = re.sub(r'[^a-z0-9]', '', c.get("title", "").lower())

            key = doi if doi else norm_title
            if not key:
                continue

            source = c.get("source_api", "Unknown")

            if key not in merged:
                merged[key] = {
                    **c,
                    "all_sources": [source],
                    "source_records": {source: c}
                }
            else:
                existing = merged[key]
                if source not in existing["all_sources"]:
                    existing["all_sources"].append(source)
                existing["source_records"][source] = c
                
                # Fill missing metadata fields from other sources
                if not existing.get("abstract") and c.get("abstract"):
                    existing["abstract"] = c.get("abstract")
                if c.get('doi_lookup'):
                    existing['doi_lookup'] = True
                if not existing.get("doi") and c.get("doi"):
                    existing["doi"] = c.get("doi")
                if not existing.get("publication_year") and c.get("publication_year"):
                    existing["publication_year"] = c.get("publication_year")
                if not existing.get("venue") and c.get("venue"):
                    existing["venue"] = c.get("venue")
                if not existing.get("authors") and c.get("authors"):
                    existing["authors"] = c.get("authors")
                if c.get("citation_count", 0) > existing.get("citation_count", 0):
                    existing["citation_count"] = c.get("citation_count")

        return list(merged.values())

scholarly_search_service = ScholarlySearchService()
