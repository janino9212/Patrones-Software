from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from src.forecasting.application.authorized_forecast_report_proxy import (
    AuthorizedForecastReportProxy,
)
from src.forecasting.domain.report_service import ForecastAccessDenied
from src.shared.security import JWTManager


class _SpyForecastService:
    """RealSubject de prueba: registra cuántas veces se le llamó."""

    def __init__(self):
        self.calls: list[str] = []

    def execute(self, product_id: str) -> dict:
        self.calls.append(product_id)
        return {"product_id": product_id, "predicted_demand": 12.5}


def _accepting_decoder(token: str) -> dict:
    return {"sub": "tester"}


def _rejecting_decoder(token: str) -> dict:
    raise ValueError("Token inválido o expirado")


def test_valid_token_delegates_to_real_service_and_returns_its_result():
    real = _SpyForecastService()
    proxy = AuthorizedForecastReportProxy(real, "token-ok", token_decoder=_accepting_decoder)

    result = proxy.execute("PROD-1")

    assert result == {"product_id": "PROD-1", "predicted_demand": 12.5}
    assert real.calls == ["PROD-1"]


def test_missing_token_is_denied_without_calling_real_service():
    real = _SpyForecastService()
    proxy = AuthorizedForecastReportProxy(real, None, token_decoder=_accepting_decoder)

    with pytest.raises(ForecastAccessDenied, match="token"):
        proxy.execute("PROD-1")

    assert real.calls == []


def test_invalid_token_is_denied_without_calling_real_service():
    real = _SpyForecastService()
    proxy = AuthorizedForecastReportProxy(real, "token-malo", token_decoder=_rejecting_decoder)

    with pytest.raises(ForecastAccessDenied):
        proxy.execute("PROD-1")

    assert real.calls == []


def test_token_without_subject_is_denied_without_calling_real_service():
    real = _SpyForecastService()
    proxy = AuthorizedForecastReportProxy(real, "token-sin-sub", token_decoder=lambda token: {})

    with pytest.raises(ForecastAccessDenied):
        proxy.execute("PROD-1")

    assert real.calls == []


def test_expired_jwt_is_denied_without_calling_real_service():
    manager = JWTManager()
    expired = jwt.encode(
        {"sub": "proxy_test_user", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        manager._secret_key,
        algorithm=manager._algorithm,
    )
    real = _SpyForecastService()

    with pytest.raises(ForecastAccessDenied):
        AuthorizedForecastReportProxy(real, expired).execute("PROD-1")

    assert real.calls == []


def test_default_decoder_accepts_a_real_jwt_and_rejects_garbage():
    manager = JWTManager()
    manager.invalidate_token("proxy_test_user")
    try:
        token = manager.create_access_token("proxy_test_user")
        real = _SpyForecastService()

        assert AuthorizedForecastReportProxy(real, token).execute("PROD-1")["product_id"] == "PROD-1"
        with pytest.raises(ForecastAccessDenied):
            AuthorizedForecastReportProxy(real, "no-es-un-jwt").execute("PROD-1")
    finally:
        manager.invalidate_token("proxy_test_user")
