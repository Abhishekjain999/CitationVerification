from app.services.scholarly.transport import ProviderClient
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.cache import scholarly_cache

class CrossrefService:
    """Queries Crossref API for authoritative DOI and publication metadata."""

    BASE_URL = "https://api.crossref.org/works"

    def __init__(self):
        self.headers = {
            "User-Agent": f"ResearchGuard/{settings.VERSION} (mailto:{settings.CROSSREF_MAILTO})",
            "Accept": "application/json",
        }

    async def get_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        if not doi:
            return None

        clean_doi = doi.strip()
        if clean_doi.startswith("https://doi.org/"):
            clean_doi = clean_doi.replace("https://doi.org/", "")
        elif clean_doi.startswith("http://dx.doi.org/"):
            clean_doi = clean_doi.replace("http://dx.doi.org/", "")

        cache_key = f"crossref:doi:{clean_doi.lower()}"
        cached = scholarly_cache.get(cache_key)
        if cached is not None:
            return cached

        url = f"{self.BASE_URL}/{clean_doi}"
        try:
            async with ProviderClient() as client:
                resp = await client.get(url, headers=self.headers)
                if resp.status_code == 200:
                    data = resp.json()
                    item = data.get("message", {})
                    formatted = self._format_work(item)
                    scholarly_cache.set(cache_key, formatted)
                    return formatted
        except Exception:
            pass

        return None

    async def search_by_title(self, title: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not title or len(title.strip()) < 3:
            return []

        cache_key = f"crossref:title:{title.strip().lower()}"
        cached = scholarly_cache.get(cache_key)
        if cached is not None:
            return cached

        params = {
            "query.title": title.strip(),
            "rows": limit,
        }

        try:
            async with ProviderClient() as client:
                resp = await client.get(self.BASE_URL, params=params, headers=self.headers)
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get("message", {}).get("items", [])
                    results = [self._format_work(item) for item in items]
                    scholarly_cache.set(cache_key, results)
                    return results
        except Exception:
            pass

        return []

    async def search_by_bibliographic(self, query_str: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not query_str or len(query_str.strip()) < 5:
            return []

        cache_key = f"crossref:bib:{query_str.strip().lower()[:100]}"
        cached = scholarly_cache.get(cache_key)
        if cached is not None:
            return cached

        params = {
            "query.bibliographic": query_str.strip(),
            "rows": limit,
        }

        try:
            async with ProviderClient() as client:
                resp = await client.get(self.BASE_URL, params=params, headers=self.headers)
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get("message", {}).get("items", [])
                    results = [self._format_work(item) for item in items]
                    scholarly_cache.set(cache_key, results)
                    return results
        except Exception:
            pass

        return []

    def _format_work(self, item: Dict[str, Any]) -> Dict[str, Any]:
        # Extract title
        titles = item.get("title") or []
        title = titles[0] if titles else None

        # Extract authors
        authors = []
        for a in item.get("author") or []:
            given = a.get("given", "").strip()
            family = a.get("family", "").strip()
            if given and family:
                authors.append(f"{given} {family}")
            elif family:
                authors.append(family)
            elif a.get("name"):
                authors.append(a.get("name"))

        # Extract publication year
        year = None
        date_parts = (
            item.get("published-print", {}).get("date-parts")
            or item.get("published-online", {}).get("date-parts")
            or item.get("issued", {}).get("date-parts")
            or item.get("created", {}).get("date-parts")
        )
        if date_parts and len(date_parts) > 0 and len(date_parts[0]) > 0:
            year = date_parts[0][0]

        # Container title / Venue
        containers = item.get("container-title") or []
        venue = containers[0] if containers else None

        doi = item.get("DOI")
        url = item.get("URL") or (f"https://doi.org/{doi}" if doi else None)

        return {
            "source_api": "Crossref",
            "id": doi,
            "title": title,
            "authors": authors,
            "publication_year": year,
            "publication_date": str(year) if year else None,
            "venue": venue,
            "journal": venue,
            "conference": venue if item.get("type") in ["proceedings-article", "proceedings"] else None,
            "publisher": item.get("publisher"),
            "doi": doi,
            "url": url,
            "volume": item.get("volume"),
            "issue": item.get("issue"),
            "pages": item.get("page"),
            "citation_count": item.get("is-referenced-by-count", 0),
            "abstract": item.get("abstract"),
            "raw_data": item,
        }

crossref_service = CrossrefService()
