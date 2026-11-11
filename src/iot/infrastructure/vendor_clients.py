"""Clientes de fabricantes (Adaptees), simulados: no hay hardware real.

Cada uno acepta un `simulated_value` opcional para que la interfaz pueda
enviar la lectura que quiera probar; sin él devuelven un valor fijo."""

_VENDOR_A_DEFAULT_CELSIUS = 23.8
_VENDOR_A_FAULTY_CELSIUS = -60.0
_VENDOR_B_DEFAULT_HUMIDITY = 61.5


class VendorATemperatureClient:
    """Adaptee: cliente del fabricante A, con su propio formato de payload,
    distinto al que espera el resto de la aplicación."""

    def __init__(self, simulated_value: float | None = None):
        self._simulated_value = simulated_value

    def fetch_reading(self) -> dict:
        value = self._simulated_value
        return {"sensorId": "TEMP-01", "tempC": _VENDOR_A_DEFAULT_CELSIUS if value is None else value}


class VendorAFaultyTemperatureClient(VendorATemperatureClient):
    """Variante del cliente A con una lectura fuera de rango físico, para
    probar el camino de error. Ignora el valor simulado."""

    def fetch_reading(self) -> dict:
        return {"sensorId": "TEMP-02", "tempC": _VENDOR_A_FAULTY_CELSIUS}


class VendorBHumidityClient:
    """Adaptee: cliente del fabricante B. Otro método, otra estructura
    (lectura anidada) y la unidad como código ('pct')."""

    def __init__(self, simulated_value: float | None = None):
        self._simulated_value = simulated_value

    def get_measure(self) -> dict:
        value = self._simulated_value
        return {
            "device": "HUM-07",
            "reading": {
                "val": _VENDOR_B_DEFAULT_HUMIDITY if value is None else value,
                "uom": "pct",
            },
        }
