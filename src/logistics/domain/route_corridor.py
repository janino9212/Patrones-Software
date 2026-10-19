import logging

from src.logistics.domain.route_component import RouteComponent

logger = logging.getLogger("scm.logistics.composite")


class RouteCorridor(RouteComponent):
    def __init__(self, name: str):
        self._name = name
        self._children: list[RouteComponent] = []

    def add(self, component: RouteComponent) -> None:
        self._children.append(component)

    def total_distance_km(self) -> float:
        total = sum(child.total_distance_km() for child in self._children)
        logger.info(
            "[COMPOSITE] Corredor '%s' suma %s km de %d componentes",
            self._name, total, len(self._children),
        )
        return total

    def describe(self) -> str:
        return f"Corredor '{self._name}' ({len(self._children)} componentes)"
