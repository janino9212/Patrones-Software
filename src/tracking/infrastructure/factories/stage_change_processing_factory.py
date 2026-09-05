from src.tracking.domain.entities import StageChangeTrackingEvent, TrackingEvent
from src.tracking.domain.processing_ports import (
    TrackingEventProcessingFactory, TrackingEventValidator, TrackingEventNotifier
)


class StageChangeValidator(TrackingEventValidator):
    def validate(self, event: TrackingEvent) -> None:
        assert isinstance(event, StageChangeTrackingEvent)
        if event.previous_stage == event.stage:
            raise ValueError("La etapa anterior no puede ser igual a la etapa nueva")


class StageChangeNotifier(TrackingEventNotifier):
    def build_notification(self, event: TrackingEvent) -> dict:
        assert isinstance(event, StageChangeTrackingEvent)
        return {
            "canal": "logistics-audit",
            "mensaje": f"Producto {event.product_id} avanzó de '{event.previous_stage}' a "
                       f"'{event.stage}', responsable: {event.responsible}",
        }


class StageChangeProcessingFactory(TrackingEventProcessingFactory):
    def create_validator(self) -> TrackingEventValidator:
        return StageChangeValidator()

    def create_notifier(self) -> TrackingEventNotifier:
        return StageChangeNotifier()