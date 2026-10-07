from abc import ABC, abstractmethod


class RouteComponent(ABC):
    @abstractmethod
    def total_distance_km(self) -> float:
        ...

    @abstractmethod
    def describe(self) -> str:
        ...