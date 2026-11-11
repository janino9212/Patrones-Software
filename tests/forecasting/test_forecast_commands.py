from datetime import date, datetime, timezone

import pytest

from src.forecasting.application.forecast_commands import (
    ForecastCommandInvoker,
    ForecastPlanConflict,
    GenerateForecastCommand,
    RecalculateForecastCommand,
)
from src.forecasting.application.forecast_planner import ForecastPlanner
from src.forecasting.domain.forecast_models import InsufficientDemandData
from src.forecasting.domain.forecast_plan import DemandRecord, ForecastPlan

_FIXED_NOW = datetime(2026, 11, 1, tzinfo=timezone.utc)


class _FakeHistory:
    def __init__(self, quantities: list[float]):
        self.quantities = quantities

    def upsert(self, record):
        raise AssertionError("los comandos no escriben historial")

    def list_by_product(self, product_id):
        return [
            DemandRecord(product_id, date(2026, month + 1, 1), quantity)
            for month, quantity in enumerate(self.quantities)
        ]


class _FakePlans:
    def __init__(self):
        self.plans: dict[str, ForecastPlan] = {}

    def get(self, product_id):
        return self.plans.get(product_id)

    def save(self, plan):
        self.plans[plan.product_id] = plan
        return plan

    def delete(self, product_id):
        self.plans.pop(product_id, None)


@pytest.fixture
def history():
    return _FakeHistory([10, 20, 30])


@pytest.fixture
def plans():
    return _FakePlans()


@pytest.fixture
def planner(history, plans):
    return ForecastPlanner(history, plans, clock=lambda: _FIXED_NOW)


def test_memento_restores_an_identical_plan():
    plan = ForecastPlan("P-1", "moving_average", 20.0, 3, _FIXED_NOW)

    assert ForecastPlan.restore(plan.create_memento()) == plan


def test_generate_stores_a_plan_with_the_default_model(planner, plans):
    plan = GenerateForecastCommand("P-1").execute(planner)

    assert plan == ForecastPlan("P-1", "moving_average", 20.0, 3, _FIXED_NOW)
    assert plans.plans["P-1"] == plan


def test_generate_twice_is_a_conflict(planner):
    GenerateForecastCommand("P-1").execute(planner)

    with pytest.raises(ForecastPlanConflict, match="recalcular"):
        GenerateForecastCommand("P-1").execute(planner)


def test_generate_without_history_fails_and_stores_nothing(plans):
    planner = ForecastPlanner(_FakeHistory([]), plans)

    with pytest.raises(InsufficientDemandData):
        GenerateForecastCommand("P-1").execute(planner)

    assert plans.plans == {}


def test_undo_generate_discards_the_plan(planner, plans):
    command = GenerateForecastCommand("P-1")
    command.execute(planner)

    assert command.undo(planner) is None
    assert plans.plans == {}


def test_recalculate_requires_an_existing_plan(planner):
    with pytest.raises(ForecastPlanConflict, match="generar"):
        RecalculateForecastCommand("P-1").execute(planner)


def test_recalculate_uses_new_history_and_keeps_the_model_by_default(planner, history):
    GenerateForecastCommand("P-1", "linear_trend").execute(planner)
    history.quantities = [10, 20, 30, 40]

    plan = RecalculateForecastCommand("P-1").execute(planner)

    assert plan.model == "linear_trend"
    assert plan.predicted_demand == 50.0
    assert plan.based_on_records == 4


def test_recalculate_can_switch_model(planner):
    GenerateForecastCommand("P-1").execute(planner)

    plan = RecalculateForecastCommand("P-1", "linear_trend").execute(planner)

    assert (plan.model, plan.predicted_demand) == ("linear_trend", 40.0)


def test_undo_recalculate_restores_the_previous_plan_from_its_memento(planner, plans):
    original = GenerateForecastCommand("P-1").execute(planner)
    command = RecalculateForecastCommand("P-1", "linear_trend")
    command.execute(planner)

    restored = command.undo(planner)

    assert restored == original
    assert plans.plans["P-1"] == original


def test_failed_recalculate_leaves_the_plan_untouched(planner, plans, history):
    original = GenerateForecastCommand("P-1").execute(planner)
    history.quantities = [10]

    with pytest.raises(InsufficientDemandData):
        RecalculateForecastCommand("P-1", "linear_trend").execute(planner)

    assert plans.plans["P-1"] == original


def test_undo_of_a_recalculate_that_never_ran_is_rejected(planner):
    with pytest.raises(ForecastPlanConflict):
        RecalculateForecastCommand("P-1").undo(planner)


def test_invoker_undoes_commands_of_a_product_in_reverse_order(planner, plans):
    invoker = ForecastCommandInvoker()
    first = invoker.run(GenerateForecastCommand("P-1"), planner)
    invoker.run(RecalculateForecastCommand("P-1", "linear_trend"), planner)
    invoker.run(GenerateForecastCommand("P-2"), planner)

    assert invoker.undo_last("P-1", planner) == first
    assert invoker.undo_last("P-1", planner) is None
    assert "P-1" not in plans.plans
    assert "P-2" in plans.plans
    assert not invoker.can_undo("P-1")
    assert invoker.can_undo("P-2")


def test_invoker_does_not_register_a_command_that_failed(planner):
    invoker = ForecastCommandInvoker()

    with pytest.raises(ForecastPlanConflict):
        invoker.run(RecalculateForecastCommand("P-1"), planner)

    assert invoker.log() == ()
    assert not invoker.can_undo("P-1")


def test_invoker_undo_without_history_is_a_conflict(planner):
    with pytest.raises(ForecastPlanConflict, match="deshacer"):
        ForecastCommandInvoker().undo_last("P-1", planner)


def test_invoker_log_lists_newest_first_and_marks_undone_operations(planner):
    invoker = ForecastCommandInvoker()
    invoker.run(GenerateForecastCommand("P-1"), planner)
    invoker.undo_last("P-1", planner)

    log = invoker.log()

    assert [(entry.command, entry.undone) for entry in log] == [
        ("generate", True),
        ("generate", False),
    ]
