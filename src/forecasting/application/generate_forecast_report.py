from src.forecasting.domain.forecast_report import BaseForecastReport
from src.forecasting.domain.report_decorators import ConfidenceIntervalDecorator, TrendAnnotationDecorator
from src.tracking.domain.repository import TrackingEventRepository

_DEMAND_FACTOR = 12.5


class GenerateForecastReportUseCase:
    def __init__(self, tracking_repository: TrackingEventRepository):
        self._tracking_repository = tracking_repository

    def execute(self, product_id: str) -> dict:
        events = self._tracking_repository.list_by_product(product_id)
        baseline_demand = round(len(events) * _DEMAND_FACTOR, 2)

        report = BaseForecastReport(product_id=product_id, predicted_demand=baseline_demand, based_on_events=len(events))
        report = ConfidenceIntervalDecorator(report)
        report = TrendAnnotationDecorator(report)
        return report.generate()