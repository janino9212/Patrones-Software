from abc import ABC, abstractmethod
from src.tracking.domain.entities import TrackingEvent


class TrackingEventValidator(ABC):
    """Puerto: valida reglas de negocio del evento ya creado
    (distinto de la construcción, que resuelve el Factory Method)."""

    @abstractmethod
    def validate(self, event: TrackingEvent) -> None:
        """Lanza ValueError si el evento no cumple las reglas de negocio."""
        ...


class TrackingEventNotifier(ABC):
    """Puerto: construye el payload de notificación/auditoría del evento."""

    @abstractmethod
    def build_notification(self, event: TrackingEvent) -> dict:
        ...


class TrackingEventProcessingFactory(ABC):
    """Abstract Factory (GoF): crea la familia de componentes de
    procesamiento (validador + notificador) coherentes entre sí para un
    tipo de evento de tracking. No crea el TrackingEvent en sí -- eso
    sigue siendo responsabilidad del Factory Method (event_factory.py)."""

    @abstractmethod
    def create_validator(self) -> TrackingEventValidator:
        ...

    @abstractmethod
    def create_notifier(self) -> TrackingEventNotifier:
        ...