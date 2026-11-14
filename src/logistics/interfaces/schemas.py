from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints, model_validator

_MAX_STOPS = 25
_MAX_CORRIDOR_ITEMS = 50
_MAX_CORRIDOR_DEPTH = 4
# Topes sobre el árbol completo de un corredor, no solo por nivel.
_MAX_CORRIDOR_NODES = 30
_MAX_CORRIDOR_ROUTES = 200
_MAX_DISTANCE_KM = 100_000

StopName = Annotated[str, StringConstraints(min_length=1, max_length=120)]


class CreateRouteRequest(BaseModel):
    route_type: Literal["standard", "express", "custom"]
    stops: list[StopName] = Field(min_length=2, max_length=_MAX_STOPS)
    departure_date: date

    # Solo obligatorio si route_type == "custom"; "standard"/"express" lo
    # deciden el Director.
    vehicle_type: str | None = Field(default=None, max_length=50)
    total_distance_km: float | None = Field(
        default=None, ge=0, le=_MAX_DISTANCE_KM, allow_inf_nan=False
    )

    # Strategy: algoritmo para ordenar las paradas. Con uno distinto de
    # "none", todas las paradas deben pertenecer al catálogo de ubicaciones.
    optimization: Literal["none", "nearest_neighbor", "two_opt"] = "none"


class RouteStopResponse(BaseModel):
    sequence: int
    location: str
    notes: str | None = None


class RouteResponse(BaseModel):
    route_id: int
    vehicle_type: str
    refrigerated: bool = False
    departure_date: date
    stops: list[RouteStopResponse]
    total_distance_km: float | None = None
    notes: str | None = None
    status: str = "planned"
    status_label: str = "planificada"
    allowed_actions: list[str] = []


class RouteTransitionRequest(BaseModel):
    action: Literal["dispatch", "deliver", "cancel"]


class CompareStrategiesRequest(BaseModel):
    stops: list[StopName] = Field(min_length=2, max_length=_MAX_STOPS)


class StrategyResultResponse(BaseModel):
    strategy: str
    description: str
    stops: list[str]
    total_distance_km: float


class LocationResponse(BaseModel):
    name: str
    latitude: float
    longitude: float


class VehicleTypeResponse(BaseModel):
    code: str
    refrigerated: bool


class CorridorRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    route_ids: list[int] = Field(default_factory=list, max_length=_MAX_CORRIDOR_ITEMS)
    # Composite: un corredor puede contener otros corredores.
    sub_corridors: list["CorridorRequest"] = Field(
        default_factory=list, max_length=_MAX_CORRIDOR_ITEMS
    )

    @model_validator(mode="after")
    def _has_content(self) -> "CorridorRequest":
        if not self.route_ids and not self.sub_corridors:
            raise ValueError("Un corredor necesita al menos una ruta o un sub-corredor")
        return self

    def depth(self) -> int:
        return 1 + max((child.depth() for child in self.sub_corridors), default=0)

    def node_count(self) -> int:
        return 1 + sum(child.node_count() for child in self.sub_corridors)

    def all_route_ids(self) -> list[int]:
        """Los ids de este corredor y de todos sus sub-corredores."""
        nested = [rid for child in self.sub_corridors for rid in child.all_route_ids()]
        return [*self.route_ids, *nested]

    @model_validator(mode="after")
    def _tree_is_bounded(self) -> "CorridorRequest":
        if self.depth() > _MAX_CORRIDOR_DEPTH:
            raise ValueError(
                f"Un corredor admite como máximo {_MAX_CORRIDOR_DEPTH} niveles de anidación"
            )
        if self.node_count() > _MAX_CORRIDOR_NODES:
            raise ValueError(
                f"Un corredor admite como máximo {_MAX_CORRIDOR_NODES} corredores en total"
            )
        route_ids = self.all_route_ids()
        if len(route_ids) > _MAX_CORRIDOR_ROUTES:
            raise ValueError(
                f"Un corredor admite como máximo {_MAX_CORRIDOR_ROUTES} rutas en total"
            )
        if len(set(route_ids)) != len(route_ids):
            raise ValueError("Una ruta no puede aparecer más de una vez en el corredor")
        return self


class CorridorResponse(BaseModel):
    name: str
    total_distance_km: float
    routes: list[str]
