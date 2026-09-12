from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.logistics.application.create_route import CreateDistributionRouteUseCase
from src.logistics.domain.entities import DistributionRoute
from src.logistics.infrastructure.repository import SqlDistributionRouteRepository
from src.logistics.interfaces.schemas import (
    CreateRouteRequest,
    RouteResponse,
    RouteStopResponse,
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


def _to_response(route: DistributionRoute) -> RouteResponse:
    return RouteResponse(
        route_id=route.route_id,
        vehicle_type=route.vehicle_type,
        departure_date=route.departure_date,
        stops=[
            RouteStopResponse(sequence=stop.sequence, location=stop.location, notes=stop.notes)
            for stop in route.stops
        ],
        total_distance_km=route.total_distance_km,
        notes=route.notes,
    )
