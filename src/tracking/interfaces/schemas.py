from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel


class TrackingEventRequest(BaseModel):
    event_type: Literal["sensor", "stage_change"]
    product_id: str
    stage: str

    # Específicos de "sensor"
    sensor_type: str | None = None
    reading_value: float | None = None
    unit: str | None = None

    # Específicos de "stage_change"
    previous_stage: str | None = None
    responsible: str | None = None


class TrackingEventResponse(BaseModel):
    event_type: str
    product_id: str
    stage: str
    timestamp: datetime
    details: dict[str, Any]
