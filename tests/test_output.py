from models import Report, Sample
from output import format_report, format_sample


def test_format_sample() -> None:
    sample = Sample(size=2_500_000, duration=0.5)

    line = format_sample(3, sample)

    assert line == "#3       2.50 MB    0.500 s      5.00 MB/s"


def test_format_report(report: Report) -> None:
    lines = format_report(report)

    assert lines == [
        "Requests:      2",
        "Downloaded:    4.00 MB",
        "Average time:  2.000 s",
        "Speed:         1.00 MB/s (8.0 Mbit/s)",
    ]
