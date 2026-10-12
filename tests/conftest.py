import pytest

from models import Report, Sample


@pytest.fixture
def example_url() -> str:
    """Адрес только для валидации и моков, по сети не запрашивается."""
    return "https://example.com/image.jpg"


@pytest.fixture
def payload() -> bytes:
    return b"\xff" * 300_000


@pytest.fixture
def samples() -> tuple[Sample, ...]:
    return Sample(size=3_000_000, duration=1.0), Sample(size=1_000_000, duration=3.0)


@pytest.fixture
def report(samples: tuple[Sample, ...]) -> Report:
    return Report(samples=samples)
