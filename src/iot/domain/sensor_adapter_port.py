from abc import ABC, abstractmethod

from src.iot.domain.sensor_reading import SensorReading


class SensorDataPort(ABC):
    """Target (GoF Adapter): interfaz común que espera el resto del
    sistema, sin importar cómo entrega los datos cada fabricante."""

    @abstractmethod
    def read(self) -> SensorReading:
        ...