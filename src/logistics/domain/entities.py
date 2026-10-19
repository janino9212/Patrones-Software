from dataclasses import dataclass
from datetime import date

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

    @property
    def vehicle(self) -> VehicleType:
        """Flyweight compartido del tipo de vehículo de esta ruta."""
        return VehicleTypeFactory.get(self.vehicle_type)
