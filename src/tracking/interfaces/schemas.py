from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class TrackingEventRequest(BaseModel):
    event_type: Literal["sensor", "stage_change"]
    # Los topes coinciden con el tamaño de las columnas de tracking_events.
    product_id: str = Field(max_length=100)
    stage: str = Field(max_length=50)

    # Específicos de "sensor"
    sensor_type: str | None = Field(default=None, max_length=50)
    reading_value: float | None = None
    unit: str | None = Field(default=None, max_length=20)

    # Específicos de "stage_change"
    previous_stage: str | None = Field(default=None, max_length=50)
    responsible: str | None = Field(default=None, max_length=100)

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