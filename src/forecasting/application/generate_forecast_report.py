from src.forecasting.domain.forecast_plan import ForecastPlanRepository
from src.forecasting.domain.forecast_report import BaseForecastReport
from src.forecasting.domain.report_decorators import (
    ConfidenceIntervalDecorator,
    SourceAnnotationDecorator,
    TrendAnnotationDecorator,
)
from src.tracking.domain.repository import TrackingEventRepository

_DEMAND_FACTOR = 12.5
_SOURCE_TRACKING_EVENTS = "eventos_tracking"


class GenerateForecastReportUseCase:
    """Arma el reporte de pronóstico de un producto y lo enriquece con
    decoradores.

    Si el producto tiene un pronóstico vigente (calculado con un modelo sobre
    su historial de demanda), el reporte parte de él. Si no, cae en la
    estimación simulada original: nº de eventos de tracking × 12.5."""

    def __init__(
        self,
        tracking_repository: TrackingEventRepository,
        plan_repository: ForecastPlanRepository | None = None,
    ):
        self._tracking_repository = tracking_repository
        self._plan_repository = plan_repository

    def execute(self, product_id: str) -> dict:
        events = self._tracking_repository.list_by_product(product_id)
        plan = self._plan_repository.get(product_id) if self._plan_repository else None

        if plan is not None:
            demand, source = plan.predicted_demand, plan.model
        else:
            demand, source = round(len(events) * _DEMAND_FACTOR, 2), _SOURCE_TRACKING_EVENTS

        report = BaseForecastReport(
            product_id=product_id, predicted_demand=demand, based_on_events=len(events)
        )
        report = ConfidenceIntervalDecorator(report)
        report = TrendAnnotationDecorator(report)
        report = SourceAnnotationDecorator(report, source)
        return report.generate()
