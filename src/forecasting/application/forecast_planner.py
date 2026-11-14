from datetime import datetime, timezone
from typing import Callable

from src.forecasting.domain.forecast_models import get_model
from src.forecasting.domain.forecast_plan import (
    DemandHistoryRepository,
    ForecastPlan,
    ForecastPlanRepository,
)

Clock = Callable[[], datetime]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ForecastPlanner:
    """Receiver del patrón Command: sabe calcular, guardar y descartar el
    pronóstico de un producto. Los comandos le dicen QUÉ hacer; el CÓMO vive
    aquí."""

    def __init__(
        self,
        history_repository: DemandHistoryRepository,
        plan_repository: ForecastPlanRepository,
        clock: Clock = _utc_now,
    ):
        self._history_repository = history_repository
        self._plan_repository = plan_repository
        self._clock = clock

    def current(self, product_id: str) -> ForecastPlan | None:
        return self._plan_repository.get(product_id)

    def compute(self, product_id: str, model_name: str) -> ForecastPlan:
        """Calcula un pronóstico con el historial actual, sin guardarlo."""
        model = get_model(model_name)
        history = self._history_repository.list_by_product(product_id)
        predicted = model.forecast([record.quantity for record in history])
        return ForecastPlan(
            product_id=product_id,
            model=model.name,
            predicted_demand=predicted,
            based_on_records=len(history),
            generated_at=self._clock(),
        )

    def store(self, plan: ForecastPlan) -> ForecastPlan:
        return self._plan_repository.save(plan)

    def discard(self, product_id: str) -> None:
        self._plan_repository.delete(product_id)
