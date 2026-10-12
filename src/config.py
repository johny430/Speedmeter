from pydantic import BaseModel, ConfigDict, Field, HttpUrl, PositiveInt

from constants import DEFAULT_REQUESTS, DEFAULT_TIMEOUT


class MeasurementConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: HttpUrl
    requests: PositiveInt = DEFAULT_REQUESTS
    timeout: float = Field(default=DEFAULT_TIMEOUT, gt=0, allow_inf_nan=False)
