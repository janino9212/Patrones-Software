from datetime import datetime

from pydantic import BaseModel, Field

from src.forecasting.interfaces.schemas import ForecastReportResponse


class ProductOverviewResponse(BaseModel):
    product_id: str
    current_stage: str | None = None
    last_event_at: datetime | None = None
    events_count: int
    forecast: ForecastReportResponse


class CreateProductRequest(BaseModel):
    # Sin espacios: es el product_id que valida la cadena de tracking.
    code: str = Field(min_length=1, max_length=100, pattern=r"^\S+$")
    name: str = Field(min_length=1, max_length=120)
    category: str | None = Field(default=None, max_length=60)


class ProductResponse(BaseModel):
    code: str
    name: str
    category: str | None = None
    created_at: datetime
