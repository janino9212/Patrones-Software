from datetime import datetime, timedelta, timezone

import pytest

from src.forecasting.domain.report_service import ForecastAccessDenied
from src.products.application.product_overview_facade import ProductOverviewFacade
from src.tracking.domain.entities import StageChangeTrackingEvent


class _FakeTrackingRepository:
    def __init__(self, events):
        self._events = events
        self.queried: list[str] = []

    def save(self, event):
        raise AssertionError("la fachada no debe escribir en tracking")

    def list_by_product(self, product_id):
        self.queried.append(product_id)
        return [e for e in self._events if e.product_id == product_id]


class _FakeForecastService:
    def __init__(self, error: Exception | None = None):
        self._error = error
        self.calls: list[str] = []

    def execute(self, product_id: str) -> dict:
        self.calls.append(product_id)
        if self._error:
            raise self._error
        return {"product_id": product_id, "predicted_demand": 25.0, "trend": "alza"}


def _event(stage: str, minutes: int) -> StageChangeTrackingEvent:
    base = datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)
    return StageChangeTrackingEvent(
        product_id="PROD-1",
        stage=stage,
        timestamp=base + timedelta(minutes=minutes),
        previous_stage="anterior",
        responsible="Planta 1",
    )


def test_overview_combines_tracking_and_forecast_in_one_call():
    tracking = _FakeTrackingRepository([_event("fabricacion", 0), _event("transporte", 5)])
    forecast = _FakeForecastService()

    overview = ProductOverviewFacade(tracking, forecast).get_overview("PROD-1")

    assert overview.product_id == "PROD-1"
    assert overview.events_count == 2
    assert overview.forecast["predicted_demand"] == 25.0
    assert tracking.queried == ["PROD-1"]
    assert forecast.calls == ["PROD-1"]


def test_current_stage_is_the_stage_of_the_most_recent_event_regardless_of_order():
    tracking = _FakeTrackingRepository([_event("entrega", 10), _event("fabricacion", 0)])

    overview = ProductOverviewFacade(tracking, _FakeForecastService()).get_overview("PROD-1")

    assert overview.current_stage == "entrega"
    assert overview.last_event_at == datetime(2026, 10, 1, 12, 10, tzinfo=timezone.utc)


def test_overview_of_product_without_events_has_no_stage():
    overview = ProductOverviewFacade(
        _FakeTrackingRepository([]), _FakeForecastService()
    ).get_overview("PROD-1")

    assert overview.current_stage is None
    assert overview.last_event_at is None
    assert overview.events_count == 0


def test_access_denied_from_forecast_propagates_and_tracking_is_not_queried():
    tracking = _FakeTrackingRepository([_event("fabricacion", 0)])
    forecast = _FakeForecastService(error=ForecastAccessDenied("sin token"))

    with pytest.raises(ForecastAccessDenied):
        ProductOverviewFacade(tracking, forecast).get_overview("PROD-1")

    assert tracking.queried == []
