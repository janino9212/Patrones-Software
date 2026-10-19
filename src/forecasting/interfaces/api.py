from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.forecasting.application.authorized_forecast_report_proxy import (
    AuthorizedForecastReportProxy,
)
from src.forecasting.application.generate_forecast_report import GenerateForecastReportUseCase
from src.forecasting.domain.report_service import ForecastAccessDenied, ForecastReportService
from src.forecasting.interfaces.schemas import ForecastReportResponse
from src.shared.auth_dependencies import bearer_token
from src.shared.database import get_db
from src.tracking.infrastructure.repository import SqlTrackingEventRepository


router = APIRouter(prefix="/forecasting", tags=["forecasting"])


def build_protected_forecast_service(
    db: Session = Depends(get_db),
    token: str | None = Depends(bearer_token),
) -> ForecastReportService:
    """Arma el sujeto real y lo envuelve en el Proxy de protección (JWT)."""
    tracking_repository = SqlTrackingEventRepository(db)
    real_service = GenerateForecastReportUseCase(tracking_repository)
    return AuthorizedForecastReportProxy(real_service, token)


@router.get("/reports/{product_id}", response_model=ForecastReportResponse)
def get_forecast_report(
    product_id: str,
    service: ForecastReportService = Depends(build_protected_forecast_service),
):
    try:
        data = service.execute(product_id)
    except ForecastAccessDenied as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return ForecastReportResponse(**data)
