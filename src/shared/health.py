"""Utilidades compartidas entre módulos.

Este archivo existe desde el primer commit únicamente para validar que
el pipeline de CI (instalación de dependencias + pytest + cobertura)
funciona correctamente desde el inicio del proyecto.
"""


def system_status() -> dict:
    """Retorna el estado básico del sistema.

    Sirve como smoke test inicial del pipeline de CI/CD.
    """
    return {"status": "ok", "system": "SCM - Cadena de Suministro"}
