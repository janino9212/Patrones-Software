from dataclasses import dataclass
from datetime import datetime

from src.forecasting.domain.report_service import ForecastReportService
from src.tracking.domain.repository import TrackingEventRepository


@dataclass(frozen=True)
class ProductOverview:
    product_id: str
    current_stage: str | None
    last_event_at: datetime | None
    events_count: int
    forecast: dict


class ProductOverviewFacade:
    """Facade (GoF): punto de entrada único para consultar el estado de un
    producto. Oculta que la respuesta sale de dos subsistemas (historial de
    `tracking` y reporte de `forecasting`), de modo que el cliente hace una
    sola llamada en vez de orquestar ambos módulos.

    El reporte se pide a través del puerto ForecastReportService, así que si
    ese servicio está protegido por el Proxy, la fachada no lo salta."""

    def __init__(
        self,
        tracking_repository: TrackingEventRepository,
        forecast_service: ForecastReportService,
    ):
        self._tracking_repository = tracking_repository
        self._forecast_service = forecast_service

    def get_overview(self, product_id: str) -> ProductOverview:
        forecast = self._forecast_service.execute(product_id)
        events = sorted(
            self._tracking_repository.list_by_product(product_id),
            key=lambda event: event.timestamp,
        )
        latest = events[-1] if events else None

        return ProductOverview(
            product_id=product_id,
            current_stage=latest.stage if latest else None,
            last_event_at=latest.timestamp if latest else None,
            events_count=len(events),
            forecast=forecast,
        )
