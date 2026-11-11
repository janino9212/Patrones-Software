from datetime import datetime, timezone

from src.iot.application.monitoring import (
    DeviceRegistryObserver,
    LiveFeedObserver,
    SensorMonitor,
    ThresholdAlertObserver,
)
from src.iot.domain.sensor_observer import SensorObservation, SensorObserver, SensorReadingSubject
from src.iot.domain.sensor_reading import SensorReading
from src.iot.infrastructure.sensor_adapters import VendorBHumidityAdapter, get_vendor_adapter
from src.iot.infrastructure.vendor_clients import VendorBHumidityClient

_NOW = datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc)


def _observation(
    value: float = 20.0, sensor_type: str = "temperatura", device_id: str = "TEMP-01"
) -> SensorObservation:
    unit = "°C" if sensor_type == "temperatura" else "%"
    return SensorObservation(
        reading=SensorReading(device_id, sensor_type, value, unit),
        product_id="PROD-1",
        stage="transporte",
        received_at=_NOW,
    )


class _SpyObserver(SensorObserver):
    def __init__(self):
        self.received: list[SensorObservation] = []

    def update(self, observation):
        self.received.append(observation)


class _BrokenObserver(SensorObserver):
    def update(self, observation):
        raise RuntimeError("observador averiado")


def test_subject_notifies_every_attached_observer():
    subject = SensorReadingSubject()
    first, second = _SpyObserver(), _SpyObserver()
    subject.attach(first)
    subject.attach(second)
    observation = _observation()

    subject.notify(observation)

    assert first.received == [observation]
    assert second.received == [observation]


def test_detached_observer_stops_receiving_notifications():
    subject = SensorReadingSubject()
    stays, leaves = _SpyObserver(), _SpyObserver()
    subject.attach(stays)
    subject.attach(leaves)

    subject.detach(leaves)
    subject.notify(_observation())

    assert len(stays.received) == 1
    assert leaves.received == []


def test_attaching_the_same_observer_twice_notifies_it_once():
    subject = SensorReadingSubject()
    observer = _SpyObserver()
    subject.attach(observer)
    subject.attach(observer)

    subject.notify(_observation())

    assert len(observer.received) == 1


def test_a_failing_observer_does_not_block_the_others():
    subject = SensorReadingSubject()
    healthy = _SpyObserver()
    subject.attach(_BrokenObserver())
    subject.attach(healthy)

    subject.notify(_observation())

    assert len(healthy.received) == 1


def test_live_feed_keeps_only_the_latest_readings_newest_first():
    feed = LiveFeedObserver(capacity=2)
    for value in (1.0, 2.0, 3.0):
        feed.update(_observation(value))

    assert [obs.reading.value for obs in feed.recent()] == [3.0, 2.0]


def test_threshold_observer_ignores_readings_inside_the_safe_range():
    alerts = ThresholdAlertObserver()

    alerts.update(_observation(2.0))
    alerts.update(_observation(30.0))

    assert alerts.alerts() == ()


def test_threshold_observer_raises_alerts_above_and_below_the_range():
    alerts = ThresholdAlertObserver()

    alerts.update(_observation(35.5))
    alerts.update(_observation(10.0, sensor_type="humedad", device_id="HUM-07"))

    newest, oldest = alerts.alerts()
    assert "por debajo" in newest.message and newest.device_id == "HUM-07"
    assert "por encima" in oldest.message and oldest.value == 35.5
    assert oldest.product_id == "PROD-1"


def test_threshold_observer_ignores_sensor_types_without_a_rule():
    alerts = ThresholdAlertObserver()

    alerts.update(_observation(9999.0, sensor_type="gps"))

    assert alerts.alerts() == ()


def test_device_registry_tracks_last_value_and_reading_count():
    registry = DeviceRegistryObserver()
    registry.update(_observation(20.0))
    registry.update(_observation(21.5))
    registry.update(_observation(55.0, sensor_type="humedad", device_id="HUM-07"))

    hum, temp = registry.devices()

    assert (temp.device_id, temp.last_value, temp.readings_count) == ("TEMP-01", 21.5, 2)
    assert (hum.device_id, hum.readings_count) == ("HUM-07", 1)


def test_monitor_wires_the_three_observers_to_its_subject():
    monitor = SensorMonitor()

    monitor.subject.notify(_observation(40.0))

    assert len(monitor.live_feed.recent()) == 1
    assert len(monitor.alerts.alerts()) == 1
    assert len(monitor.devices.devices()) == 1


def test_vendor_b_adapter_normalizes_nested_payload_and_unit_code():
    reading = VendorBHumidityAdapter(VendorBHumidityClient()).read()

    assert reading == SensorReading("HUM-07", "humedad", 61.5, "%")


def test_simulated_value_overrides_the_vendor_default_except_for_the_faulty_one():
    assert get_vendor_adapter("a", 5.0).read().value == 5.0
    assert get_vendor_adapter("b", 90.0).read().value == 90.0
    assert get_vendor_adapter("a-faulty", 5.0).read().value == -60.0


# ---- API ------------------------------------------------------------------


def _ingest(client, vendor: str, **extra):
    return client.post(
        f"/iot/sensors/{vendor}/ingest",
        json={"product_id": "PROD-obs", "stage": "transporte", **extra},
    )


def test_ingested_readings_appear_in_the_live_feed_and_devices(client):
    _ingest(client, "a")
    _ingest(client, "b")

    readings = client.get("/iot/readings/recent").json()
    devices = client.get("/iot/devices").json()

    assert [reading["device_id"] for reading in readings] == ["HUM-07", "TEMP-01"]
    assert [device["device_id"] for device in devices] == ["HUM-07", "TEMP-01"]
    assert client.get("/iot/alerts").json() == []


def test_out_of_range_reading_is_stored_and_raises_an_alert(client):
    response = _ingest(client, "a", simulated_value=38.0)

    assert response.status_code == 201
    (alert,) = client.get("/iot/alerts").json()
    assert alert["value"] == 38.0
    assert alert["product_id"] == "PROD-obs"
    assert "por encima" in alert["message"]


def test_rejected_reading_is_not_published_to_observers(client):
    response = _ingest(client, "a-faulty")

    assert response.status_code == 400
    assert client.get("/iot/readings/recent").json() == []
    assert client.get("/iot/alerts").json() == []


def test_vendors_endpoint_lists_supported_vendors(client):
    codes = [vendor["code"] for vendor in client.get("/iot/vendors").json()]

    assert codes == ["a", "a-faulty", "b"]


def test_simulated_value_out_of_bounds_returns_422(client):
    assert _ingest(client, "a", simulated_value=5000).status_code == 422
