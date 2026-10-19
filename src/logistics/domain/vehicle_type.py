from dataclasses import dataclass


@dataclass(frozen=True)
class VehicleType:
    """Flyweight (GoF): estado intrínseco e inmutable de un tipo de vehículo,
    compartido por todas las rutas que lo usan. El estado extrínseco (fecha,
    paradas, distancia) vive en cada DistributionRoute."""

    code: str
    refrigerated: bool = False


class VehicleTypeFactory:
    """Flyweight Factory: entrega siempre la misma instancia para cada tipo
    de vehículo del catálogo. El pool se llena una sola vez al cargar el módulo
    y después solo se lee, por lo que no necesita bloqueo.

    Los códigos fuera del catálogo (strings libres que llegan por la API en
    rutas 'custom') NO se guardan en el pool: si se guardaran, cualquier
    cliente podría hacer crecer la memoria sin límite enviando códigos
    distintos. Para ellos se devuelve una instancia transitoria."""

    _pool: dict[str, VehicleType] = {
        vehicle.code: vehicle
        for vehicle in (
            VehicleType("camion_estandar"),
            VehicleType("moto_express"),
            VehicleType("furgon_refrigerado", refrigerated=True),
        )
    }

    @classmethod
    def get(cls, code: str) -> VehicleType:
        pooled = cls._pool.get(code)
        return pooled if pooled is not None else VehicleType(code)

    @classmethod
    def pool_size(cls) -> int:
        return len(cls._pool)
