"""Pruebas de los defectos encontrados en la revisión de código y seguridad."""
import threading
import time
from datetime import date, datetime, timezone

import pytest

from src.forecasting.application.forecast_commands import (
    ForecastCommandInvoker,
    ForecastPlanConflict,
    GenerateForecastCommand,
)
from src.forecasting.application.forecast_planner import ForecastPlanner
from src.forecasting.domain.forecast_plan import DemandRecord
from src.iot.application.monitoring import DeviceRegistryObserver
from src.iot.domain.sensor_observer import SensorObservation
from src.iot.domain.sensor_reading import SensorReading
from src.shared.password_hashing import hash_password, verify_password
from src.shared.security import JWTManager

# ---- Contraseñas y sesión ---------------------------------------------------


def test_verify_password_rejects_passwords_beyond_the_bcrypt_limit():
    stored = hash_password("clave123")

    assert verify_password("a" * 73, stored) is False
    assert verify_password("ñ" * 40, stored) is False  # 80 bytes


def test_login_with_an_overlong_password_returns_401_not_500(client_with_seeded_admin):
    response = client_with_seeded_admin.post(
        "/login", json={"username": "admin", "password": "ñ" * 40}
    )

    assert response.status_code == 401


def test_register_rejects_a_password_longer_than_72_bytes(client):
    response = client.post("/register", json={"username": "largo", "password": "ñ" * 40})

    assert response.status_code == 422


def test_register_can_be_disabled_with_an_environment_variable(client, monkeypatch):
    monkeypatch.setenv("ALLOW_REGISTRATION", "false")

    response = client.post("/register", json={"username": "nuevo", "password": "clave123"})

    assert response.status_code == 403


def test_logout_with_a_replaced_token_does_not_close_the_new_session():
    manager = JWTManager()
    old_token = manager.create_access_token("user_logout_race")
    new_token = manager.create_access_token("user_logout_race")
    try:
        manager.invalidate_token("user_logout_race", old_token)

        assert manager.decode_active_token(new_token)["sub"] == "user_logout_race"
    finally:
        manager.invalidate_token("user_logout_race")


def test_health_does_not_leak_the_database_error(client):
    from src.main import app
    from src.shared.database import get_db

    class _FailingSession:
        def execute(self, *args, **kwargs):
            raise RuntimeError("host=db.interno user=scm password=secreto")

    def _failing_db():
        yield _FailingSession()

    app.dependency_overrides[get_db] = _failing_db

    body = client.get("/health").json()

    assert body == {"status": "error", "database": "disconnected"}


# ---- Límites de entrada -----------------------------------------------------


def _route_payload(**overrides) -> dict:
    return {
        "route_type": "custom",
        "vehicle_type": "furgon",
        "stops": ["Bodega Central", "Cliente A"],
        "departure_date": "2026-09-10",
        **overrides,
    }


def test_infinite_distance_is_rejected_and_nothing_is_stored(client):
    response = client.post(
        "/logistics/routes",
        content='{"route_type":"custom","vehicle_type":"furgon","stops":["A","B"],'
        '"departure_date":"2026-09-10","total_distance_km":Infinity}',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
    assert client.get("/logistics/routes").json() == []


def test_overlong_stop_name_is_rejected(client):
    response = client.post(
        "/logistics/routes", json=_route_payload(stops=["Bodega Central", "x" * 121])
    )

    assert response.status_code == 422


def test_corridor_rejects_a_route_listed_twice_across_levels(client):
    route_id = client.post("/logistics/routes", json=_route_payload()).json()["route_id"]

    response = client.post(
        "/logistics/corridors",
        json={
            "name": "Duplicado",
            "route_ids": [route_id],
            "sub_corridors": [{"name": "Interno", "route_ids": [route_id]}],
        },
    )

    assert response.status_code == 422


def test_corridor_rejects_more_nodes_than_the_total_cap(client):
    children = [{"name": f"c{index}", "route_ids": [index + 1]} for index in range(30)]

    response = client.post(
        "/logistics/corridors", json={"name": "Enorme", "sub_corridors": children}
    )

    assert response.status_code == 422


def test_tracking_field_longer_than_its_column_is_rejected(client):
    response = client.post(
        "/tracking/events",
        json={
            "event_type": "stage_change",
            "product_id": "PROD-largo",
            "stage": "x" * 51,
            "previous_stage": "fabricacion",
            "responsible": "Planta 1",
        },
    )

    assert response.status_code == 422


def test_duplicate_demand_period_and_product_code_never_return_500(client):
    for quantity in (10, 12):
        response = client.post(
            "/forecasting/demand",
            json={"product_id": "P-dup", "period": "2026-01-01", "quantity": quantity},
        )
        assert response.status_code == 201
    assert client.post("/products", json={"code": "P-dup", "name": "Uno"}).status_code == 201
    assert client.post("/products", json={"code": "P-dup", "name": "Dos"}).status_code == 409


# ---- Concurrencia del invoker ----------------------------------------------


class _History:
    def upsert(self, record):
        raise AssertionError("no se usa")

    def list_by_product(self, product_id):
        return [DemandRecord(product_id, date(2026, 1, 1), 10.0)]


class _SlowPlans:
    """Repositorio lento: abre la ventana en la que dos hilos compiten."""

    def __init__(self):
        self.plans = {}
        self.fail_on_delete = False

    def get(self, product_id):
        time.sleep(0.02)
        return self.plans.get(product_id)

    def save(self, plan):
        self.plans[plan.product_id] = plan
        return plan

    def delete(self, product_id):
        if self.fail_on_delete:
            raise RuntimeError("la base de datos no responde")
        self.plans.pop(product_id, None)


def test_two_simultaneous_generates_leave_exactly_one_undoable_command():
    invoker = ForecastCommandInvoker()
    planner = ForecastPlanner(_History(), _SlowPlans())
    outcomes: list[str] = []

    def generate() -> None:
        try:
            invoker.run(GenerateForecastCommand("P-1"), planner)
            outcomes.append("ok")
        except ForecastPlanConflict:
            outcomes.append("conflict")

    threads = [threading.Thread(target=generate) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(outcomes) == ["conflict", "ok"]
    assert [entry.command for entry in invoker.log()] == ["generate"]


def test_a_failed_undo_keeps_the_command_so_it_can_be_retried():
    invoker = ForecastCommandInvoker()
    plans = _SlowPlans()
    planner = ForecastPlanner(_History(), plans)
    invoker.run(GenerateForecastCommand("P-1"), planner)
    plans.fail_on_delete = True

    with pytest.raises(RuntimeError):
        invoker.undo_last("P-1", planner)

    assert invoker.can_undo("P-1")
    plans.fail_on_delete = False
    assert invoker.undo_last("P-1", planner) is None
    assert "P-1" not in plans.plans


# ---- Registro de dispositivos ----------------------------------------------


def _observation(device_id: str, minute: int) -> SensorObservation:
    return SensorObservation(
        reading=SensorReading(device_id, "temperatura", 20.0, "°C"),
        product_id="PROD-1",
        stage="transporte",
        received_at=datetime(2026, 11, 1, 12, minute, tzinfo=timezone.utc),
    )


def test_full_device_registry_evicts_the_device_silent_for_longest():
    registry = DeviceRegistryObserver(capacity=2)
    registry.update(_observation("A", minute=0))
    registry.update(_observation("B", minute=1))
    registry.update(_observation("A", minute=2))

    registry.update(_observation("C", minute=3))

    assert [device.device_id for device in registry.devices()] == ["A", "C"]
