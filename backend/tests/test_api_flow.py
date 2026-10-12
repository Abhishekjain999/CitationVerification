import asyncio
from unittest.mock import AsyncMock
import pytest
import pymupdf
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.api import papers
from app.services.scholarly.search_service import scholarly_search_service
from app.core.config import settings


@pytest.fixture
def client(tmp_path, monkeypatch):
    engine = create_async_engine(f'sqlite+aiosqlite:///{tmp_path}/test.db')
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async def setup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(setup())
    async def database():
        async with sessions() as session:
            yield session
    app.dependency_overrides[get_db] = database
    monkeypatch.setattr(papers, 'AsyncSessionLocal', sessions)
    monkeypatch.setattr(settings, 'UPLOAD_DIR', tmp_path)
    monkeypatch.setattr(settings, 'REPORTS_DIR', tmp_path)
    # Do not enter app lifespan: isolate tests from the user's existing database.
    test_client = TestClient(app)
    yield test_client
    test_client.close()
    app.dependency_overrides.clear()
    asyncio.run(engine.dispose())


def pdf_bytes():
    with pymupdf.open() as doc:
        page = doc.new_page()
        text = 'Research Methods and Evidence\nAlice Smith\nAbstract\nWe study evidence in research.\nIntroduction\nPrior work [2], [3], and [4] describes this method.\nReferences\n'
        text += '\n'.join(f'[{i}] Smith, J. (2020). Research method {i}. Science.' for i in range(1, 9))
        page.insert_text((40, 40), text, fontsize=10)
        return doc.tobytes()


def test_upload_validation(client, monkeypatch):
    assert client.post('/api/papers/upload', files={'file': ('file.txt', b'hello')}).status_code == 400
    assert client.post('/api/papers/upload', files={'file': ('file.pdf', b'broken')}).status_code == 422
    assert client.post('/api/papers/upload', files={'file': ('file.pdf', b'')}).status_code == 400
    monkeypatch.setattr(settings, 'MAX_FILE_SIZE_MB', 0)
    assert client.post('/api/papers/upload', files={'file': ('file.pdf', pdf_bytes())}).status_code == 413


def test_full_analysis_and_reanalysis(client, monkeypatch):
    monkeypatch.setattr(scholarly_search_service, 'search_reference', AsyncMock(return_value=[]))
    upload = client.post('/api/papers/upload', files={'file': ('paper.pdf', pdf_bytes(), 'application/pdf')})
    assert upload.status_code == 200, upload.text
    paper_id = upload.json()['id']
    assert client.get(f'/api/papers/{paper_id}/report').status_code == 409
    for _ in range(2):
        response = client.post(f'/api/papers/{paper_id}/analyze')
        assert response.status_code == 202, response.text
        paper = client.get(f'/api/papers/{paper_id}').json()
        assert paper['processing_status'] == 'completed', paper
        refs = client.get(f'/api/papers/{paper_id}/references').json()
        assert len(refs) == 8
        occurrences = client.get(f'/api/papers/{paper_id}/citations').json()
        assert len(occurrences) == 3
        issues = client.get(f'/api/papers/{paper_id}/issues').json()
        assert not any(i['issue_type'] == 'ORPHAN_CITATION' for i in issues)
        assert len([i for i in issues if i['issue_type'] == 'UNUSED_REFERENCE']) == 5
    report = client.get(f'/api/papers/{paper_id}/report?format=json')
    assert report.status_code == 200, report.text
    assert len(report.json()['references']) == 8
    report = client.get(f'/api/papers/{paper_id}/report')
    assert report.status_code == 200, report.text
    assert report.content.startswith(b'%PDF')
    score_before = client.get(f'/api/papers/{paper_id}').json()['health_score']
    async def verified(parsed):
        return [{'title': parsed['title'], 'authors': parsed['authors'], 'publication_year': parsed['year'], 'venue': parsed['venue'], 'all_sources': ['Crossref'], 'source_records': {}}]
    monkeypatch.setattr(scholarly_search_service, 'search_reference', verified)
    response = client.post(f"/api/references/{refs[1]['id']}/verify")
    assert response.status_code == 200, response.text
    assert client.get(f'/api/papers/{paper_id}').json()['health_score'] > score_before
    assert not any(i.get('reference_id') == refs[1]['id'] and i['issue_type'] == 'NOT_FOUND' for i in client.get(f'/api/papers/{paper_id}/issues').json())
    assert client.delete(f'/api/papers/{paper_id}').status_code == 200


def test_repeated_demo_load(client):
    for _ in range(2):
        response = client.post('/api/demo/load')
        assert response.status_code == 200, response.text
        paper_id = response.json()['id']
        assert response.json()['paper_stats']['demo']
        refs = client.get(f'/api/papers/{paper_id}/references').json()
        assert len(refs) == 8


def test_missing_paper_and_queued_deduplication(client, monkeypatch):
    assert client.get('/api/papers/nonexistent').status_code == 404
    assert client.post('/api/papers/nonexistent/analyze').status_code == 404
    job = AsyncMock()
    monkeypatch.setattr(papers, 'run_analysis_job', job)
    paper_id = client.post('/api/papers/upload', files={'file': ('paper.pdf', pdf_bytes())}).json()['id']
    assert client.post(f'/api/papers/{paper_id}/analyze').status_code == 202
    assert client.post(f'/api/papers/{paper_id}/analyze').status_code == 202
    assert job.await_count == 1
    assert client.delete(f'/api/papers/{paper_id}').status_code == 409


@pytest.mark.asyncio
async def test_partial_provider_failure(monkeypatch):
    from app.services.scholarly.search_service import openalex_service, crossref_service, semantic_scholar_service
    monkeypatch.setattr(openalex_service, 'search_by_title', AsyncMock(side_effect=TimeoutError))
    monkeypatch.setattr(semantic_scholar_service, 'search_by_title', AsyncMock(return_value=[]))
    monkeypatch.setattr(crossref_service, 'search_by_title', AsyncMock(return_value=[{'title': 'Useful work', 'source_api': 'Crossref'}]))
    result = await scholarly_search_service.search_reference({'title': 'Useful work'})
    assert len(result) == 1 and result[0]['title'] == 'Useful work'
