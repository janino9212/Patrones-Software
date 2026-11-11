import pytest

from src.logistics.domain.location_catalog import (
    Location,
    distance_km,
    find_location,
    path_length_km,
)
from src.logistics.domain.route_optimization import (
    KeepOrderStrategy,
    NearestNeighborStrategy,
    RouteOptimizationStrategy,
    RoutePlanner,
    TwoOptStrategy,
    get_strategy,
)

# Puntos sobre una línea (misma latitud): el orden óptimo es evidente.
_ORIGIN = Location("origen", 0.0, 0.0)
_NEAR = Location("cerca", 0.0, 1.0)
_MID = Location("medio", 0.0, 2.0)
_FAR = Location("lejos", 0.0, 3.0)


def test_distance_between_known_cities_is_plausible():
    bucaramanga = find_location("bucaramanga")
    bogota = find_location("Bogotá")

    assert 280 < distance_km(bucaramanga, bogota) < 300
    assert distance_km(bucaramanga, bucaramanga) == 0


def test_find_location_ignores_case_and_surrounding_spaces():
    assert find_location("  GIRÓN ").name == "Girón"
    assert find_location("Ciudad Inventada") is None


def test_keep_order_strategy_returns_stops_unchanged():
    stops = [_ORIGIN, _FAR, _NEAR, _MID]

    assert KeepOrderStrategy().order(stops) == stops


def test_nearest_neighbor_keeps_origin_and_visits_closest_first():
    ordered = NearestNeighborStrategy().order([_ORIGIN, _FAR, _NEAR, _MID])

    assert ordered == [_ORIGIN, _NEAR, _MID, _FAR]


@pytest.mark.parametrize("strategy", [NearestNeighborStrategy(), TwoOptStrategy()])
def test_optimizing_strategies_never_lengthen_the_route(strategy):
    stops = [_ORIGIN, _FAR, _NEAR, _MID]

    ordered = strategy.order(stops)

    assert ordered[0] == _ORIGIN
    assert sorted(ordered, key=lambda s: s.name) == sorted(stops, key=lambda s: s.name)
    assert path_length_km(ordered) <= path_length_km(stops)


def test_two_opt_improves_a_route_where_nearest_neighbor_is_not_optimal():
    # Desde el origen, el vecino más cercano es "este" (1.0) y obliga a
    # devolverse; el óptimo visita primero el lado oeste.
    origin = Location("o", 0.0, 0.0)
    east = Location("este", 0.0, 1.0)
    west = Location("oeste", 0.0, -1.1)
    far_east = Location("lejos-este", 0.0, 4.0)
    stops = [origin, east, west, far_east]

    greedy = path_length_km(NearestNeighborStrategy().order(stops))
    refined = path_length_km(TwoOptStrategy().order(stops))

    assert refined < greedy


def test_strategies_handle_empty_and_single_stop_lists():
    for strategy in (KeepOrderStrategy(), NearestNeighborStrategy(), TwoOptStrategy()):
        assert strategy.order([]) == []
        assert strategy.order([_ORIGIN]) == [_ORIGIN]


def test_get_strategy_rejects_unknown_name():
    with pytest.raises(ValueError, match="no soportada"):
        get_strategy("recocido_simulado")


def test_planner_delegates_ordering_to_the_injected_strategy():
    class _ReverseTailStrategy(RouteOptimizationStrategy):
        name = "reverse"
        description = "de prueba"

        def order(self, stops):
            return [stops[0], *reversed(stops[1:])]

    planned = RoutePlanner(_ReverseTailStrategy()).plan(["Bucaramanga", "Girón", "Bogotá"])

    assert planned.strategy == "reverse"
    assert planned.stop_names == ("Bucaramanga", "Bogotá", "Girón")
    assert planned.total_distance_km > 0


def test_planner_reports_stops_missing_from_the_catalog():
    with pytest.raises(ValueError, match="Cliente A"):
        RoutePlanner(KeepOrderStrategy()).plan(["Bucaramanga", "Cliente A"])
