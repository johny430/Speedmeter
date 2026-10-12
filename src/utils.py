from constants import BYTES_PER_MB


def to_megabytes(size: int) -> float:
    return size / BYTES_PER_MB
