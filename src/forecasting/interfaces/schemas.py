from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

# Mismo formato que valida la cadena de tracking: sin espacios, hasta 100.
ProductId = Field(min_length=1, max_length=100, pattern=r"^\S+$")
ModelName = Literal["moving_average", "exponential_smoothing", "linear_trend"]


class ForecastReportResponse(BaseModel):
    product_id: str
    predicted_demand: float
    based_on_events: int
    confidence_interval: list[float]
    trend: str
    source: str = "eventos_tracking"


class DemandRecordRequest(BaseModel):
    product_id: str = ProductId
    period: date
    quantity: float = Field(ge=0, le=1_000_000_000)


class DemandRecordResponse(BaseModel):
    product_id: str
    period: date
    quantity: float


class ForecastModelResponse(BaseModel):
    name: str
    label: str
    min_points: int


class ForecastPlanResponse(BaseModel):
    product_id: str
    model: str
    predicted_demand: float
    based_on_records: int
    generated_at: datetime
    can_undo: bool = False


class ForecastCommandRequest(BaseModel):
    action: Literal["generate", "recalculate"]
    product_id: str = ProductId
    model: ModelName | None = None


class UndoRequest(BaseModel):
    product_id: str = ProductId


class UndoResponse(BaseModel):
    product_id: str
    plan: ForecastPlanResponse | None = None


class CommandLogResponse(BaseModel):
    command: str
    product_id: str
    executed_at: datetime
    undone: bool
