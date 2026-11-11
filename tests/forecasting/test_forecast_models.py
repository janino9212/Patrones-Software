import pytest

from src.forecasting.domain.forecast_models import (
    DemandForecastModel,
    ExponentialSmoothingModel,
    InsufficientDemandData,
    LinearTrendModel,
    MovingAverageModel,
    available_models,
    get_model,
)


class _SpyModel(DemandForecastModel):
    """Registra el orden en que el método plantilla invoca cada paso."""

    name = "spy"
    label = "Espía"
    min_points = 2

    def __init__(self, estimate: float = 10.0):
        self.calls: list[str] = []
        self._value = estimate

    def _prepare(self, series):
        self.calls.append("prepare")
        return super()._prepare(series)

    def _check_enough_data(self, series):
        self.calls.append("check")
        super()._check_enough_data(series)

    def _estimate(self, series):
        self.calls.append("estimate")
        return self._value

    def _finalize(self, estimate):
        self.calls.append("finalize")
        return super()._finalize(estimate)


def test_template_method_runs_the_steps_in_a_fixed_order():
    model = _SpyModel()

    model.forecast([1, 2, 3])

    assert model.calls == ["prepare", "check", "estimate", "finalize"]


def test_template_method_stops_before_estimating_when_data_is_insufficient():
    model = _SpyModel()

    with pytest.raises(InsufficientDemandData, match="al menos 2"):
        model.forecast([5])

    assert model.calls == ["prepare", "check"]


def test_finalize_step_clamps_negative_estimates_and_rounds():
    assert _SpyModel(estimate=-4.0).forecast([1, 2]) == 0.0
    assert _SpyModel(estimate=3.14159).forecast([1, 2]) == 3.14


def test_moving_average_uses_the_last_three_periods():
    assert MovingAverageModel().forecast([100, 10, 20, 30]) == 20.0
    assert MovingAverageModel().forecast([8]) == 8.0


def test_exponential_smoothing_weights_recent_periods_more():
    # nivel: 10 -> 0.5*20+0.5*10=15 -> 0.5*40+0.5*15=27.5
    assert ExponentialSmoothingModel().forecast([10, 20, 40]) == 27.5


def test_linear_trend_extrapolates_a_perfect_line():
    assert LinearTrendModel().forecast([10, 20, 30]) == 40.0
    assert LinearTrendModel().forecast([30, 20, 10]) == 0.0


def test_linear_trend_needs_two_periods():
    with pytest.raises(InsufficientDemandData):
        LinearTrendModel().forecast([10])


@pytest.mark.parametrize("model", available_models())
def test_every_model_rejects_an_empty_history(model):
    with pytest.raises(InsufficientDemandData):
        model.forecast([])


def test_get_model_rejects_unknown_name():
    with pytest.raises(ValueError, match="no soportado"):
        get_model("red_neuronal")
