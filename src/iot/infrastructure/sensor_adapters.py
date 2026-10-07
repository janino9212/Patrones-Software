from src.iot.domain.sensor_adapter_port import SensorDataPort
from src.iot.domain.sensor_reading import SensorReading
from src.iot.infrastructure.vendor_clients import (
    VendorAFaultyTemperatureClient,
    VendorATemperatureClient,
)


class VendorATemperatureAdapter(SensorDataPort):
    """Adapter concreto: traduce el payload del fabricante A al
    SensorReading común que el resto de la aplicación entiende."""

    def __init__(self, client: VendorATemperatureClient):
        self._client = client

    def read(self) -> SensorReading:
        raw = self._client.fetch_reading()
        print(f"[ADAPTER] Normalizando payload fabricante A: {raw}")
        return SensorReading(
            device_id=raw["sensorId"],
            sensor_type="temperatura",
            value=raw["tempC"],
            unit="°C",
        )


_VENDOR_ADAPTERS = {
    "a": lambda: VendorATemperatureAdapter(VendorATemperatureClient()),
    "a-faulty": lambda: VendorATemperatureAdapter(VendorAFaultyTemperatureClient()),
}


def get_vendor_adapter(vendor: str) -> SensorDataPort:
    factory = _VENDOR_ADAPTERS.get(vendor)
    if factory is None:
        raise ValueError(f"Fabricante de sensor no soportado: '{vendor}'")
    return factory()