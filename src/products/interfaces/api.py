from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.forecasting.application.authorized_forecast_report_proxy import (
    AuthorizedForecastReportProxy,
)
from src.forecasting.application.generate_forecast_report import GenerateForecastReportUseCase
from src.forecasting.domain.report_service import ForecastAccessDenied
from src.forecasting.interfaces.schemas import ForecastReportResponse
from src.products.application.product_overview_facade import ProductOverviewFacade
from src.products.interfaces.schemas import ProductOverviewResponse
from src.shared.auth_dependencies import bearer_token
from src.shared.database import get_db
from src.tracking.infrastructure.repository import SqlTrackingEventRepository

router = APIRouter(prefix="/products", tags=["products"])


def _build_facade(
    db: Session = Depends(get_db),
    token: str | None = Depends(bearer_token),
) -> ProductOverviewFacade:
    tracking_repository = SqlTrackingEventRepository(db)
    forecast_service = AuthorizedForecastReportProxy(
        GenerateForecastReportUseCase(tracking_repository), token
    )
    return ProductOverviewFacade(tracking_repository, forecast_service)


@router.get("/{product_id}/overview", response_model=ProductOverviewResponse)
def get_product_overview(
    product_id: str,
    facade: ProductOverviewFacade = Depends(_build_facade),
):
    try:
        overview = facade.get_overview(product_id)
    except ForecastAccessDenied as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return ProductOverviewResponse(
        product_id=overview.product_id,
        current_stage=overview.current_stage,
        last_event_at=overview.last_event_at,
        events_count=overview.events_count,
        forecast=ForecastReportResponse(**overview.forecast),
    )
