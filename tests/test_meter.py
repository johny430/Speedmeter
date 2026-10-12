from collections.abc import AsyncIterator
from contextlib import aclosing
from unittest.mock import Mock

import httpx
import pytest

from exceptions import MeasurementError
from meter import download, measure

pytestmark = pytest.mark.anyio


@pytest.fixture
def handler(payload: bytes) -> Mock:
    """Обработчик mock-транспорта: каждый запрос успешно отдаёт payload."""
    return Mock(side_effect=lambda _: httpx.Response(200, stream=httpx.ByteStream(payload)))


@pytest.fixture
async def client(handler: Mock) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        yield client


@pytest.fixture
async def flaky_client(payload: bytes) -> AsyncIterator[httpx.AsyncClient]:
    """Клиент, у которого первый запрос успешен, а второй падает с HTTP 503."""
    responses = [httpx.Response(status, stream=httpx.ByteStream(payload)) for status in (200, 503)]
    transport = httpx.MockTransport(Mock(side_effect=responses))
    async with httpx.AsyncClient(transport=transport) as client:
        yield client


@pytest.fixture
async def unreachable_client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.MockTransport(Mock(side_effect=httpx.ConnectError("connection refused")))
    async with httpx.AsyncClient(transport=transport) as client:
        yield client


async def test_download_reads_whole_body(
    client: httpx.AsyncClient, example_url: str, payload: bytes
) -> None:
    sample = await download(client, example_url)

    assert sample.size == len(payload)
    assert sample.duration > 0


async def test_measure_downloads_url_given_number_of_times(
    client: httpx.AsyncClient, handler: Mock, example_url: str, payload: bytes
) -> None:
    count = 3

    samples = [sample async for sample in measure(client, example_url, count)]

    assert [sample.size for sample in samples] == [len(payload)] * count
    assert handler.call_count == count


async def test_measure_sends_next_request_only_after_previous_completes(
    client: httpx.AsyncClient, handler: Mock, example_url: str
) -> None:
    async with aclosing(measure(client, example_url, count=3)) as series:
        await anext(series)

    assert handler.call_count == 1


async def test_measure_reports_failed_request_number(
    flaky_client: httpx.AsyncClient, example_url: str
) -> None:
    series = measure(flaky_client, example_url, count=2)
    await anext(series)

    with pytest.raises(MeasurementError) as error:
        await anext(series)

    assert str(error.value) == "request #2 failed: HTTP 503 Service Unavailable"


async def test_measure_wraps_transport_errors(
    unreachable_client: httpx.AsyncClient, example_url: str
) -> None:
    with pytest.raises(MeasurementError) as error:
        await anext(measure(unreachable_client, example_url, count=1))

    assert str(error.value) == "request #1 failed: connection refused"
    assert isinstance(error.value.__cause__, httpx.ConnectError)
