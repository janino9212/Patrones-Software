from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class IngestSensorRequest(BaseModel):
    product_id: str = Field(min_length=1, max_length=100)
    stage: str = Field(min_length=1, max_length=50)
    # No hay hardware real: permite indicar la lectura que entregará el
    # dispositivo simulado. Sin él, cada fabricante devuelve su valor fijo.
    simulated_value: float | None = Field(default=None, ge=-1000, le=1000)

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"product_id": "PROD-001", "stage": "transporte"}]}
    )


class IngestSensorResponse(BaseModel):
    product_id: str
    sensor_type: str
    reading_value: float
    unit: str
    notified_via: str
    message: str
    device_id: str | None = None


class VendorResponse(BaseModel):
    code: str
    label: str
    sensor_type: str
    unit: str
    accepts_simulated_value: bool


class ReadingResponse(BaseModel):
    device_id: str
    sensor_type: str
    value: float
    unit: str
    product_id: str
    stage: str
    received_at: datetime


class AlertResponse(BaseModel):
    device_id: str
    sensor_type: str
    value: float
    unit: str
    product_id: str
    message: str
    raised_at: datetime


class DeviceResponse(BaseModel):
    device_id: str
    sensor_type: str
    last_value: float
    unit: str
    last_product_id: str
    last_seen_at: datetime
    readings_count: int
