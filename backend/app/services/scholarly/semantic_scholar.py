from app.services.scholarly.transport import ProviderClient
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.cache import scholarly_cache

class SemanticScholarService:
    """Queries Semantic Scholar Academic Graph API."""

    BASE_SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
    BASE_PAPER_URL = "https://api.semanticscholar.org/graph/v1/paper"

    def __init__(self):
        self.headers = {
            "User-Agent": f"ResearchGuard/{settings.VERSION}",
            "Accept": "application/json",
        }
        if settings.SEMANTIC_SCHOLAR_API_KEY:
            self.headers["x-api-key"] = settings.SEMANTIC_SCHOLAR_API_KEY

    async def search_by_title(self, title: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not title or len(title.strip()) < 3:
            return []

        cache_key = f"s2:title:{title.strip().lower()}"
        cached = scholarly_cache.get(cache_key)
        if cached is not None:
            return cached

        params = {
            "query": title.strip(),
            "limit": limit,
            "fields": "title,authors,year,venue,publicationVenue,abstract,citationCount,externalIds,url,openAccessPdf",
        }

        try:
            async with ProviderClient() as client:
                resp = await client.get(self.BASE_SEARCH_URL, params=params, headers=self.headers)
                if resp.status_code == 200:
                    data = resp.json()
                    papers = data.get("data", [])
                    results = [self._format_paper(p) for p in papers]
                    scholarly_cache.set(cache_key, results)
                    return results
        except Exception:
            pass

        return []

    async def get_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        if not doi:
            return None

        clean_doi = doi.strip()
        if clean_doi.startswith("https://doi.org/"):
            clean_doi = clean_doi.replace("https://doi.org/", "")

        cache_key = f"s2:doi:{clean_doi.lower()}"
        cached = scholarly_cache.get(cache_key)
        if cached is not None:
            return cached

        url = f"{self.BASE_PAPER_URL}/DOI:{clean_doi}"
        params = {
            "fields": "title,authors,year,venue,publicationVenue,abstract,citationCount,externalIds,url,openAccessPdf"
        }

        try:
            async with ProviderClient() as client:
                resp = await client.get(url, params=params, headers=self.headers)
                if resp.status_code == 200:
                    paper = resp.json()
                    formatted = self._format_paper(paper)
                    scholarly_cache.set(cache_key, formatted)
                    return formatted
        except Exception:
            pass

        return None

    def _format_paper(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        # Extract authors
        authors = []
        for a in paper.get("authors") or []:
            if a.get("name"):
                authors.append(a.get("name"))

        # External IDs
        ext_ids = paper.get("externalIds", {}) or {}
        doi = ext_ids.get("DOI")

        # Venue
        venue = paper.get("venue")
        pub_venue = paper.get("publicationVenue") or {}
        if not venue and pub_venue:
            venue = pub_venue.get("name")

        url = paper.get("url") or (f"https://doi.org/{doi}" if doi else None)

        return {
            "source_api": "Semantic Scholar",
            "id": paper.get("paperId"),
            "title": paper.get("title"),
            "authors": authors,
            "publication_year": paper.get("year"),
            "publication_date": str(paper.get("year")) if paper.get("year") else None,
            "venue": venue,
            "journal": venue,
            "conference": venue if pub_venue.get("type") == "conference" else None,
            "publisher": pub_venue.get("publisher"),
            "doi": doi,
            "url": url,
            "citation_count": paper.get("citationCount", 0),
            "abstract": paper.get("abstract"),
            "is_oa": bool(paper.get("openAccessPdf")),
            "raw_data": paper,
        }

semantic_scholar_service = SemanticScholarService()
