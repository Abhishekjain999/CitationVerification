from app.services.scholarly.transport import ProviderClient
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.cache import scholarly_cache

class OpenAlexService:
    """Queries OpenAlex API for scholarly metadata."""

    BASE_URL = "https://api.openalex.org/works"

    def __init__(self):
        self.headers = {
            "User-Agent": f"ResearchGuard/{settings.VERSION} (mailto:{settings.OPENALEX_EMAIL})",
            "Accept": "application/json",
        }

    async def search_by_title(self, title: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not title or len(title.strip()) < 3:
            return []

        cache_key = f"openalex:title:{title.strip().lower()}"
        cached = scholarly_cache.get(cache_key)
        if cached is not None:
            return cached

        params = {
            "search": title.strip(),
            "per-page": limit,
            "mailto": settings.OPENALEX_EMAIL,
        }

        try:
            async with ProviderClient() as client:
                resp = await client.get(self.BASE_URL, params=params, headers=self.headers)
                if resp.status_code == 200:
                    data = resp.json()
                    results = [self._format_work(w) for w in data.get("results", [])]
                    scholarly_cache.set(cache_key, results)
                    return results
        except Exception:
            # Silently handle network/timeout error
            pass

        return []

    async def get_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        if not doi:
            return None

        clean_doi = doi.strip().lower()
        if not clean_doi.startswith("10."):
            clean_doi = clean_doi.replace("https://doi.org/", "").replace("http://dx.doi.org/", "")

        cache_key = f"openalex:doi:{clean_doi}"
        cached = scholarly_cache.get(cache_key)
        if cached is not None:
            return cached

        url = f"{self.BASE_URL}/https://doi.org/{clean_doi}"
        try:
            async with ProviderClient() as client:
                resp = await client.get(url, headers=self.headers)
                if resp.status_code == 200:
                    work = resp.json()
                    formatted = self._format_work(work)
                    scholarly_cache.set(cache_key, formatted)
                    return formatted
        except Exception:
            pass

        return None

    def _reconstruct_abstract(self, inverted_index: Optional[Dict[str, List[int]]]) -> Optional[str]:
        if not inverted_index:
            return None
        try:
            word_positions = []
            for word, positions in inverted_index.items():
                for pos in positions:
                    word_positions.append((pos, word))
            word_positions.sort(key=lambda x: x[0])
            return " ".join([w[1] for w in word_positions])
        except Exception:
            return None

    def _format_work(self, work: Dict[str, Any]) -> Dict[str, Any]:
        # Extract authors
        authors = []
        for authorship in work.get("authorships") or []:
            author_obj = authorship.get("author", {})
            name = author_obj.get("display_name")
            if name:
                authors.append(name)

        # Primary location / venue
        primary_loc = work.get("primary_location") or {}
        source = primary_loc.get("source") or {}
        venue_name = source.get("display_name")
        host_org = source.get("host_organization_name")

        doi = work.get("doi")
        if doi and doi.startswith("https://doi.org/"):
            doi = doi.replace("https://doi.org/", "")

        abstract = self._reconstruct_abstract(work.get("abstract_inverted_index"))

        return {
            "source_api": "OpenAlex",
            "id": work.get("id"),
            "title": work.get("title") or work.get("display_name"),
            "authors": authors,
            "publication_year": work.get("publication_year"),
            "publication_date": work.get("publication_date"),
            "venue": venue_name,
            "journal": venue_name if source.get("type") == "journal" else None,
            "conference": venue_name if source.get("type") == "conference" else None,
            "publisher": host_org,
            "doi": doi,
            "url": work.get("doi") or work.get("id"),
            "citation_count": work.get("cited_by_count", 0),
            "abstract": abstract,
            "is_oa": (work.get("open_access") or {}).get("is_oa", False),
            "concepts": [c.get("display_name") for c in (work.get("concepts") or [])[:5]],
            "raw_data": work,
        }

openalex_service = OpenAlexService()
