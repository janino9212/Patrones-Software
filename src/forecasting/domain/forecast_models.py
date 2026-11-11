from abc import ABC, abstractmethod
from types import MappingProxyType
from typing import Mapping, Sequence

_MOVING_AVERAGE_WINDOW = 3
_SMOOTHING_ALPHA = 0.5


class InsufficientDemandData(ValueError):
    """El historial no alcanza para el modelo de pronóstico elegido."""


class DemandForecastModel(ABC):
    """Template Method (GoF): `forecast` fija los pasos de todo pronóstico
    (limpiar la serie, comprobar que alcanza, estimar, ajustar el resultado)
    y cada modelo concreto solo aporta la estimación (`_estimate`)."""

    name: str
    label: str
    min_points: int = 1

    def forecast(self, series: Sequence[float]) -> float:
        """Método plantilla: demanda estimada para el siguiente período."""
        prepared = self._prepare(series)
        self._check_enough_data(prepared)
        estimate = self._estimate(prepared)
        return self._finalize(estimate)

    def _prepare(self, series: Sequence[float]) -> list[float]:
        """Paso con implementación por defecto: copia la serie como floats."""
        return [float(value) for value in series]

    def _check_enough_data(self, series: Sequence[float]) -> None:
        if len(series) < self.min_points:
            raise InsufficientDemandData(
                f"El modelo '{self.label}' necesita al menos {self.min_points} "
                f"período(s) de demanda y hay {len(series)}"
            )

    @abstractmethod
    def _estimate(self, series: Sequence[float]) -> float:
        """Paso que define cada modelo: la estimación sin ajustar."""

    def _finalize(self, estimate: float) -> float:
        """Paso con implementación por defecto: la demanda no es negativa."""
        return round(max(estimate, 0.0), 2)


class MovingAverageModel(DemandForecastModel):
    name = "moving_average"
    label = "Promedio móvil"

    def _estimate(self, series: Sequence[float]) -> float:
        window = series[-_MOVING_AVERAGE_WINDOW:]
        return sum(window) / len(window)


class ExponentialSmoothingModel(DemandForecastModel):
    name = "exponential_smoothing"
    label = "Suavizado exponencial"

    def _estimate(self, series: Sequence[float]) -> float:
        level = series[0]
        for value in series[1:]:
            level = _SMOOTHING_ALPHA * value + (1 - _SMOOTHING_ALPHA) * level
        return level


class LinearTrendModel(DemandForecastModel):
    name = "linear_trend"
    label = "Tendencia lineal"
    min_points = 2

    def _estimate(self, series: Sequence[float]) -> float:
        """Recta de mínimos cuadrados evaluada en el período siguiente."""
        count = len(series)
        mean_x = (count - 1) / 2
        mean_y = sum(series) / count
        covariance = sum((x - mean_x) * (y - mean_y) for x, y in enumerate(series))
        variance = sum((x - mean_x) ** 2 for x in range(count))
        slope = covariance / variance
        return mean_y + slope * (count - mean_x)


_MODELS: Mapping[str, DemandForecastModel] = MappingProxyType(
    {
        model.name: model
        for model in (MovingAverageModel(), ExponentialSmoothingModel(), LinearTrendModel())
    }
)
DEFAULT_MODEL_NAME = MovingAverageModel.name


def available_models() -> tuple[DemandForecastModel, ...]:
    return tuple(_MODELS.values())


def get_model(name: str) -> DemandForecastModel:
    model = _MODELS.get(name)
    if model is None:
        raise ValueError(f"Modelo de pronóstico no soportado: '{name}'")
    return model
