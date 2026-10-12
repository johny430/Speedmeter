import pytest

from cli import parse_config
from enums import ExitCode


def test_parse_config_reads_arguments(example_url: str) -> None:
    argv = [example_url, "--requests", "3", "--timeout", "5"]

    config = parse_config(argv)

    assert str(config.url) == example_url
    assert config.requests == 3
    assert config.timeout == 5.0


def test_parse_config_rejects_non_http_url(capsys: pytest.CaptureFixture[str]) -> None:
    argv = ["ftp://example.com/image.jpg"]

    with pytest.raises(SystemExit) as exit_info:
        parse_config(argv)

    assert exit_info.value.code == ExitCode.USAGE
    assert "argument url:" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("options", "message"),
    [
        (["--requests", "0"], "argument requests:"),
        (["--timeout", "abc"], "argument -t/--timeout:"),
    ],
)
def test_parse_config_rejects_invalid_options(
    example_url: str, options: list[str], message: str, capsys: pytest.CaptureFixture[str]
) -> None:
    argv = [example_url, *options]

    with pytest.raises(SystemExit) as exit_info:
        parse_config(argv)

    assert exit_info.value.code == ExitCode.USAGE
    assert message in capsys.readouterr().err
