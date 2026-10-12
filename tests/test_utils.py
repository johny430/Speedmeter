import pytest

from utils import to_megabytes


def test_to_megabytes_uses_decimal_units() -> None:
    megabytes = to_megabytes(2_500_000)

    assert megabytes == pytest.approx(2.5)
