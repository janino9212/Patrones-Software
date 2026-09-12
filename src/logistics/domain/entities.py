from dataclasses import dataclass
from datetime import date


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
