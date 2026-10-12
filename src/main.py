import asyncio
import logging
import sys
from collections.abc import Sequence

from cli import parse_config
from config import MeasurementConfig
from enums import ExitCode
from exceptions import MeasurementError
from logger import configure_logging
from meter import create_client, measure
from models import Report, Sample
from output import format_report, format_sample

logger = logging.getLogger(__name__)


async def run(config: MeasurementConfig) -> Report:
    logger.info("Downloading %s %d times", config.url, config.requests)
    samples: list[Sample] = []
    async with create_client(config.timeout) as client:
        async for sample in measure(client, str(config.url), config.requests):
            samples.append(sample)
            logger.info(format_sample(len(samples), sample))
    return Report(samples=tuple(samples))


def main(argv: Sequence[str] | None = None) -> ExitCode:
    config = parse_config(argv)
    try:
        report = asyncio.run(run(config))
    except MeasurementError as error:
        logger.error("%s", error)
        return ExitCode.FAILURE
    except KeyboardInterrupt:
        logger.warning("Interrupted")
        return ExitCode.INTERRUPTED
    for line in format_report(report):
        logger.info(line)
    return ExitCode.OK


if __name__ == "__main__":
    configure_logging()
    sys.exit(main())
