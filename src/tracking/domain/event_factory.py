from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

from src.tracking.domain.entities import (
    SensorTrackingEvent,
    StageChangeTrackingEvent,
    TrackingEvent,
)


class UnsupportedEventTypeError(ValueError):
    """Se pidió crear un evento de un tipo que no tiene Creator registrado."""


class TrackingEventCreator(ABC):
    """Creator del patrón Factory Method (GoF).

    Cada subclase decide qué subtipo concreto de TrackingEvent instanciar a
    partir de los datos crudos de tracking (por tipo de sensor o de etapa),
    sin que el código que la invoca (el caso de uso) conozca esas clases
    concretas.
    """

    @abstractmethod
    def create_event(self, raw_data: dict[str, Any]) -> TrackingEvent:
        ...


class SensorEventCreator(TrackingEventCreator):
    """Crea eventos a partir de la lectura de un sensor IoT."""

    def create_event(self, raw_data: dict[str, Any]) -> SensorTrackingEvent:
        return SensorTrackingEvent(
            product_id=raw_data["product_id"],
            stage=raw_data["stage"],
            timestamp=datetime.now(timezone.utc),
            sensor_type=raw_data["sensor_type"],
            reading_value=raw_data["reading_value"],
            unit=raw_data["unit"],
        )


class StageChangeEventCreator(TrackingEventCreator):
    """Crea eventos cuando un producto avanza de una etapa a otra."""

    def create_event(self, raw_data: dict[str, Any]) -> StageChangeTrackingEvent:
        return StageChangeTrackingEvent(
            product_id=raw_data["product_id"],
            stage=raw_data["stage"],
            timestamp=datetime.now(timezone.utc),
            previous_stage=raw_data["previous_stage"],
            responsible=raw_data["responsible"],
        )


# Registro de creators disponibles por tipo de evento. Es un diccionario
# inmutable de instancias sin estado -- deliberadamente NO es un Singleton:
# ese patrón ya está reservado en este proyecto para DatabaseConnection y
# JWTManager (src/shared). Mezclarlo aquí confundiría cuál patrón se está
# demostrando en cada módulo.
_CREATORS: dict[str, TrackingEventCreator] = {
    "sensor": SensorEventCreator(),
    "stage_change": StageChangeEventCreator(),
}


def get_creator(event_type: str) -> TrackingEventCreator:
    try:
        return _CREATORS[event_type]
    except KeyError as exc:
        raise UnsupportedEventTypeError(
            f"Tipo de evento de tracking no soportado: '{event_type}'"
        ) from exc
