class VendorATemperatureClient:
    """Adaptee: cliente real del fabricante A (simulado), con su propio
    formato de payload, distinto al que espera el resto de la aplicación."""

    def fetch_reading(self) -> dict:
        return {"sensorId": "TEMP-01", "tempC": 23.8}


class VendorAFaultyTemperatureClient:
    """Variante del cliente A con una lectura fuera de rango, para probar
    el camino de error/alerta."""

    def fetch_reading(self) -> dict:
        return {"sensorId": "TEMP-02", "tempC": -60.0}