from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.forecasting.domain.report_service import ForecastAccessDenied
from src.forecasting.interfaces.api import build_forecast_service
from src.forecasting.interfaces.schemas import ForecastReportResponse
from src.products.application.product_overview_facade import ProductOverviewFacade
from src.products.domain.product import Product, ProductAlreadyExists
from src.products.infrastructure.repository import SqlProductRepository
from src.products.interfaces.schemas import (
    CreateProductRequest,
    ProductOverviewResponse,
    ProductResponse,
)
from src.shared.auth_dependencies import bearer_token, current_user
from src.shared.database import get_db
from src.tracking.infrastructure.repository import SqlTrackingEventRepository

router = APIRouter(prefix="/products", tags=["products"])


def _build_facade(
    db: Session = Depends(get_db),
    token: str | None = Depends(bearer_token),
) -> ProductOverviewFacade:
    return ProductOverviewFacade(SqlTrackingEventRepository(db), build_forecast_service(db, token))


@router.get("", response_model=list[ProductResponse], dependencies=[Depends(current_user)])
def list_products(db: Session = Depends(get_db)):
    return [_to_response(product) for product in SqlProductRepository(db).list_all()]


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(current_user)],
)
def create_product(payload: CreateProductRequest, db: Session = Depends(get_db)):
    product = Product(
        code=payload.code,
        name=payload.name.strip(),
        category=payload.category.strip() if payload.category else None,
        created_at=datetime.now(timezone.utc),
    )
    try:
        SqlProductRepository(db).add(product)
    except ProductAlreadyExists as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _to_response(product)


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


def _to_response(product: Product) -> ProductResponse:
    return ProductResponse(
        code=product.code,
        name=product.name,
        category=product.category,
        created_at=product.created_at,
    )
