from dataclasses import dataclass
from datetime import datetime, timezone

from src.iot.domain.notification_channel import NotificationChannel
from src.iot.domain.notification_dispatcher import build_dispatcher, resolve_channel_name
from src.iot.domain.sensor_adapter_port import SensorDataPort
from src.iot.domain.sensor_observer import SensorObservation, SensorReadingSubject
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
    device_id: str


class IngestSensorReadingUseCase:
    """1) Adapter normaliza el payload del fabricante.
    2) Chain of Responsibility + Factory Method + Abstract Factory (en
       tracking) validan, crean y construyen la notificación.
    3) Bridge decide canal + urgencia y despacha.
    4) Observer publica la lectura aceptada a quienes estén suscritos
       (panel en vivo, alertas por umbral, estado de dispositivos)."""

    def __init__(
        self,
        register_use_case: RegisterTrackingEventUseCase,
        subject: SensorReadingSubject | None = None,
    ):
        self._register_use_case = register_use_case
        self._subject = subject

    def execute(
        self, vendor: str, product_id: str, stage: str, simulated_value: float | None = None
    ) -> IngestResult:
        adapter: SensorDataPort = get_vendor_adapter(vendor, simulated_value)
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

        if self._subject is not None:
            self._subject.notify(
                SensorObservation(
                    reading=reading,
                    product_id=product_id,
                    stage=stage,
                    received_at=datetime.now(timezone.utc),
                )
            )

        return IngestResult(
            event=event,
            notified_via=channel_name,
            message=notification["mensaje"],
            device_id=reading.device_id,
        )
