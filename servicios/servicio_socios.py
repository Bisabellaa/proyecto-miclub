from datetime import date
from pathlib import Path

from base_datos.base_datos import (
    actualizar_estado_socio,
    buscar_socio_por_usuario,
    conectar,
    guardar_socio,
    listar_clubes_de_socio as listar_clubes_en_bd,
    listar_socios as listar_clubes_en_bd,
)
from modelo.socio import Socio

RUTA_DB = Path(__file__).parent.parent / "club.db"



def listar_socios():
    conexion = conectar(str(RUTA_DB))
    try:
        return None
    finally:
        conexion.close()



def listar_clubes_de_socio(usuario):
    conexion = conectar(str(RUTA_DB))
    try:
        return listar_clubes_en_bd(conexion, usuario)
    finally:
        conexion.close()


def registrar_socio(nombre, edad, tipo_identificacion, identificacion,
                    nacionalidad, usuario, contrasenia):
    """Valida y guarda un socio nuevo. Devuelve el Socio creado."""
    conexion = conectar(str(RUTA_DB))
    try:
        # 1) Validar primero
        if not nombre or not usuario or not contrasenia:
            raise ValueError("Nombre, usuario y contraseña son obligatorios.")
        if edad <= 0:
            raise ValueError("La edad debe ser mayor a 0.")
        if buscar_socio_por_usuario(conexion, usuario) is not None:
            raise ValueError(f"El usuario '{usuario}' ya existe.")

        # 2) Guardar al final
        socio = Socio(nombre, edad, tipo_identificacion, identificacion,
                      nacionalidad, date.today(), "Activo", "socio",
                      usuario, contrasenia)
        guardar_socio(conexion, socio)
        return socio
    finally:
        conexion.close()



def suspender_socio(usuario):
    """Suspende al socio. Devuelve True si se suspendió, False si no existe
    o ya estaba suspendido."""
    conexion = conectar(str(RUTA_DB))
    try:
        socio = buscar_socio_por_usuario(conexion, usuario)
        if socio is None:
            return False
        if not socio.suspender():
            return False
        actualizar_estado_socio(conexion, usuario, socio.estado)
        return True
    finally:
        conexion.close()


def reactivar_socio(usuario):
    """Reactiva al socio. Devuelve True si se reactivó, False si no existe
    o ya estaba activo."""
    conexion = conectar(str(RUTA_DB))
    try:
        socio = buscar_socio_por_usuario(conexion, usuario)
        if socio is None:
            return False
        if not socio.reactivar():
            return False
        actualizar_estado_socio(conexion, usuario, socio.estado)
        return True
    finally:
        conexion.close()
    