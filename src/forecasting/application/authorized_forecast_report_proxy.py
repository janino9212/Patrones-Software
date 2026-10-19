import logging
from typing import Callable

from src.forecasting.domain.report_service import ForecastAccessDenied, ForecastReportService
from src.shared.security import JWTManager

logger = logging.getLogger("scm.forecasting.proxy")

TokenDecoder = Callable[[str], dict]


class AuthorizedForecastReportProxy:
    """Proxy de protección (GoF): controla el acceso al sujeto real
    (ForecastReportService) validando un JWT antes de delegar la llamada.

    Si el token falta o no es válido, el sujeto real nunca se ejecuta."""

    def __init__(
        self,
        real_service: ForecastReportService,
        token: str | None,
        token_decoder: TokenDecoder | None = None,
    ):
        self._real_service = real_service
        self._token = token
        self._token_decoder = token_decoder

    def execute(self, product_id: str) -> dict:
        username = self._authorize()
        logger.info("[PROXY] Acceso autorizado para %r al reporte de %r", username, product_id)
        return self._real_service.execute(product_id)

    def _authorize(self) -> str:
        if not self._token:
            logger.warning("[PROXY] Acceso denegado: falta el token")
            raise ForecastAccessDenied("Falta el token de acceso")

        decoder = self._token_decoder or JWTManager().decode_token
        try:
            payload = decoder(self._token)
        except ValueError as exc:
            logger.warning("[PROXY] Acceso denegado: token inválido o expirado")
            raise ForecastAccessDenied("Token inválido o expirado") from exc
        username = payload.get("sub")
        if not isinstance(username, str) or not username:
            logger.warning("[PROXY] Acceso denegado: el token no identifica a un usuario")
            raise ForecastAccessDenied("Token inválido o expirado")
        return username
