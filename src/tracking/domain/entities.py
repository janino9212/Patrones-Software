from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TrackingEvent:
    """Producto base del Factory Method: un evento de seguimiento de un
    producto en algún punto de la cadena de suministro."""

    product_id: str
    stage: str
    timestamp: datetime


@dataclass(frozen=True)
class SensorTrackingEvent(TrackingEvent):
    """Evento generado por la lectura de un sensor IoT (temperatura, GPS, etc.)."""

    sensor_type: str
    reading_value: float
    unit: str


@dataclass(frozen=True)
class StageChangeTrackingEvent(TrackingEvent):
    """Evento generado cuando un producto pasa de una etapa a otra
    (ej. fabricación -> transporte -> entrega)."""

    previous_stage: str
    responsible: str


def event_type_of(event: TrackingEvent) -> str:
    """Discriminador usado por infraestructura e interfaces para saber qué
    subtipo concreto de TrackingEvent se está manejando."""
    if isinstance(event, SensorTrackingEvent):
        return "sensor"
    if isinstance(event, StageChangeTrackingEvent):
        return "stage_change"
    raise TypeError(f"Tipo de TrackingEvent desconocido: {type(event)!r}")
