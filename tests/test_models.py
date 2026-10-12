import pytest
from pydantic import ValidationError

from models import Report, Sample


def test_sample_speed() -> None:
    sample = Sample(size=5_000_000, duration=2.0)

    speed = sample.speed_mb_per_s

    assert speed == pytest.approx(2.5)


def test_report_aggregates_samples(samples: tuple[Sample, ...]) -> None:
    report = Report(samples=samples)

    assert report.total_bytes == 4_000_000
    assert report.total_mb == pytest.approx(4.0)
    assert report.total_time == pytest.approx(4.0)
    assert report.average_time == pytest.approx(2.0)
    assert report.speed_mb_per_s == pytest.approx(1.0)
    assert report.speed_mbit_per_s == pytest.approx(8.0)


def test_report_requires_samples() -> None:
    with pytest.raises(ValidationError) as error:
        Report(samples=())

    assert error.value.errors()[0]["loc"] == ("samples",)


@pytest.mark.parametrize(
    ("size", "duration", "invalid_field"),
    [(-1, 1.0, "size"), (1, 0.0, "duration"), (1, float("nan"), "duration")],
)
def test_sample_rejects_invalid_values(size: int, duration: float, invalid_field: str) -> None:
    with pytest.raises(ValidationError) as error:
        Sample(size=size, duration=duration)

    assert error.value.errors()[0]["loc"] == (invalid_field,)
