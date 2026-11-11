import dataclasses
from dataclasses import dataclass
from datetime import date

from src.logistics.domain.route_state import INITIAL_STATUS, RouteState, state_for
from src.logistics.domain.vehicle_type import VehicleType, VehicleTypeFactory


@dataclass(frozen=True)
class RouteStop:
    """Una parada dentro de una ruta de distribución."""

    sequence: int
    location: str
    notes: str | None = None


@dataclass(frozen=True)
class DistributionRoute:
    """Producto del Builder: una ruta de distribución completa."""

    vehicle_type: str
    departure_date: date
    stops: tuple[RouteStop, ...]
    total_distance_km: float | None = None
    notes: str | None = None
    route_id: int | None = None
    status: str = INITIAL_STATUS

    @property
    def vehicle(self) -> VehicleType:
        """Flyweight compartido del tipo de vehículo de esta ruta."""
        return VehicleTypeFactory.get(self.vehicle_type)

    @property
    def state(self) -> RouteState:
        """Objeto State que decide qué acciones admite la ruta ahora."""
        return state_for(self.status)

    # La ruta (Context) delega cada acción en su estado actual y devuelve una
    # ruta nueva con el estado resultante; la original no cambia.
    def dispatch(self) -> "DistributionRoute":
        return self._moved_to(self.state.dispatch())

    def deliver(self) -> "DistributionRoute":
        return self._moved_to(self.state.deliver())

    def cancel(self) -> "DistributionRoute":
        return self._moved_to(self.state.cancel())

    def _moved_to(self, new_state: RouteState) -> "DistributionRoute":
        return dataclasses.replace(self, status=new_state.status)
