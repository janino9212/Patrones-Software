from datetime import date

from src.logistics.domain.route_builder import RouteBuilder

_STANDARD_VEHICLE = "camion_estandar"
_EXPRESS_VEHICLE = "moto_express"
_EXPRESS_NOTES = "Ruta express: prioridad alta, sin paradas intermedias de carga"


class RouteDirector:
    """Director (GoF): conoce 'recetas' de construcción estándar (rutas
    estándar vs. express) y las reproduce usando cualquier RouteBuilder,
    sin acoplarse a su clase concreta. Configura el builder y lo devuelve
    -- quien lo llama decide cuándo invocar build() (por si necesita
    agregar más partes opcionales antes de cerrar la construcción)."""

    @staticmethod
    def configure_standard_route(
        builder: RouteBuilder, stops: list[str], departure_date: date
    ) -> RouteBuilder:
        builder.set_vehicle(_STANDARD_VEHICLE).set_departure_date(departure_date)
        for stop in stops:
            builder.add_stop(stop)
        return builder

    @staticmethod
    def configure_express_route(
        builder: RouteBuilder, stops: list[str], departure_date: date
    ) -> RouteBuilder:
        builder.set_vehicle(_EXPRESS_VEHICLE).set_departure_date(departure_date).set_notes(
            _EXPRESS_NOTES
        )
        for stop in stops:
            builder.add_stop(stop)
        return builder
