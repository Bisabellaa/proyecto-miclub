"""Pruebas del backend (servicios + base de datos) sobre una BD temporal."""
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from base_datos.base_datos import conectar, crear_tablas, guardar_socio
from modelo.socio import Socio
from modelo.cuota import Cuota
import servicios.servicio_socios as ss
import servicios.servicio_cuotas as sc
import servicios.servicio_autenticacion as sa

DB_TEMP = Path(tempfile.mkdtemp()) / "test.db"

# Redirigir los servicios a la BD temporal
ss.RUTA_DB = DB_TEMP
sc.RUTA_DB = DB_TEMP
sa.RUTA_DB = DB_TEMP

conexion = conectar(str(DB_TEMP))
crear_tablas(conexion)
guardar_socio(conexion, Socio(
    "Ezequiel Vitullo", 28, "DNI", "45908376", "Argentina",
    date(2024, 11, 23), "Activo", "socio", "bubu", "ezebubu"))
guardar_socio(conexion, Socio(
    "Admin Prueba", 40, "DNI", "11111111", "Argentina",
    date(2023, 1, 1), "Activo", "admin", "admin1", "admin123"))
conexion.close()

errores = []

def chequear(nombre, funcion, excepcion_esperada=None):
    try:
        resultado = funcion()
        if excepcion_esperada is not None:
            errores.append(nombre)
            print(f"FALLA - {nombre}: esperaba {excepcion_esperada.__name__} y no ocurrió")
            return None
        print(f"OK   - {nombre}: {resultado!r}")
        return resultado
    except excepcion_esperada as e:
        print(f"OK   - {nombre}: (excepción esperada) {e}")
        return None
    except Exception as e:
        errores.append(nombre)
        print(f"FALLA - {nombre}: {type(e).__name__}: {e}")
        return None

socio = chequear("autenticar(bubu/ezebubu)", lambda: sa.autenticar("bubu", "ezebubu"))
chequear("autenticar clave incorrecta", lambda: sa.autenticar("bubu", "mala"))

socios = chequear("listar_socios", ss.listar_socios)
if socios is not None:
    assert len(socios) == 2, f"esperaba 2 socios, hay {len(socios)}"

chequear("obtener_socio(bubu)", lambda: ss.obtener_socio("bubu"))

# Cuotas: generar una para bubu usando el servicio (debe existir forma)
from base_datos.base_datos import guardar_cuota
c = conectar(str(DB_TEMP))
guardar_cuota(c, sa.autenticar("bubu", "ezebubu"), Cuota("Pendiente", date(2026, 5, 12), "2026-05"))
c.close()

cuotas = chequear("listar_cuotas(bubu)", lambda: sc.listar_cuotas("bubu"))
if cuotas:
    cuota = cuotas[0]
    print("     estado:", cuota.get_estado(), "| periodo:", cuota.periodo,
          "| vencimiento:", cuota.fecha_de_vencimiento)
    chequear("cuota.dias_para_vencimiento()", cuota.dias_para_vencimiento)
    chequear("cuota.actualizar_estado()", cuota.actualizar_estado)

chequear("pagar_cuota(bubu, 2026-05)", lambda: sc.pagar_cuota("bubu", "2026-05"))
chequear("pagar_cuota dos veces", lambda: sc.pagar_cuota("bubu", "2026-05"))

clubes = chequear("listar_clubes_de_socio(bubu)", lambda: ss.listar_clubes_de_socio("bubu"))
if clubes is not None:
    assert isinstance(clubes, list), "debe devolver una lista"

chequear("registrar_socio nuevo", lambda: ss.registrar_socio(
    "Nuevo Socio", 20, "DNI", "22222222", "Argentina", "nuevo1", "clave1"))
chequear("registrar socio duplicado (debe fallar con ValueError)",
         lambda: ss.registrar_socio("Nuevo Socio", 20, "DNI", "22222222",
                                    "Argentina", "nuevo1", "clave1"),
         excepcion_esperada=ValueError)
chequear("suspender_socio(bubu)", lambda: ss.suspender_socio("bubu"))
chequear("reactivar_socio(bubu)", lambda: ss.reactivar_socio("bubu"))

print()
if errores:
    print(f"RESULTADO: {len(errores)} prueba(s) fallaron: {errores}")
    sys.exit(1)
print("RESULTADO: todas las pruebas pasaron")
