import pytest

from src.iot.domain.sensor_adapter_port import SensorDataPort
from src.iot.domain.sensor_reading import SensorReading
from src.iot.infrastructure.sensor_adapters import (
    VendorATemperatureAdapter,
    get_vendor_adapter,
)
from src.iot.infrastructure.vendor_clients import (
    VendorAFaultyTemperatureClient,
    VendorATemperatureClient,
)


def test_adapter_normalizes_vendor_a_payload_to_common_reading():
    adapter = VendorATemperatureAdapter(VendorATemperatureClient())

    reading = adapter.read()

    assert reading == SensorReading(
        device_id="TEMP-01", sensor_type="temperatura", value=23.8, unit="°C"
    )


def test_adapter_wraps_faulty_client_without_changing_the_value():
    adapter = VendorATemperatureAdapter(VendorAFaultyTemperatureClient())

    reading = adapter.read()

    assert reading.device_id == "TEMP-02"
    assert reading.value == -60.0


@pytest.mark.parametrize("vendor", ["a", "a-faulty"])
def test_get_vendor_adapter_returns_port_implementation(vendor):
    assert isinstance(get_vendor_adapter(vendor), SensorDataPort)


def test_get_vendor_adapter_with_unknown_vendor_raises_value_error():
    with pytest.raises(ValueError, match="no soportado"):
        get_vendor_adapter("fabricante-x")
