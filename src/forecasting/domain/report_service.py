from typing import Protocol


class ForecastAccessDenied(Exception):
    """El llamante no está autorizado para pedir un reporte de pronóstico."""


class ForecastReportService(Protocol):
    """Subject del patrón Proxy: interfaz común que cumplen tanto el sujeto
    real (GenerateForecastReportUseCase) como su proxy de protección, para
    que el cliente no distinga uno del otro."""

    def execute(self, product_id: str) -> dict: ...
