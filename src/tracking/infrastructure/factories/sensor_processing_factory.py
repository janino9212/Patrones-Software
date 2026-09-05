from src.tracking.domain.entities import SensorTrackingEvent, TrackingEvent
from src.tracking.domain.processing_ports import (
    TrackingEventProcessingFactory, TrackingEventValidator, TrackingEventNotifier
)


class SensorEventValidator(TrackingEventValidator):
    def validate(self, event: TrackingEvent) -> None:
        assert isinstance(event, SensorTrackingEvent)
        if event.reading_value < 0 and event.unit == "°C" and event.reading_value < -50:
            raise ValueError("Lectura de temperatura fuera de rango físico plausible")


class SensorEventNotifier(TrackingEventNotifier):
    def build_notification(self, event: TrackingEvent) -> dict:
        assert isinstance(event, SensorTrackingEvent)
        return {
            "canal": "iot-monitor",
            "mensaje": f"Sensor {event.sensor_type} reportó {event.reading_value}{event.unit} "
                       f"para el producto {event.product_id}",
        }


class SensorProcessingFactory(TrackingEventProcessingFactory):
    def create_validator(self) -> TrackingEventValidator:
        return SensorEventValidator()

    def create_notifier(self) -> TrackingEventNotifier:
        return SensorEventNotifier()