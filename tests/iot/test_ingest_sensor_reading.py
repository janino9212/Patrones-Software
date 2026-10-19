import pytest

from src.iot.application import ingest_sensor_reading
from src.iot.application.ingest_sensor_reading import IngestSensorReadingUseCase
from src.iot.domain.notification_channel import NotificationChannel
from src.tracking.application.register_event import RegisterTrackingEventUseCase


class _FakeTrackingEventRepository:
    def __init__(self):
        self.saved = []

    def save(self, event):
        self.saved.append(event)
        return event

    def list_by_product(self, product_id):
        return [e for e in self.saved if e.product_id == product_id]


class _SpyChannel(NotificationChannel):
    def __init__(self):
        self.sent: list[str] = []

    def send(self, message: str) -> None:
        self.sent.append(message)


@pytest.fixture
def spy_channels(monkeypatch):
    channels = {"mqtt": _SpyChannel(), "webhook": _SpyChannel()}
    monkeypatch.setattr(ingest_sensor_reading, "_CHANNELS", channels)
    return channels


def _use_case():
    repository = _FakeTrackingEventRepository()
    return IngestSensorReadingUseCase(RegisterTrackingEventUseCase(repository)), repository


def test_execute_saves_event_and_notifies_via_mqtt_urgent(spy_channels):
    use_case, repository = _use_case()

    result = use_case.execute("a", "PROD-1", "transporte")

    assert result.notified_via == "mqtt"
    assert result.event.sensor_type == "temperatura"
    assert result.event.reading_value == 23.8
    assert repository.saved == [result.event]
    assert len(spy_channels["mqtt"].sent) == 1
    assert spy_channels["mqtt"].sent[0].startswith("URGENTE: ")
    assert spy_channels["webhook"].sent == []


def test_execute_with_out_of_range_reading_raises_and_does_not_save_or_notify(spy_channels):
    use_case, repository = _use_case()

    with pytest.raises(ValueError):
        use_case.execute("a-faulty", "PROD-1", "transporte")

    assert repository.saved == []
    assert spy_channels["mqtt"].sent == []
    assert spy_channels["webhook"].sent == []


def test_execute_with_unknown_vendor_raises_value_error(spy_channels):
    use_case, repository = _use_case()

    with pytest.raises(ValueError, match="no soportado"):
        use_case.execute("fabricante-x", "PROD-1", "transporte")

    assert repository.saved == []
