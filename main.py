from interfaz.inicio_de_sesion import LoginBocaHandball

if __name__ == "__main__":
    app = LoginBocaHandball()
    app.mainloop()


if __name__ == "__main__":
    try:
        app.mainloop()
    except KeyboardInterrupt:
        print("\nAplicación cerrada por el usuario.")
        


from pathlib import Path

from base_datos.base_datos import conectar, crear_tablas
from interfaz.app import ClubApp

RUTA_BASE = Path(__file__).parent / "club.db"


def main():
    conexion = conectar(str(RUTA_BASE))
    crear_tablas(conexion)
    conexion.close()

    ClubApp().mainloop()


if __name__ == "__main__":
    main()
