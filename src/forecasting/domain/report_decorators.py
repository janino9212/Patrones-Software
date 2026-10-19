from src.forecasting.domain.forecast_report import ForecastReport


class ForecastReportDecorator(ForecastReport):
    def __init__(self, wrapped: ForecastReport):
        self._wrapped = wrapped

    def generate(self) -> dict:
        return self._wrapped.generate()


class ConfidenceIntervalDecorator(ForecastReportDecorator):
    def generate(self) -> dict:
        data = super().generate()
        margin = data["predicted_demand"] * 0.1
        data["confidence_interval"] = [
            round(data["predicted_demand"] - margin, 2),
            round(data["predicted_demand"] + margin, 2),
        ]
        print(f"[DECORATOR] Intervalo de confianza agregado: {data['confidence_interval']}")
        return data


class TrendAnnotationDecorator(ForecastReportDecorator):
    def generate(self) -> dict:
        data = super().generate()
        data["trend"] = "alza" if data["based_on_events"] >= 3 else "insuficientes datos"
        print(f"[DECORATOR] Tendencia anotada: {data['trend']}")
        return data