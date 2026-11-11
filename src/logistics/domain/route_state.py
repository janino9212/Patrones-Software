from abc import ABC
from types import MappingProxyType
from typing import Mapping


class InvalidRouteTransition(ValueError):
    """Se pidió una acción que el estado actual de la ruta no permite."""


class RouteState(ABC):
    """State (GoF): el comportamiento de una ruta ante despachar, entregar o
    cancelar depende de su estado. Cada estado concreto sobreescribe solo
    las transiciones que permite; las demás quedan rechazadas aquí."""

    status: str
    label: str
    allowed_actions: tuple[str, ...] = ()

    def dispatch(self) -> "RouteState":
        raise self._rejected("despachar")

    def deliver(self) -> "RouteState":
        raise self._rejected("entregar")

    def cancel(self) -> "RouteState":
        raise self._rejected("cancelar")

    def _rejected(self, action: str) -> InvalidRouteTransition:
        return InvalidRouteTransition(f"No se puede {action} una ruta en estado '{self.label}'")


class PlannedState(RouteState):
    status = "planned"
    label = "planificada"
    allowed_actions = ("dispatch", "cancel")

    def dispatch(self) -> RouteState:
        return InTransitState()

    def cancel(self) -> RouteState:
        return CancelledState()


class InTransitState(RouteState):
    status = "in_transit"
    label = "en tránsito"
    allowed_actions = ("deliver", "cancel")

    def deliver(self) -> RouteState:
        return DeliveredState()

    def cancel(self) -> RouteState:
        return CancelledState()


class DeliveredState(RouteState):
    status = "delivered"
    label = "entregada"


class CancelledState(RouteState):
    status = "cancelled"
    label = "cancelada"


_STATES: Mapping[str, RouteState] = MappingProxyType(
    {
        state.status: state
        for state in (PlannedState(), InTransitState(), DeliveredState(), CancelledState())
    }
)
ROUTE_ACTIONS: tuple[str, ...] = ("dispatch", "deliver", "cancel")
INITIAL_STATUS = PlannedState.status


def state_for(status: str) -> RouteState:
    state = _STATES.get(status)
    if state is None:
        raise ValueError(f"Estado de ruta desconocido: '{status}'")
    return state


