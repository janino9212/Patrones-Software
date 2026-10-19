from datetime import datetime, timezone

from src.forecasting.application.generate_forecast_report import GenerateForecastReportUseCase
from src.tracking.domain.entities import StageChangeTrackingEvent


class _FakeTrackingRepository:
    def __init__(self, events):
        self._events = events

    def save(self, event):
        raise AssertionError("forecasting no debe escribir en tracking")

    def list_by_product(self, product_id):
        return [e for e in self._events if e.product_id == product_id]


def _event(product_id: str) -> StageChangeTrackingEvent:
    return StageChangeTrackingEvent(
        product_id=product_id,
        stage="transporte",
        timestamp=datetime.now(timezone.utc),
        previous_stage="fabricacion",
        responsible="Planta 1",
    )


def test_report_without_events_has_zero_demand_and_insufficient_data():
    report = GenerateForecastReportUseCase(_FakeTrackingRepository([])).execute("PROD-1")

    assert report["predicted_demand"] == 0
    assert report["based_on_events"] == 0
    assert report["confidence_interval"] == [0, 0]
    assert report["trend"] == "insuficientes datos"


def test_report_scales_demand_with_number_of_product_events():
    events = [_event("PROD-1") for _ in range(4)] + [_event("OTRO")]

    report = GenerateForecastReportUseCase(_FakeTrackingRepository(events)).execute("PROD-1")

    assert report["based_on_events"] == 4
    assert report["predicted_demand"] == 50.0
    assert report["confidence_interval"] == [45.0, 55.0]
    assert report["trend"] == "alza"
