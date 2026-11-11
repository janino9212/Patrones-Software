from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.logistics.application.change_route_status import ChangeRouteStatusUseCase, RouteNotFound
from src.logistics.application.create_route import CreateDistributionRouteUseCase
from src.logistics.domain.entities import DistributionRoute
from src.logistics.domain.location_catalog import all_locations
from src.logistics.domain.repository import DistributionRouteRepository
from src.logistics.domain.route_corridor import RouteCorridor
from src.logistics.domain.route_leaf import SingleRoute
from src.logistics.domain.route_optimization import RoutePlanner, available_strategies
from src.logistics.domain.vehicle_type import VehicleTypeFactory
from src.logistics.infrastructure.repository import SqlDistributionRouteRepository
from src.logistics.interfaces.schemas import (
    CompareStrategiesRequest,
    CorridorRequest,
    CorridorResponse,
    CreateRouteRequest,
    LocationResponse,
    RouteResponse,
    RouteStopResponse,
    RouteTransitionRequest,
    StrategyResultResponse,
    VehicleTypeResponse,
)
from src.shared.database import get_db

router = APIRouter(prefix="/logistics", tags=["logistics"])


def _build_use_case(db: Session = Depends(get_db)) -> CreateDistributionRouteUseCase:
    repository = SqlDistributionRouteRepository(db)
    return CreateDistributionRouteUseCase(repository)


@router.post("/routes", response_model=RouteResponse, status_code=status.HTTP_201_CREATED)
def create_route(
    payload: CreateRouteRequest,
    use_case: CreateDistributionRouteUseCase = Depends(_build_use_case),
):
    try:
        route = use_case.execute(
            route_type=payload.route_type,
            stops=payload.stops,
            departure_date=payload.departure_date,
            vehicle_type=payload.vehicle_type,
            total_distance_km=payload.total_distance_km,
            optimization=payload.optimization,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return _to_response(route)


@router.get("/routes/{route_id}", response_model=RouteResponse)
def get_route(route_id: int, db: Session = Depends(get_db)):
    repository = SqlDistributionRouteRepository(db)
    route = repository.get(route_id)
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ruta no encontrada")
    return _to_response(route)


@router.get("/routes", response_model=list[RouteResponse])
def list_routes(db: Session = Depends(get_db)):
    repository = SqlDistributionRouteRepository(db)
    return [_to_response(route) for route in repository.list_all()]


@router.post("/routes/{route_id}/transition", response_model=RouteResponse)
def change_route_status(
    route_id: int, payload: RouteTransitionRequest, db: Session = Depends(get_db)
):
    use_case = ChangeRouteStatusUseCase(SqlDistributionRouteRepository(db))
    try:
        route = use_case.execute(route_id, payload.action)
    except RouteNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        # Incluye InvalidRouteTransition: la acción no aplica al estado actual.
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _to_response(route)


@router.post("/optimizations/compare", response_model=list[StrategyResultResponse])
def compare_strategies(payload: CompareStrategiesRequest):
    """Aplica cada estrategia a las mismas paradas, sin guardar nada."""
    try:
        results = [
            (strategy, RoutePlanner(strategy).plan(payload.stops))
            for strategy in available_strategies()
        ]
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return [
        StrategyResultResponse(
            strategy=strategy.name,
            description=strategy.description,
            stops=list(planned.stop_names),
            total_distance_km=planned.total_distance_km,
        )
        for strategy, planned in results
    ]


@router.get("/locations", response_model=list[LocationResponse])
def list_locations():
    return [
        LocationResponse(name=loc.name, latitude=loc.latitude, longitude=loc.longitude)
        for loc in all_locations()
    ]


@router.get("/vehicle-types", response_model=list[VehicleTypeResponse])
def list_vehicle_types():
    return [
        VehicleTypeResponse(code=vehicle.code, refrigerated=vehicle.refrigerated)
        for vehicle in VehicleTypeFactory.catalog()
    ]


@router.post("/corridors", response_model=CorridorResponse, status_code=status.HTTP_201_CREATED)
def create_corridor(payload: CorridorRequest, db: Session = Depends(get_db)):
    corridor = _build_corridor(payload, SqlDistributionRouteRepository(db))
    return CorridorResponse(
        name=payload.name,
        total_distance_km=corridor.total_distance_km(),
        # Iterator: recorre todas las rutas, incluidas las de sub-corredores.
        routes=[leaf.describe() for leaf in corridor],
    )


def _build_corridor(
    payload: CorridorRequest, repository: DistributionRouteRepository
) -> RouteCorridor:
    corridor = RouteCorridor(payload.name)
    for route_id in payload.route_ids:
        route = repository.get(route_id)
        if route is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"No existe la ruta #{route_id}"
            )
        corridor.add(SingleRoute(route))
    for sub_corridor in payload.sub_corridors:
        corridor.add(_build_corridor(sub_corridor, repository))
    return corridor


def _to_response(route: DistributionRoute) -> RouteResponse:
    return RouteResponse(
        route_id=route.route_id,
        vehicle_type=route.vehicle_type,
        refrigerated=route.vehicle.refrigerated,
        departure_date=route.departure_date,
        stops=[
            RouteStopResponse(sequence=stop.sequence, location=stop.location, notes=stop.notes)
            for stop in route.stops
        ],
        total_distance_km=route.total_distance_km,
        notes=route.notes,
        status=route.status,
        status_label=route.state.label,
        allowed_actions=list(route.state.allowed_actions),
    )
