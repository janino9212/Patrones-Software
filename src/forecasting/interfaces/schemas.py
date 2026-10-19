from pydantic import BaseModel


class ForecastReportResponse(BaseModel):
    product_id: str
    predicted_demand: float
    based_on_events: int
    confidence_interval: list[float]
    trend: str