# ResearchGuard

Research paper metadata, bibliography verification and citation consistency checks, with a React dashboard and downloadable PDF/JSON evidence reports.

## Run locally

Requires Python 3.12+ and Node.js 22+. From the repository root in PowerShell:

```powershell
py -3.12 -m venv .venv-rg
.venv-rg/Scripts/python.exe -m pip install -r backend/requirements.txt
Copy-Item backend/.env.example backend/.env
.venv-rg/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

In a second terminal:

```powershell
cd frontend
npm ci
npm run dev -- --host 127.0.0.1
```

Open http://127.0.0.1:5173. API documentation: http://127.0.0.1:8000/docs.
The existing `.venv` points to a missing Python installation on this machine; use `.venv-rg`, created and installed during the handoff. If `py` is unavailable, use any installed Python 3.12+ interpreter for the first command.

Set `VITE_API_URL` in `frontend/.env` to change the API URL (default `http://127.0.0.1:8000/api`).

## Workflow

Upload a text PDF, start analysis, and inspect the dashboard, reference roster, citation contexts, issues, and report. Uploads are limited to 50 MB. Empty, malformed, encrypted, and scanned/textless PDFs produce a clear error. Apply OCR externally before uploading scanned papers.

The demo button loads curated sample findings and labels them as demonstration data. Demo confidence values and findings are illustrative, not results of a live scholarly search. Upload `sample_papers/Attention_Transformer_Sample.pdf` for the actual pipeline. The demo can be loaded repeatedly without duplicating records.

## Architecture and persistence

`backend/app/services` separates extraction, parsing, matching, verification, citation analysis, issues, scoring, reports and orchestration. FastAPI routes use Pydantic schemas; SQLAlchemy stores documents, references, verification evidence/timestamps, citations, issues and score components. SQLite is the existing local development default. PostgreSQL is supported through `DATABASE_URL=postgresql+asyncpg://...` in `backend/.env`; create the database/user first. The async driver is included. Tables are initialized on startup. This change adds no database columns; existing data does not need a schema migration. Future schema changes require migrations rather than relying on `create_all` to alter tables. An unavailable database returns HTTP 503 with a diagnostic.

`POST /api/papers/{id}/analyze` returns 202 and queues a background analysis using a separate database session. Poll `GET /api/papers/{id}` for persisted stage/status. Duplicate starts during an active analysis are ignored. Reanalysis removes previous derived rows. Reverification refreshes issues, citation relevance and the aggregate score. An interrupted job is marked failed on server restart and can be retried.

Background tasks are an MVP facility: use **one backend worker**. Jobs do not resume across restarts. A production deployment needs a durable queue, authentication/access controls, an upload retention policy, migrations, and shared provider rate limiting. Do not expose this local application publicly as-is.

## Providers and evidence

Crossref, OpenAlex and Semantic Scholar have independent integrations, cached successful responses, one in-flight request per provider, one-second request spacing, bounded 429 retries and timeouts. A provider failure does not fail the paper. Failure diagnostics are included in inconclusive explanations. Optional contact emails/keys are read from `.env`; no paid API key is required for the core path. Do not commit `.env`.

Provider policies can change. Crossref supports public access and a contact email for its polite pool: https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/. OpenAlex authentication guidance: https://help.openalex.org/api/authentication/. Availability/rate limits can affect evidence coverage.

Legacy status identifiers are retained for API/UI compatibility:

| Status | Meaning |
| --- | --- |
| VERIFIED | Strong multidimensional agreement with DOI or corroborating author/year metadata |
| VERIFIED WITH METADATA ISSUES | Identified candidate with metadata discrepancies; review individual fields |
| POSSIBLE MATCH | Candidate found, insufficient confidence for verification |
| NOT FOUND | Unverified/inconclusive; never proof of fabrication |
| INVALID DOI | A direct lookup of the supplied DOI returned a work with a substantially different title |

Titles, authors, year, venue and normalized DOIs contribute to matching. Candidate evidence URLs, source records, discrepancies and explanations are exposed in reference details and the full JSON report. Missing API results do not establish that a DOI is invalid.

