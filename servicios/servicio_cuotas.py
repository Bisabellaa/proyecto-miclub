from pathlib import Path
from base_datos.base_datos import (
    conectar,
    listar_cuotas_de_socio,
    pagar_cuota as pagar_cuota_db,
)
from modelo.cuota import Cuota

RUTA_DB = Path(__file__).parent.parent / "club.db"


def listar_cuotas(usuario):
    """Devuelve la lista de Cuota del socio (vacía si no tiene)."""
    conexion = conectar(str(RUTA_DB))
    try:
        return listar_cuotas_de_socio(conexion, usuario)
    finally:
        conexion.close()


def pagar_cuota(usuario, periodo):
    """Paga la cuota del período y devuelve el mensaje de la base tal cual."""
    conexion = conectar(str(RUTA_DB))
    try:
        return pagar_cuota_db(conexion, usuario, periodo)
    finally:
        conexion.close()