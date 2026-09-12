from typing import Any

from src.tracking.domain.entities import TrackingEvent
from src.tracking.domain.event_factory import get_creator
from src.tracking.domain.repository import TrackingEventRepository
from src.tracking.application.processing_factory_registry import TrackingProcessingFactoryRegistry


class RegisterTrackingEventUseCase:
    """Caso de uso: resuelve el Creator adecuado (Factory Method) según el
    tipo de evento recibido, construye el TrackingEvent y lo persiste
    a través del puerto de repositorio (independiente de la BD concreta)."""

    def __init__(self, repository: TrackingEventRepository):
        self._repository = repository

    def execute(self, event_type: str, raw_data: dict[str, Any]) -> TrackingEvent:
        creator = get_creator(event_type)
        event = creator.create_event(raw_data)

        processing_factory = TrackingProcessingFactoryRegistry.get_factory(event_type)
        validator = processing_factory.create_validator()
        notifier = processing_factory.create_notifier()

        validator.validate(event)
        notification = notifier.build_notification(event)
        print(f"[ABSTRACT FACTORY] Notificación generada: {notification}")
        return self._repository.save(event)
