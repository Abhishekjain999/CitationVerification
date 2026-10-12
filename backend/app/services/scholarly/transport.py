"""Bounded provider requests with per-host pacing and request-local diagnostics."""
import asyncio
import time
from contextvars import ContextVar
from urllib.parse import urlparse
import httpx
from app.core.config import settings

diagnostics = ContextVar('provider_diagnostics', default=None)


class ProviderClient:
    _locks = {}
    _next_request = {}

    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=settings.API_TIMEOUT, follow_redirects=True)
        return self

    async def __aexit__(self, *args):
        await self.client.aclose()

    async def get(self, url, **kwargs):
        host = urlparse(url).netloc
        # One in-flight request per provider, including bibliographic searches.
        key = (asyncio.get_running_loop(), host)
        lock = self._locks.setdefault(key, asyncio.Lock())
        async with lock:
            for attempt in range(2):
                delay = self._next_request.get(key, 0) - time.monotonic()
                if delay > 0:
                    await asyncio.sleep(delay)
                self._next_request[key] = time.monotonic() + 1.0
                try:
                    response = await self.client.get(url, **kwargs)
                except httpx.HTTPError as exc:
                    self._record(host, type(exc).__name__)
                    raise
                if response.status_code == 429 and attempt == 0:
                    retry = response.headers.get('Retry-After', '2')
                    delay = min(10.0, max(1.0, float(retry))) if retry.replace('.', '', 1).isdigit() else 2.0
                    await asyncio.sleep(delay)
                    continue
                if response.status_code != 200:
                    self._record(host, f'HTTP {response.status_code}')
                return response

    @staticmethod
    def _record(host, reason):
        messages = diagnostics.get()
        if messages is not None:
            messages.append(f'{host}: {reason}')
