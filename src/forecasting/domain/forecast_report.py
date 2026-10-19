from abc import ABC, abstractmethod


class ForecastReport(ABC):
    @abstractmethod
    def generate(self) -> dict:
        ...


class BaseForecastReport(ForecastReport):
    def __init__(self, product_id: str, predicted_demand: float, based_on_events: int):
        self._product_id = product_id
        self._predicted_demand = predicted_demand
        self._based_on_events = based_on_events

    def generate(self) -> dict:
        return {
            "product_id": self._product_id,
            "predicted_demand": self._predicted_demand,
            "based_on_events": self._based_on_events,
        }