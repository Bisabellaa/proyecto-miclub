from pathlib import Path

from base_datos.base_datos import conectar, crear_tablas
from interfaz.inicio_de_sesion import LoginBocaHandball

RUTA_DB = Path(__file__).parent / "club.db"


def main():
    # Garantiza que las tablas existan (y aplica migraciones) antes del login
    conexion = conectar(str(RUTA_DB))
    crear_tablas(conexion)
    conexion.close()

    app = LoginBocaHandball()
    app.mainloop()


if __name__ == "__main__":
    main()
