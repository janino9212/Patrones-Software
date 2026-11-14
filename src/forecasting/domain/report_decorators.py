import logging

from src.forecasting.domain.forecast_report import ForecastReport

logger = logging.getLogger("scm.forecasting.decorator")

_CONFIDENCE_MARGIN = 0.1
_MIN_EVENTS_FOR_TREND = 3


class ForecastReportDecorator(ForecastReport):
    def __init__(self, wrapped: ForecastReport):
        self._wrapped = wrapped

    def generate(self) -> dict:
        return self._wrapped.generate()


class ConfidenceIntervalDecorator(ForecastReportDecorator):
    def generate(self) -> dict:
        data = super().generate()
        margin = data["predicted_demand"] * _CONFIDENCE_MARGIN
        data["confidence_interval"] = [
            round(data["predicted_demand"] - margin, 2),
            round(data["predicted_demand"] + margin, 2),
        ]
        logger.info("[DECORATOR] Intervalo de confianza agregado: %s", data["confidence_interval"])
        return data


class SourceAnnotationDecorator(ForecastReportDecorator):
    """Anota de dónde salió la demanda estimada: el nombre del modelo de
    pronóstico o la estimación simulada a partir de eventos de tracking."""

    def __init__(self, wrapped: ForecastReport, source: str):
        super().__init__(wrapped)
        self._source = source

    def generate(self) -> dict:
        return {**super().generate(), "source": self._source}


class TrendAnnotationDecorator(ForecastReportDecorator):
    def generate(self) -> dict:
        data = super().generate()
        data["trend"] = "alza" if data["based_on_events"] >= _MIN_EVENTS_FOR_TREND else "insuficientes datos"
        logger.info("[DECORATOR] Tendencia anotada: %s", data["trend"])
        return data
