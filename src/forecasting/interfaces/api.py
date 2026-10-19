from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.forecasting.application.generate_forecast_report import GenerateForecastReportUseCase
from src.forecasting.interfaces.schemas import ForecastReportResponse
from src.shared.database import get_db
from src.tracking.infrastructure.repository import SqlTrackingEventRepository


router = APIRouter(prefix="/forecasting", tags=["forecasting"])


def _build_use_case(db: Session = Depends(get_db)) -> GenerateForecastReportUseCase:
    tracking_repository = SqlTrackingEventRepository(db)
    return GenerateForecastReportUseCase(tracking_repository)


@router.get("/reports/{product_id}", response_model=ForecastReportResponse)
def get_forecast_report(product_id: str, use_case: GenerateForecastReportUseCase = Depends(_build_use_case)):
    data = use_case.execute(product_id)
    return ForecastReportResponse(**data)