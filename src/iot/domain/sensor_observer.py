import logging
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from src.iot.domain.sensor_reading import SensorReading

logger = logging.getLogger("scm.iot.observer")


@dataclass(frozen=True)
class SensorObservation:
    """Lo que se publica a los observadores: una lectura ya aceptada, con el
    producto y la etapa a los que pertenece."""

    reading: SensorReading
    product_id: str
    stage: str
    received_at: datetime


class SensorObserver(ABC):
    """Observer (GoF): reacciona a cada lectura publicada."""

    @abstractmethod
    def update(self, observation: SensorObservation) -> None:
        ...


class SensorReadingSubject:
    """Subject (GoF): mantiene la lista de observadores y les avisa de cada
    lectura nueva. Quien publica no sabe cuántos observadores hay ni qué
    hace cada uno; agregar una reacción nueva es suscribir otro observador."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._observers: tuple[SensorObserver, ...] = ()

    def attach(self, observer: SensorObserver) -> None:
        with self._lock:
            if observer not in self._observers:
                self._observers = (*self._observers, observer)

    def detach(self, observer: SensorObserver) -> None:
        with self._lock:
            self._observers = tuple(o for o in self._observers if o is not observer)

    def notify(self, observation: SensorObservation) -> None:
        for observer in self._observers:
            try:
                observer.update(observation)
            except Exception:
                # Un observador que falla no debe impedir que los demás se
                # enteren ni tumbar la ingesta, que ya quedó registrada.
                logger.exception(
                    "[OBSERVER] %s falló al procesar la lectura de %s",
                    type(observer).__name__, observation.reading.device_id,
                )
