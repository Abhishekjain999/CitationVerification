import httpx
import pytest
from app.services.scholarly.transport import ProviderClient, diagnostics
from app.services.scholarly.openalex import openalex_service
from app.services.scholarly.crossref import crossref_service
from app.services.scholarly.semantic_scholar import semantic_scholar_service


@pytest.mark.asyncio
async def test_rate_limit_is_retried_once(monkeypatch):
    replies = iter([429, 200])
    async def fake_get(self, url, **kwargs):
        return httpx.Response(next(replies), json={'message': {}}, headers={'Retry-After': '0'})
    async def no_wait(delay):
        pass
    monkeypatch.setattr(httpx.AsyncClient, 'get', fake_get)
    monkeypatch.setattr('app.services.scholarly.transport.asyncio.sleep', no_wait)
    async with ProviderClient() as client:
        result = await client.get('https://api.crossref.org/works')
    assert result.status_code == 200


@pytest.mark.asyncio
async def test_network_failure_is_recorded(monkeypatch):
    async def fake_get(self, url, **kwargs):
        raise httpx.ConnectError('unavailable')
    monkeypatch.setattr(httpx.AsyncClient, 'get', fake_get)
    messages = []
    diagnostics.set(messages)
    async with ProviderClient() as client:
        with pytest.raises(httpx.ConnectError):
            await client.get('https://api.example.org/works')
    assert 'ConnectError' in messages[0]


def test_partial_provider_records():
    assert crossref_service._format_work({'title': ['A work'], 'author': None})['authors'] == []
    assert openalex_service._format_work({'title': 'A work', 'open_access': None, 'authorships': None})['abstract'] is None
    assert semantic_scholar_service._format_paper({'title': 'A work', 'authors': None})['doi'] is None
