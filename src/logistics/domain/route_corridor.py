from src.logistics.domain.route_component import RouteComponent


class RouteCorridor(RouteComponent):
    def __init__(self, name: str):
        self._name = name
        self._children: list[RouteComponent] = []

    def add(self, component: RouteComponent) -> None:
        self._children.append(component)

    def total_distance_km(self) -> float:
        total = sum(child.total_distance_km() for child in self._children)
        print(f"[COMPOSITE] Corredor '{self._name}' suma {total} km de {len(self._children)} componentes")
        return total

    def describe(self) -> str:
        return f"Corredor '{self._name}' ({len(self._children)} componentes)"