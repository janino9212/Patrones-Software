from pydantic import BaseModel, ConfigDict


class IngestSensorRequest(BaseModel):
    product_id: str
    stage: str

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