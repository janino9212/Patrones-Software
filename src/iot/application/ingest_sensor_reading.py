from dataclasses import dataclass

from src.iot.domain.notification_channel import NotificationChannel
from src.iot.domain.notification_dispatcher import build_dispatcher, resolve_channel_name
from src.iot.domain.sensor_adapter_port import SensorDataPort
from src.iot.infrastructure.channels import MqttChannel, WebhookChannel
from src.iot.infrastructure.sensor_adapters import get_vendor_adapter
from src.tracking.application.register_event import RegisterTrackingEventUseCase
from src.tracking.domain.entities import TrackingEvent

_CHANNELS: dict[str, NotificationChannel] = {
    "mqtt": MqttChannel(),
    "webhook": WebhookChannel(),
}


@dataclass(frozen=True)
class IngestResult:
    event: TrackingEvent
    notified_via: str
    message: str


class IngestSensorReadingUseCase:
    """1) Adapter normaliza el payload del fabricante.
    2) Factory Method + Abstract Factory (en tracking) crean, validan y
       construyen la notificación.
    3) Bridge decide canal + urgencia y despacha."""

    def __init__(self, register_use_case: RegisterTrackingEventUseCase):
        self._register_use_case = register_use_case

    def execute(self, vendor: str, product_id: str, stage: str) -> IngestResult:
        adapter: SensorDataPort = get_vendor_adapter(vendor)
        reading = adapter.read()

        raw_data = {
            "product_id": product_id,
            "stage": stage,
            "sensor_type": reading.sensor_type,
            "reading_value": reading.value,
            "unit": reading.unit,
        }
        event, notification = self._register_use_case.execute_with_notification("sensor", raw_data)

        channel_name = resolve_channel_name(notification["canal"])
        channel = _CHANNELS[channel_name]
        dispatcher = build_dispatcher(notification["canal"], channel)
        dispatcher.dispatch(notification["mensaje"])

        return IngestResult(event=event, notified_via=channel_name, message=notification["mensaje"])