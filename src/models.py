from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt

from constants import BITS_PER_BYTE
from utils import to_megabytes


class Sample(BaseModel):
    """Один завершённый запрос: размер тела в байтах и время в секундах."""

    model_config = ConfigDict(frozen=True)

    size: NonNegativeInt
    duration: float = Field(gt=0, allow_inf_nan=False)

    @property
    def size_mb(self) -> float:
        return to_megabytes(self.size)

    @property
    def speed_mb_per_s(self) -> float:
        return self.size_mb / self.duration


class Report(BaseModel):
    model_config = ConfigDict(frozen=True)

    samples: tuple[Sample, ...] = Field(min_length=1)

    @property
    def total_bytes(self) -> int:
        return sum(sample.size for sample in self.samples)

    @property
    def total_mb(self) -> float:
        return to_megabytes(self.total_bytes)

    @property
    def total_time(self) -> float:
        return sum(sample.duration for sample in self.samples)

    @property
    def average_time(self) -> float:
        return self.total_time / len(self.samples)

    @property
    def speed_mb_per_s(self) -> float:
        # Суммарная пропускная способность, а не среднее скоростей отдельных запросов.
        return self.total_mb / self.total_time

    @property
    def speed_mbit_per_s(self) -> float:
        return self.speed_mb_per_s * BITS_PER_BYTE
