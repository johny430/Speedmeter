import argparse
from collections.abc import Sequence

from pydantic import ValidationError

from config import MeasurementConfig
from constants import DEFAULT_REQUESTS, DEFAULT_TIMEOUT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Measure download speed by fetching a URL several times in a row.",
    )
    parser.add_argument("url", help="file to download, e.g. a large image")
    parser.add_argument(
        "-n",
        "--requests",
        type=int,
        default=DEFAULT_REQUESTS,
        help="number of sequential requests (default: %(default)s)",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="network timeout in seconds (default: %(default)s)",
    )
    return parser


def parse_config(argv: Sequence[str] | None = None) -> MeasurementConfig:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return MeasurementConfig(url=args.url, requests=args.requests, timeout=args.timeout)
    except ValidationError as error:
        parser.error(_describe(error))


def _describe(error: ValidationError) -> str:
    return "; ".join(
        f"argument {'.'.join(map(str, detail['loc']))}: {detail['msg']}"
        for detail in error.errors()
    )
