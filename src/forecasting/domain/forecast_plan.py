from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol


@dataclass(frozen=True)
class DemandRecord:
    """Demanda real observada de un producto en un período."""

    product_id: str
    period: date
    quantity: float


@dataclass(frozen=True)
class ForecastPlanMemento:
    """Memento (GoF): instantánea del estado de un ForecastPlan.

    Solo el propio ForecastPlan la crea y la interpreta; quien la guarda (el
    comando de recálculo, que actúa como caretaker) no usa su contenido."""

    _product_id: str
    _model: str
    _predicted_demand: float
    _based_on_records: int
    _generated_at: datetime


@dataclass(frozen=True)
class ForecastPlan:
    """Pronóstico vigente de un producto. Es el Originator del Memento."""

    product_id: str
    model: str
    predicted_demand: float
    based_on_records: int
    generated_at: datetime

    def create_memento(self) -> ForecastPlanMemento:
        return ForecastPlanMemento(
            self.product_id,
            self.model,
            self.predicted_demand,
            self.based_on_records,
            self.generated_at,
        )

    @classmethod
    def restore(cls, memento: ForecastPlanMemento) -> "ForecastPlan":
        return cls(
            product_id=memento._product_id,
            model=memento._model,
            predicted_demand=memento._predicted_demand,
            based_on_records=memento._based_on_records,
            generated_at=memento._generated_at,
        )


class DemandHistoryRepository(Protocol):
    """Puerto: historial de demanda real por producto."""

    def upsert(self, record: DemandRecord) -> DemandRecord: ...

    def list_by_product(self, product_id: str) -> list[DemandRecord]: ...


class ForecastPlanRepository(Protocol):
    """Puerto: pronóstico vigente por producto."""

    def get(self, product_id: str) -> ForecastPlan | None: ...

    def save(self, plan: ForecastPlan) -> ForecastPlan: ...

    def delete(self, product_id: str) -> None: ...
