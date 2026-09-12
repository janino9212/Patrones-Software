from abc import ABC, abstractmethod
from datetime import date

from src.logistics.domain.entities import DistributionRoute, RouteStop


class RouteBuilder(ABC):
    """Builder (GoF): construye una DistributionRoute paso a paso, ocultando
    el orden de ensamblaje y las validaciones de las partes obligatorias
    (vehículo, fecha, mínimo de paradas) y opcionales (distancia, notas)."""

    @abstractmethod
    def set_vehicle(self, vehicle_type: str) -> "RouteBuilder":
        ...

    @abstractmethod
    def set_departure_date(self, departure_date: date) -> "RouteBuilder":
        ...

    @abstractmethod
    def add_stop(self, location: str, notes: str | None = None) -> "RouteBuilder":
        ...

    @abstractmethod
    def set_total_distance_km(self, total_distance_km: float) -> "RouteBuilder":
        ...

    @abstractmethod
    def set_notes(self, notes: str) -> "RouteBuilder":
        ...

    @abstractmethod
    def build(self) -> DistributionRoute:
        ...


class DistributionRouteBuilder(RouteBuilder):
    """Builder concreto: acumula las partes de la ruta y valida las
    invariantes mínimas antes de entregar el producto final (inmutable)."""

    def __init__(self) -> None:
        self._vehicle_type: str | None = None
        self._departure_date: date | None = None
        self._stops: list[RouteStop] = []
        self._total_distance_km: float | None = None
        self._notes: str | None = None

    def set_vehicle(self, vehicle_type: str) -> "DistributionRouteBuilder":
        self._vehicle_type = vehicle_type
        return self

    def set_departure_date(self, departure_date: date) -> "DistributionRouteBuilder":
        self._departure_date = departure_date
        return self

    def add_stop(self, location: str, notes: str | None = None) -> "DistributionRouteBuilder":
        sequence = len(self._stops) + 1
        self._stops.append(RouteStop(sequence=sequence, location=location, notes=notes))
        return self

    def set_total_distance_km(self, total_distance_km: float) -> "DistributionRouteBuilder":
        self._total_distance_km = total_distance_km
        return self

    def set_notes(self, notes: str) -> "DistributionRouteBuilder":
        self._notes = notes
        return self

    def build(self) -> DistributionRoute:
        if self._vehicle_type is None:
            raise ValueError("La ruta necesita un tipo de vehículo (set_vehicle)")
        if self._departure_date is None:
            raise ValueError("La ruta necesita una fecha de salida (set_departure_date)")
        if len(self._stops) < 2:
            raise ValueError("Una ruta de distribución necesita al menos 2 paradas")

        return DistributionRoute(
            vehicle_type=self._vehicle_type,
            departure_date=self._departure_date,
            stops=tuple(self._stops),
            total_distance_km=self._total_distance_km,
            notes=self._notes,
        )
