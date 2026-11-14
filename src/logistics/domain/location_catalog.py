import math
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Sequence

_EARTH_RADIUS_KM = 6371.0


@dataclass(frozen=True)
class Location:
    """Punto de la red de distribución con coordenadas conocidas."""

    name: str
    latitude: float
    longitude: float


_LOCATIONS: tuple[Location, ...] = (
    Location("Bucaramanga", 7.1193, -73.1227),
    Location("Floridablanca", 7.0622, -73.0864),
    Location("Girón", 7.0682, -73.1698),
    Location("Piedecuesta", 6.9877, -73.0495),
    Location("Barrancabermeja", 7.0653, -73.8547),
    Location("San Gil", 6.5552, -73.1336),
    Location("Cúcuta", 7.8939, -72.5078),
    Location("Tunja", 5.5353, -73.3678),
    Location("Bogotá", 4.7110, -74.0721),
    Location("Medellín", 6.2442, -75.5812),
    Location("Barranquilla", 10.9685, -74.7813),
    Location("Cartagena", 10.3910, -75.4794),
)

_BY_KEY: Mapping[str, Location] = MappingProxyType(
    {location.name.casefold(): location for location in _LOCATIONS}
)


def all_locations() -> tuple[Location, ...]:
    return _LOCATIONS


def find_location(name: str) -> Location | None:
    """Busca una ubicación del catálogo sin distinguir mayúsculas."""
    return _BY_KEY.get(name.strip().casefold())


def distance_km(origin: Location, destination: Location) -> float:
    """Distancia en línea recta sobre la esfera (fórmula de haversine).
    Es una aproximación: no sigue la red vial."""
    lat1, lat2 = math.radians(origin.latitude), math.radians(destination.latitude)
    delta_lat = lat2 - lat1
    delta_lon = math.radians(destination.longitude - origin.longitude)
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    return 2 * _EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def path_length_km(stops: Sequence[Location]) -> float:
    """Suma de los tramos consecutivos de un recorrido."""
    return sum(distance_km(a, b) for a, b in zip(stops, stops[1:]))
