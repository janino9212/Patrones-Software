from datetime import datetime

from pydantic import BaseModel

from src.forecasting.interfaces.schemas import ForecastReportResponse


class ProductOverviewResponse(BaseModel):
    product_id: str
    current_stage: str | None = None
    last_event_at: datetime | None = None
    events_count: int
    forecast: ForecastReportResponse
