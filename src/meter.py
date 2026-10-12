import time
from collections.abc import AsyncGenerator

import httpx

from constants import CHUNK_SIZE, USER_AGENT
from exceptions import MeasurementError
from models import Sample


def create_client(timeout: float) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        headers={"User-Agent": USER_AGENT},
        timeout=timeout,
        follow_redirects=True,
    )


async def download(client: httpx.AsyncClient, url: str) -> Sample:
    """Скачивает тело ответа целиком; время — от отправки запроса до последнего байта."""
    size = 0
    started = time.perf_counter()
    async with client.stream("GET", url) as response:
        response.raise_for_status()
        async for chunk in response.aiter_raw(CHUNK_SIZE):
            size += len(chunk)
        duration = time.perf_counter() - started
    return Sample(size=size, duration=duration)


async def measure(client: httpx.AsyncClient, url: str, count: int) -> AsyncGenerator[Sample, None]:
    """Скачивает URL `count` раз; следующий запрос стартует после завершения предыдущего."""
    for number in range(1, count + 1):
        try:
            sample = await download(client, url)
        except httpx.HTTPError as error:
            raise MeasurementError(f"request #{number} failed: {_describe(error)}") from error
        yield sample


def _describe(error: httpx.HTTPError) -> str:
    if isinstance(error, httpx.HTTPStatusError):
        return f"HTTP {error.response.status_code} {error.response.reason_phrase}"
    return str(error) or type(error).__name__
