from typing import Protocol

from src.tracking.domain.entities import TrackingEvent


class TrackingEventRepository(Protocol):
    """Puerto (hexagonal): lo que la capa de aplicación necesita para
    persistir/consultar eventos, sin saber cómo se implementa."""

    def save(self, event: TrackingEvent) -> TrackingEvent: ...

    def list_by_product(self, product_id: str) -> list[TrackingEvent]: ...