## Score rules

The deterministic 0–100 review score is the sum of:

| Component | Rule |
| --- | --- |
| Verification / 40 | `(verified + 0.8 × metadata issues + 0.4 × possible matches) / total × 40` |
| Metadata / 20 | `verified / total × 20` |
| Coverage / 15 | Fraction of bibliography entries cited in recognized body citations × 15 |
| Consistency / 15 | `15 − min(8, orphan occurrences × 3)` |
| Hygiene / 10 | `10 − min(10, invalid DOIs × 8) − min(4, duplicate pairs × 3) − min(2, unused references × 0.5)` |

Each component is bounded by zero and its maximum. The total is bounded to 5–100 when references exist; no reliably extracted references yields an extraction limitation. If at least half the references are unverified, the rating is **Inconclusive** and the UI displays **Verification incomplete** instead of a numerical rating. For adequate evidence coverage, ratings are Excellent ≥85, Good ≥70, Needs Review ≥50, Poor otherwise; these describe a review score, never integrity or misconduct. Components are shown in reports. Lexical relevance scores do not change this health score. This is not an academic integrity certification.

## Extraction and relevance limitations

- Bibliographies require a recognizable heading. Numbered entries preserve printed identifiers, including gaps. Wrapped entries and common APA author-year entries are supported heuristically. Two-column layouts, unusual styles, footnotes and malformed references can need manual review.
- Recognized citations include `[2]`, `[2,4;7]`, `[2–5]`, `(Smith, 2022)` and `Smith (2022)`, semicolon-separated author-year groups and year suffixes. Ranges have a 26-item safety cap; reversed/oversized ranges are not expanded. Ambiguous same-author/same-year entries are flagged for clarification rather than orphaned. The bibliography is excluded while appendix citations are included.
- Extraction heuristics do not establish publication metadata as authoritative. A bibliography DOI is not used as the uploaded paper DOI. A DOI alone does not imply open access.
- Relevance uses the established local TF-IDF, token similarity and keyword overlap approach. No large model download is required. Title-only evidence remains inconclusive. Only accepted candidate abstracts are assessed. An abstract is not full source text; overlap cannot prove or disprove support for a specific claim.
- Potential missing-citation flags are heuristic review suggestions. The system does not invent source findings or label unmatched references fabricated.

## Validation

```powershell
.venv-rg/Scripts/python.exe -m pytest -q
.venv-rg/Scripts/python.exe -m ruff check backend/app backend/tests --select F
cd frontend
npm run build
npm run lint
```

Install `ruff` separately to run backend lint. Tests use temporary databases and mocked providers, leaving the existing database intact. Coverage includes the exact `[1]–[8]` bibliography / `[2]–[4]` orphan regression, range/identifier normalization, author-year citations, bibliography boundaries, metadata, PDF errors, conservative DOI verification, scoring, API validation, duplicate job starts, reanalysis, reverification, repeated demo loads, partial provider failures and PDF/JSON reports.

`backend/requirements.lock.txt` captures the installed and tested Python versions (including the linter). For a reproducible setup, install that file instead of `requirements.txt`. Matching score thresholds can be overridden with `VERIFIED_SCORE`, `METADATA_MATCH_SCORE`, and `POSSIBLE_MATCH_SCORE`; the defaults are 82, 70 and 45, with additional metadata and title agreement guards.

PDF reports are generated with ReportLab and visually checked using Poppler. JSON reports contain the complete structured evidence, citations, issues and timestamps: `GET /api/papers/{id}/report?format=json`. PDF download uses the same route with the default `format=pdf`.

`sample_papers/BERT_N19-1423.pdf` is the authentic NAACL 2019 paper from https://aclanthology.org/N19-1423.pdf. Regression tests check its 56 references, full title, four authors, complete abstract, two-column reading order and citation links. This fixture exposed appendix/page-number parsing errors missed by the initial synthetic tests. When Codex starts the backend inside a network-restricted sandbox, external providers cannot be queried; run the backend from a normal terminal or an approved execution context. Provider failures are now displayed in analysis limitations.
