import threading
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Mapping

from src.iot.domain.sensor_observer import SensorObservation, SensorObserver, SensorReadingSubject

_MAX_FEED = 50
_MAX_ALERTS = 100
_MAX_DEVICES = 200


class LiveFeedObserver(SensorObserver):
    """Guarda las últimas lecturas para el panel de monitoreo."""

    def __init__(self, capacity: int = _MAX_FEED):
        self._lock = threading.Lock()
        self._feed: deque[SensorObservation] = deque(maxlen=capacity)

    def update(self, observation: SensorObservation) -> None:
        with self._lock:
            self._feed.append(observation)

    def recent(self) -> tuple[SensorObservation, ...]:
        """De la lectura más reciente a la más antigua."""
        with self._lock:
            return tuple(reversed(self._feed))


@dataclass(frozen=True)
class SensorThreshold:
    minimum: float
    maximum: float


@dataclass(frozen=True)
class SensorAlert:
    device_id: str
    sensor_type: str
    value: float
    unit: str
    product_id: str
    message: str
    raised_at: datetime


DEFAULT_THRESHOLDS: Mapping[str, SensorThreshold] = MappingProxyType(
    {
        "temperatura": SensorThreshold(minimum=2.0, maximum=30.0),
        "humedad": SensorThreshold(minimum=20.0, maximum=80.0),
    }
)


class ThresholdAlertObserver(SensorObserver):
    """Levanta una alerta cuando una lectura se sale del rango seguro de su
    tipo de sensor."""

    def __init__(
        self,
        thresholds: Mapping[str, SensorThreshold] = DEFAULT_THRESHOLDS,
        capacity: int = _MAX_ALERTS,
    ):
        self._thresholds = thresholds
        self._lock = threading.Lock()
        self._alerts: deque[SensorAlert] = deque(maxlen=capacity)

    def update(self, observation: SensorObservation) -> None:
        reading = observation.reading
        threshold = self._thresholds.get(reading.sensor_type)
        if threshold is None or threshold.minimum <= reading.value <= threshold.maximum:
            return
        direction = "por debajo" if reading.value < threshold.minimum else "por encima"
        alert = SensorAlert(
            device_id=reading.device_id,
            sensor_type=reading.sensor_type,
            value=reading.value,
            unit=reading.unit,
            product_id=observation.product_id,
            message=(
                f"{reading.sensor_type.capitalize()} {direction} del rango seguro "
                f"({threshold.minimum:g} a {threshold.maximum:g} {reading.unit})"
            ),
            raised_at=observation.received_at,
        )
        with self._lock:
            self._alerts.append(alert)

    def alerts(self) -> tuple[SensorAlert, ...]:
        """De la alerta más reciente a la más antigua."""
        with self._lock:
            return tuple(reversed(self._alerts))


@dataclass(frozen=True)
class DeviceStatus:
    device_id: str
    sensor_type: str
    last_value: float
    unit: str
    last_product_id: str
    last_seen_at: datetime
    readings_count: int


class DeviceRegistryObserver(SensorObserver):
    """Lleva el último estado conocido de cada dispositivo."""

    def __init__(self, capacity: int = _MAX_DEVICES):
        self._capacity = capacity
        self._lock = threading.Lock()
        self._devices: dict[str, DeviceStatus] = {}

    def update(self, observation: SensorObservation) -> None:
        reading = observation.reading
        with self._lock:
            previous = self._devices.get(reading.device_id)
            if previous is None and len(self._devices) >= self._capacity:
                # Lleno: sale el dispositivo que lleva más tiempo sin reportar.
                stalest = min(self._devices.values(), key=lambda device: device.last_seen_at)
                del self._devices[stalest.device_id]
            self._devices[reading.device_id] = DeviceStatus(
                device_id=reading.device_id,
                sensor_type=reading.sensor_type,
                last_value=reading.value,
                unit=reading.unit,
                last_product_id=observation.product_id,
                last_seen_at=observation.received_at,
                readings_count=(previous.readings_count if previous else 0) + 1,
            )

    def devices(self) -> tuple[DeviceStatus, ...]:
        with self._lock:
            return tuple(sorted(self._devices.values(), key=lambda device: device.device_id))


class SensorMonitor:
    """Arma el Subject con sus tres observadores. El estado vive en memoria
    del proceso: se reinicia con la API (las lecturas en sí quedan
    guardadas como eventos de tracking)."""

    def __init__(self) -> None:
        self.subject = SensorReadingSubject()
        self.live_feed = LiveFeedObserver()
        self.alerts = ThresholdAlertObserver()
        self.devices = DeviceRegistryObserver()
        for observer in (self.live_feed, self.alerts, self.devices):
            self.subject.attach(observer)


_monitor = SensorMonitor()


def get_sensor_monitor() -> SensorMonitor:
    """Dependencia de FastAPI: el monitor compartido por todas las peticiones."""
    return _monitor
