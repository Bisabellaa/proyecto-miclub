from datetime import date
from pathlib import Path
from modelo.socio import Socio
from base_datos.base_datos import (
    listar_cuotas_de_socio,
)

RUTA_DB = Path(__file__).parent.parent / "club.db"

def listar_cuotas(usuario):
    """Devuelve la lista de Cuota del socio (vacía si no tiene)."""
    conexion = conectar(str(RUTA_DB))
    try:
        return listar_cuotas_de_socio(conexion, usuario)
    finally:
        conexion.close()