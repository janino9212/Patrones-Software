import logging
from dataclasses import dataclass
from types import MappingProxyType
from typing import Callable, Mapping

from src.iot.domain.sensor_adapter_port import SensorDataPort
from src.iot.domain.sensor_reading import SensorReading
from src.iot.infrastructure.vendor_clients import (
    VendorAFaultyTemperatureClient,
    VendorATemperatureClient,
    VendorBHumidityClient,
)

logger = logging.getLogger("scm.iot.adapter")

_VENDOR_B_UNITS = MappingProxyType({"pct": "%"})


class VendorATemperatureAdapter(SensorDataPort):
    """Adapter concreto: traduce el payload del fabricante A al
    SensorReading común que el resto de la aplicación entiende."""

    def __init__(self, client: VendorATemperatureClient):
        self._client = client

    def read(self) -> SensorReading:
        raw = self._client.fetch_reading()
        logger.info("[ADAPTER] Normalizando payload fabricante A: %s", raw)
        return SensorReading(
            device_id=raw["sensorId"],
            sensor_type="temperatura",
            value=raw["tempC"],
            unit="°C",
        )


class VendorBHumidityAdapter(SensorDataPort):
    """Adapter concreto del fabricante B: otro método (`get_measure`), la
    lectura anidada y la unidad como código."""

    def __init__(self, client: VendorBHumidityClient):
        self._client = client

    def read(self) -> SensorReading:
        raw = self._client.get_measure()
        logger.info("[ADAPTER] Normalizando payload fabricante B: %s", raw)
        reading = raw["reading"]
        return SensorReading(
            device_id=raw["device"],
            sensor_type="humedad",
            value=reading["val"],
            unit=_VENDOR_B_UNITS.get(reading["uom"], reading["uom"]),
        )


@dataclass(frozen=True)
class VendorInfo:
    code: str
    label: str
    sensor_type: str
    unit: str
    accepts_simulated_value: bool = True


AdapterFactory = Callable[[float | None], SensorDataPort]

_VENDORS: Mapping[str, tuple[VendorInfo, AdapterFactory]] = MappingProxyType(
    {
        "a": (
            VendorInfo("a", "Fabricante A, temperatura", "temperatura", "°C"),
            lambda value: VendorATemperatureAdapter(VendorATemperatureClient(value)),
        ),
        "a-faulty": (
            VendorInfo(
                "a-faulty", "Fabricante A, sensor averiado", "temperatura", "°C",
                accepts_simulated_value=False,
            ),
            lambda value: VendorATemperatureAdapter(VendorAFaultyTemperatureClient()),
        ),
        "b": (
            VendorInfo("b", "Fabricante B, humedad", "humedad", "%"),
            lambda value: VendorBHumidityAdapter(VendorBHumidityClient(value)),
        ),
    }
)


def supported_vendors() -> tuple[VendorInfo, ...]:
    return tuple(info for info, _factory in _VENDORS.values())


def get_vendor_adapter(vendor: str, simulated_value: float | None = None) -> SensorDataPort:
    entry = _VENDORS.get(vendor)
    if entry is None:
        raise ValueError(f"Fabricante de sensor no soportado: '{vendor}'")
    _info, factory = entry
    return factory(simulated_value)
