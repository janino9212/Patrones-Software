from dataclasses import dataclass


@dataclass(frozen=True)
class SensorReading:
    """Formato común al que se normaliza cualquier lectura de sensor,
    sin importar el fabricante de origen."""

    device_id: str
    sensor_type: str
    value: float
    unit: str