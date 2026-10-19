from abc import ABC, abstractmethod


class NotificationChannel(ABC):
    """Implementor (GoF Bridge): CÓMO se envía un mensaje, independiente
    de qué tan urgente sea."""

    @abstractmethod
    def send(self, message: str) -> None:
        ...