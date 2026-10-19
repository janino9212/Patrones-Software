from src.forecasting.domain.forecast_report import BaseForecastReport, ForecastReport
from src.forecasting.domain.report_decorators import (
    ConfidenceIntervalDecorator,
    TrendAnnotationDecorator,
)


def _base(predicted_demand: float = 100.0, based_on_events: int = 4) -> BaseForecastReport:
    return BaseForecastReport("PROD-1", predicted_demand, based_on_events)


def test_base_report_contains_only_core_fields():
    assert _base().generate() == {
        "product_id": "PROD-1",
        "predicted_demand": 100.0,
        "based_on_events": 4,
    }


def test_confidence_interval_decorator_adds_ten_percent_margin():
    data = ConfidenceIntervalDecorator(_base(100.0)).generate()

    assert data["confidence_interval"] == [90.0, 110.0]
    assert data["predicted_demand"] == 100.0


def test_trend_decorator_reports_rise_with_three_or_more_events():
    assert TrendAnnotationDecorator(_base(based_on_events=3)).generate()["trend"] == "alza"


def test_trend_decorator_reports_insufficient_data_below_three_events():
    data = TrendAnnotationDecorator(_base(based_on_events=2)).generate()

    assert data["trend"] == "insuficientes datos"


def test_decorators_are_composable_and_keep_the_report_interface():
    report = TrendAnnotationDecorator(ConfidenceIntervalDecorator(_base()))

    assert isinstance(report, ForecastReport)
    data = report.generate()
    assert {"confidence_interval", "trend", "product_id"} <= data.keys()
