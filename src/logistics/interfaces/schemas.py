from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class CreateRouteRequest(BaseModel):
    route_type: Literal["standard", "express", "custom"]
    stops: list[str] = Field(min_length=2)
    departure_date: date

    # Solo obligatorio si route_type == "custom"; "standard"/"express" lo
    # deciden el Director.
    vehicle_type: str | None = None
    total_distance_km: float | None = None


class RouteStopResponse(BaseModel):
    sequence: int
    location: str
    notes: str | None = None


class RouteResponse(BaseModel):
    route_id: int
    vehicle_type: str
    departure_date: date
    stops: list[RouteStopResponse]
    total_distance_km: float | None = None
    notes: str | None = None
