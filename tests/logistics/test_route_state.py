import dataclasses
from datetime import date

import pytest

from src.logistics.application.change_route_status import ChangeRouteStatusUseCase, RouteNotFound
from src.logistics.domain.entities import DistributionRoute, RouteStop
from src.logistics.domain.route_state import (
    CancelledState,
    DeliveredState,
    InTransitState,
    InvalidRouteTransition,
    PlannedState,
    state_for,
)


def _route(status: str = "planned") -> DistributionRoute:
    return DistributionRoute(
        vehicle_type="camion_estandar",
        departure_date=date(2026, 9, 10),
        stops=(RouteStop(1, "A"), RouteStop(2, "B")),
        route_id=1,
        status=status,
    )


def test_planned_route_can_be_dispatched_or_cancelled():
    assert isinstance(PlannedState().dispatch(), InTransitState)
    assert isinstance(PlannedState().cancel(), CancelledState)


def test_planned_route_cannot_be_delivered_directly():
    with pytest.raises(InvalidRouteTransition, match="planificada"):
        PlannedState().deliver()


def test_route_in_transit_can_be_delivered_or_cancelled():
    assert isinstance(InTransitState().deliver(), DeliveredState)
    assert isinstance(InTransitState().cancel(), CancelledState)


@pytest.mark.parametrize("terminal", [DeliveredState(), CancelledState()])
@pytest.mark.parametrize("action", ["dispatch", "deliver", "cancel"])
def test_terminal_states_reject_every_action(terminal, action):
    assert terminal.allowed_actions == ()
    with pytest.raises(InvalidRouteTransition):
        getattr(terminal, action)()


@pytest.mark.parametrize("status", ["planned", "in_transit", "delivered", "cancelled"])
def test_allowed_actions_match_the_transitions_that_succeed(status):
    state = state_for(status)

    succeeded = []
    for action in ("dispatch", "deliver", "cancel"):
        try:
            getattr(state, action)()
        except InvalidRouteTransition:
            continue
        succeeded.append(action)

    assert tuple(succeeded) == state.allowed_actions


def test_state_for_rejects_unknown_status():
    with pytest.raises(ValueError, match="desconocido"):
        state_for("perdida")


def test_route_delegates_actions_to_its_state_and_stays_immutable():
    planned = _route()

    in_transit = planned.dispatch()
    delivered = in_transit.deliver()

    assert planned.status == "planned"
    assert (in_transit.status, delivered.status) == ("in_transit", "delivered")
    assert delivered.route_id == planned.route_id


def test_route_rejects_an_action_its_state_does_not_allow():
    with pytest.raises(InvalidRouteTransition, match="entregada"):
        _route("delivered").cancel()


class _FakeRepository:
    def __init__(self, routes: dict):
        self.routes = routes

    def get(self, route_id):
        return self.routes.get(route_id)

    def update_status(self, route_id, new_status, expected_status):
        current = self.routes[route_id]
        if current.status != expected_status:
            return None
        self.routes[route_id] = dataclasses.replace(current, status=new_status)
        return self.routes[route_id]


class _RacingRepository(_FakeRepository):
    """Simula que otra petición cambia la ruta entre la lectura y la escritura."""

    def get(self, route_id):
        route = super().get(route_id)
        self.routes[route_id] = dataclasses.replace(route, status="cancelled")
        return route


def test_use_case_persists_the_new_status():
    repository = _FakeRepository({1: _route()})

    updated = ChangeRouteStatusUseCase(repository).execute(1, "dispatch")

    assert updated.status == "in_transit"
    assert updated.state.allowed_actions == ("deliver", "cancel")


def test_use_case_does_not_persist_an_invalid_transition():
    repository = _FakeRepository({1: _route("delivered")})

    with pytest.raises(InvalidRouteTransition):
        ChangeRouteStatusUseCase(repository).execute(1, "cancel")

    assert repository.routes[1].status == "delivered"


def test_use_case_rejects_the_update_when_the_route_changed_meanwhile():
    repository = _RacingRepository({1: _route("in_transit")})

    with pytest.raises(InvalidRouteTransition, match="cambió de estado"):
        ChangeRouteStatusUseCase(repository).execute(1, "deliver")

    assert repository.routes[1].status == "cancelled"


def test_use_case_reports_missing_route_and_unknown_action():
    with pytest.raises(RouteNotFound):
        ChangeRouteStatusUseCase(_FakeRepository({})).execute(99, "dispatch")
    with pytest.raises(ValueError, match="no soportada"):
        ChangeRouteStatusUseCase(_FakeRepository({1: _route()})).execute(1, "teletransportar")
