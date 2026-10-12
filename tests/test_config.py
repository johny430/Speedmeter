import pytest
from pydantic import ValidationError

from config import MeasurementConfig
from constants import DEFAULT_REQUESTS, DEFAULT_TIMEOUT


def test_config_defaults(example_url: str) -> None:
    config = MeasurementConfig(url=example_url)

    assert config.requests == DEFAULT_REQUESTS
    assert config.timeout == DEFAULT_TIMEOUT


@pytest.mark.parametrize(
    ("overrides", "invalid_field"),
    [
        ({"url": "ftp://example.com/image.jpg"}, "url"),
        ({"url": "example.com/image.jpg"}, "url"),
        ({"url": "http://"}, "url"),
        ({"requests": 0}, "requests"),
        ({"timeout": 0}, "timeout"),
        ({"timeout": float("inf")}, "timeout"),
    ],
)
def test_config_rejects_invalid_values(
    example_url: str, overrides: dict[str, object], invalid_field: str
) -> None:
    fields = {"url": example_url, **overrides}

    with pytest.raises(ValidationError) as error:
        MeasurementConfig.model_validate(fields)

    assert error.value.errors()[0]["loc"] == (invalid_field,)
