import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone

from src.forecasting.application.forecast_planner import ForecastPlanner
from src.forecasting.domain.forecast_models import DEFAULT_MODEL_NAME
from src.forecasting.domain.forecast_plan import ForecastPlan, ForecastPlanMemento

_MAX_HISTORY = 100


class ForecastPlanConflict(ValueError):
    """La operación no aplica al estado actual del pronóstico del producto."""


class ForecastCommand(ABC):
    """Command (GoF): una operación sobre el pronóstico de un producto,
    encapsulada como objeto para poder registrarla y deshacerla.

    El receiver (ForecastPlanner) se recibe en cada llamada y no en el
    constructor, porque está ligado a la sesión de BD de una petición y el
    comando sobrevive a ella dentro del historial del invoker."""

    name: str

    def __init__(self, product_id: str):
        self.product_id = product_id

    @abstractmethod
    def execute(self, planner: ForecastPlanner) -> ForecastPlan:
        ...

    @abstractmethod
    def undo(self, planner: ForecastPlanner) -> ForecastPlan | None:
        """Revierte el efecto de execute; devuelve el pronóstico que queda."""


class GenerateForecastCommand(ForecastCommand):
    """Crea el primer pronóstico de un producto."""

    name = "generate"

    def __init__(self, product_id: str, model_name: str | None = None):
        super().__init__(product_id)
        self._model_name = model_name or DEFAULT_MODEL_NAME

    def execute(self, planner: ForecastPlanner) -> ForecastPlan:
        if planner.current(self.product_id) is not None:
            raise ForecastPlanConflict(
                f"El producto {self.product_id} ya tiene un pronóstico; use 'recalcular'"
            )
        return planner.store(planner.compute(self.product_id, self._model_name))

    def undo(self, planner: ForecastPlanner) -> ForecastPlan | None:
        planner.discard(self.product_id)
        return None


class RecalculateForecastCommand(ForecastCommand):
    """Vuelve a calcular el pronóstico con el historial actual y,
    opcionalmente, con otro modelo. Guarda un Memento del pronóstico
    anterior para poder restaurarlo."""

    name = "recalculate"

    def __init__(self, product_id: str, model_name: str | None = None):
        super().__init__(product_id)
        self._model_name = model_name
        self._previous: ForecastPlanMemento | None = None

    def execute(self, planner: ForecastPlanner) -> ForecastPlan:
        current = planner.current(self.product_id)
        if current is None:
            raise ForecastPlanConflict(
                f"El producto {self.product_id} aún no tiene pronóstico; use 'generar'"
            )
        recalculated = planner.compute(self.product_id, self._model_name or current.model)
        self._previous = current.create_memento()
        return planner.store(recalculated)

    def undo(self, planner: ForecastPlanner) -> ForecastPlan | None:
        if self._previous is None:
            raise ForecastPlanConflict("El recálculo no llegó a ejecutarse")
        return planner.store(ForecastPlan.restore(self._previous))


@dataclass(frozen=True)
class CommandLogEntry:
    command: str
    product_id: str
    executed_at: datetime
    undone: bool = False


class ForecastCommandInvoker:
    """Invoker: ejecuta los comandos, lleva la bitácora y conserva los que
    todavía se pueden deshacer.

    El historial vive en memoria del proceso: se pierde al reiniciar la API
    (los pronósticos sí quedan en la base de datos)."""

    def __init__(self) -> None:
        # Reentrante: run y undo_last lo retienen mientras ejecutan el comando
        # y registran el resultado, y _record lo vuelve a tomar.
        self._lock = threading.RLock()
        self._undoable: list[ForecastCommand] = []
        self._log: list[CommandLogEntry] = []

    def run(self, command: ForecastCommand, planner: ForecastPlanner) -> ForecastPlan:
        """Ejecuta el comando y lo registra como una sola operación atómica:
        dos peticiones simultáneas no pueden pasar a la vez la comprobación
        "¿ya hay pronóstico?" ni desordenar el historial."""
        with self._lock:
            plan = command.execute(planner)
            self._undoable = [*self._undoable, command][-_MAX_HISTORY:]
            self._record(command, undone=False)
            return plan

    def undo_last(self, product_id: str, planner: ForecastPlanner) -> ForecastPlan | None:
        """Deshace el comando más reciente del producto. El comando solo sale
        del historial si su undo terminó bien, para poder reintentarlo."""
        with self._lock:
            command = next(
                (cmd for cmd in reversed(self._undoable) if cmd.product_id == product_id), None
            )
            if command is None:
                raise ForecastPlanConflict(
                    f"No hay operaciones por deshacer para el producto {product_id}"
                )
            plan = command.undo(planner)
            self._undoable = [cmd for cmd in self._undoable if cmd is not command]
            self._record(command, undone=True)
            return plan

    def can_undo(self, product_id: str) -> bool:
        with self._lock:
            return any(cmd.product_id == product_id for cmd in self._undoable)

    def log(self) -> tuple[CommandLogEntry, ...]:
        """Bitácora, de la operación más reciente a la más antigua."""
        with self._lock:
            return tuple(reversed(self._log))

    def _record(self, command: ForecastCommand, undone: bool) -> None:
        entry = CommandLogEntry(
            command=command.name,
            product_id=command.product_id,
            executed_at=datetime.now(timezone.utc),
            undone=undone,
        )
        self._log = [*self._log, entry][-_MAX_HISTORY:]


_invoker = ForecastCommandInvoker()


def get_command_invoker() -> ForecastCommandInvoker:
    """Dependencia de FastAPI: el invoker compartido por todas las peticiones."""
    return _invoker
