from typing import Protocol

from src.logistics.domain.entities import DistributionRoute


class DistributionRouteRepository(Protocol):
    """Puerto (hexagonal): lo que la capa de aplicación necesita para
    persistir/consultar rutas, sin saber cómo se implementa."""

    def save(self, route: DistributionRoute) -> DistributionRoute: ...

    def get(self, route_id: int) -> DistributionRoute | None: ...

    def list_all(self) -> list[DistributionRoute]: ...

    def update_status(
        self, route_id: int, new_status: str, expected_status: str
    ) -> DistributionRoute | None:
        """Cambia el estado solo si la ruta sigue en `expected_status`.
        Devuelve None si otra operación la cambió antes."""
        ...
