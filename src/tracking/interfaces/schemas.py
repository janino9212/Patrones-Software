from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "event_type": "sensor",
                    "product_id": "PROD-001",
                    "stage": "transporte",
                    "sensor_type": "temperatura",
                    "reading_value": 23.5,
                    "unit": "°C",
                },
                {
                    "event_type": "stage_change",
                    "product_id": "PROD-001",
                    "stage": "transporte",
                    "previous_stage": "fabricacion",
                    "responsible": "Julian Nino",
                },
            ]
        }
    )


class TrackingEventResponse(BaseModel):
    event_type: str
    product_id: str
    stage: str
    timestamp: datetime
    details: dict[str, Any]