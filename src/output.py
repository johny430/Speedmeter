from models import Report, Sample


def format_sample(number: int, sample: Sample) -> str:
    return (
        f"#{number:<3} {sample.size_mb:8.2f} MB"
        f"  {sample.duration:7.3f} s  {sample.speed_mb_per_s:8.2f} MB/s"
    )


def format_report(report: Report) -> list[str]:
    return [
        f"Requests:      {len(report.samples)}",
        f"Downloaded:    {report.total_mb:.2f} MB",
        f"Average time:  {report.average_time:.3f} s",
        f"Speed:         {report.speed_mb_per_s:.2f} MB/s ({report.speed_mbit_per_s:.1f} Mbit/s)",
    ]
