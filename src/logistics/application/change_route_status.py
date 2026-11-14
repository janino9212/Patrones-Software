from typing import Callable, Mapping

from src.logistics.domain.entities import DistributionRoute
from src.logistics.domain.repository import DistributionRouteRepository
from src.logistics.domain.route_state import InvalidRouteTransition

_ACTIONS: Mapping[str, Callable[[DistributionRoute], DistributionRoute]] = {
    "dispatch": DistributionRoute.dispatch,
    "deliver": DistributionRoute.deliver,
    "cancel": DistributionRoute.cancel,
}


class RouteNotFound(LookupError):
    """No existe una ruta con el identificador pedido."""


class ChangeRouteStatusUseCase:
    """Caso de uso: aplica una acción (despachar, entregar, cancelar) a una
    ruta. Qué acciones son válidas lo decide el estado actual (State)."""

    def __init__(self, repository: DistributionRouteRepository):
        self._repository = repository

    def execute(self, route_id: int, action: str) -> DistributionRoute:
        perform = _ACTIONS.get(action)
        if perform is None:
            raise ValueError(f"Acción de ruta no soportada: '{action}'")

        route = self._repository.get(route_id)
        if route is None:
            raise RouteNotFound(f"No existe la ruta #{route_id}")

        moved = perform(route)
        saved = self._repository.update_status(route_id, moved.status, route.status)
        if saved is None:
            raise InvalidRouteTransition(
                f"La ruta #{route_id} cambió de estado mientras se procesaba; vuelve a intentarlo"
            )
        return saved
