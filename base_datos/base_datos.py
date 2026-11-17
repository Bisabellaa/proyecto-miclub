import sqlite3
from datetime import date
from modelo.actividades import Actividad
from modelo.cuota import Cuota
from modelo.socio import Socio
from modelo.club import Club


def conectar(ruta):
    """Abre una conexión a la base de datos en la ruta indicada.
    Si el archivo no existe, lo crea automáticamente."""
    conexion = sqlite3.connect(ruta)
    return conexion

def crear_tablas(conexion):
    """Crea las tablas necesarias si no existen."""
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS socios (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo     TEXT NOT NULL,
            edad                INTEGER,
            tipo_identificacion TEXT,
            identificacion      TEXT,
            nacionalidad        TEXT,
            fecha_inscripcion   TEXT,
            estado              TEXT DEFAULT 'Activo',
            rol                 TEXT DEFAULT 'socio',
            usuario             TEXT UNIQUE NOT NULL,
            contrasenia         TEXT NOT NULL
        )
    """)
    conexion.commit()

    """Crea las tablas necesarias si no existen."""
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cuotas (
            id  INTEGER PRIMARY KEY AUTOINCREMENT,
            socio_id  INTEGER NOT NULL,
            estado TEXT DEFAULT 'pendiente',
            fecha_de_vencimiento TEXT,
            periodo TEXT NOT NULL,
            FOREIGN KEY (socio_id) REFERENCES socios(id)
        )
    """)
    conexion.commit()

    """Crea las tablas necesarias si no existen."""
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clubes (
            club_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            ubicacion TEXT NOT NULL,
            presidente TEXT NOT NULL,
            fecha_fundacion TEXT
        )
    """)
    conexion.commit()

    cursor = conexion.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS actividades(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        dia TEXT NOT NULL,
        horario TEXT NOT NULL
        )
    """)
    conexion.commit()

    cursor = conexion.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS socio_actividad (
        socio_id     INTEGER,
        actividad_id INTEGER,
        PRIMARY KEY (socio_id, actividad_id),
        FOREIGN KEY (socio_id) REFERENCES socios(id),
        FOREIGN KEY (actividad_id) REFERENCES actividades(id)
    )
""")
    conexion.commit()

    cursor = conexion.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS socio_club (
        socio_id INTEGER REFERENCES socios(id),
        club_id  INTEGER REFERENCES clubes(club_id),
        PRIMARY KEY (socio_id, club_id)
    )
""")
    conexion.commit()

    _migrar_actividades(conexion)
    _normalizar_estados(conexion)


def _migrar_actividades(conexion):
    """Si la tabla actividades vieja no tiene columna id, la reconstruye
    conservando sus datos."""
    cursor = conexion.cursor()
    columnas = [fila[1] for fila in cursor.execute("PRAGMA table_info(actividades)")]
    if columnas and "id" not in columnas:
        cursor.execute("ALTER TABLE actividades RENAME TO actividades_vieja")
        cursor.execute("""
            CREATE TABLE actividades(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                dia TEXT NOT NULL,
                horario TEXT NOT NULL
            )
        """)
        cursor.execute("""
            INSERT INTO actividades (nombre, dia, horario)
            SELECT nombre, dia, horario FROM actividades_vieja
        """)
        cursor.execute("DROP TABLE actividades_vieja")
        conexion.commit()


def _normalizar_estados(conexion):
    """Homogeneiza los estados de cuotas guardados en minúscula."""
    cursor = conexion.cursor()
    cursor.execute("UPDATE cuotas SET estado = 'Pendiente' WHERE estado = 'pendiente'")
    cursor.execute("UPDATE cuotas SET estado = 'Pagada' WHERE estado = 'pagada'")
    cursor.execute("UPDATE cuotas SET estado = 'Vencida' WHERE estado = 'vencida'")
    conexion.commit()

def guardar_socio(conexion, socio):
    """Recibe un objeto Socio y lo guarda en la tabla socios."""
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO socios (nombre_completo, edad, tipo_identificacion,
                            identificacion, nacionalidad, fecha_inscripcion,
                            estado, rol, usuario, contrasenia)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        socio.nombre_completo,
        socio.edad,
        socio.get_tipo_identificacion(),
        socio.get_identificacion(),
        socio.get_nacionalidad(),
        socio.fecha_inscripcion.isoformat(),
        socio.estado,
        socio.rol,
        socio.get_usuario(),
        socio.get_contrasenia()
    ))
    conexion.commit()



def guardar_cuota(conexion, socio, cuota):
    cursor = conexion.cursor()
    cursor.execute("SELECT id FROM socios WHERE usuario = ?", (socio.get_usuario(),))
    fila = cursor.fetchone()
    if fila is None:
        return "El socio no existe"

    socio_id = fila[0]

    cursor.execute("""
        INSERT INTO cuotas (socio_id, estado, fecha_de_vencimiento, periodo)
        VALUES (?, ?, ?, ?)
    """, (
        socio_id,
        cuota.get_estado(),
        cuota.fecha_de_vencimiento,
        cuota.periodo
    ))
    conexion.commit()



def listar_cuotas_de_socio(conexion, usuario):
    """Devuelve una lista de objetos Cuota para el socio con ese usuario."""
    cursor = conexion.cursor()

    cursor.execute("SELECT id FROM socios WHERE usuario = ?", (usuario,))
    fila = cursor.fetchone()
    if fila is None:
        return []

    socio_id = fila[0]

    # Traer todas las cuotas de ese socio
    cursor.execute(
        "SELECT periodo, estado, fecha_de_vencimiento FROM cuotas WHERE socio_id = ?",
        (socio_id,)
    )

    cuotas = []
    for periodo, estado, fecha_de_vencimiento in cursor.fetchall():
        cuota = Cuota(estado, fecha_de_vencimiento, periodo)
        cuotas.append(cuota)
    return cuotas


#buscar un socio

def buscar_socio_por_usuario(conexion, usuario):
    """Devuelve el Socio (con sus cuotas cargadas) o None si no existe."""
    cursor = conexion.cursor()
    # Pedimos exactamente las 10 columnas en orden, sin el ID
    cursor.execute("""
        SELECT nombre_completo, edad, tipo_identificacion, identificacion, 
               nacionalidad, fecha_inscripcion, estado, rol, usuario, contrasenia 
        FROM socios 
        WHERE usuario = ?
    """, (usuario,))
    
    fila = cursor.fetchone()
    if fila is None:
        return None
    else:
        return construir_socio(fila)

def construir_socio(fila):
    (nombre_completo, edad, tipo_identificacion, identificacion, nacionalidad, fecha_inscripcion, estado, rol, usuario, contrasenia) = fila
    return Socio(nombre_completo, edad, tipo_identificacion, identificacion, nacionalidad, fecha_inscripcion, estado, rol, usuario, contrasenia)


#guardar club
def guardar_club(conexion, clubes):
    """Guarda el club en la tabla clubes (solo si no existe uno).
    Devuelve el club_id (nuevo o existente)."""
    cursor = conexion.cursor()

    cursor.execute("SELECT club_id FROM clubes")
    fila = cursor.fetchone()
    if fila is not None:
        return fila[0]

    cursor.execute(
        "INSERT INTO clubes (nombre, descripcion,ubicacion, presidente, fecha_fundacion) VALUES (?, ?, ?, ?, ?)",
        (
        clubes.nombre,
        clubes.descripcion,
        clubes.ubicacion,
        clubes.get_presidente(),
        clubes.get_fecha_fundacion()
        ))
    conexion.commit()
    return cursor.lastrowid



def guardar_actividad(conexion, actividad):
    """Guarda una actividad. Si ya existe una con el mismo nombre, no la
    duplica. Devuelve el id de la actividad (nuevo o existente)."""
    cursor = conexion.cursor()

    cursor.execute("SELECT id FROM actividades WHERE nombre = ?", (actividad.nombre,))
    fila = cursor.fetchone()
    if fila is not None:
        return fila[0]

    cursor.execute(
        "INSERT INTO actividades (nombre, dia, horario) VALUES (?,?,?)",
        (
        actividad.nombre,
        actividad.dia,
        actividad.horario
        ))
    conexion.commit()
    return cursor.lastrowid
    

def anotar_socio_actividad(conexion, usuario, nombre_actividad):
    """Anota al socio en la actividad indicada."""
    cursor = conexion.cursor()

    cursor.execute("SELECT id FROM socios WHERE usuario = ?", (usuario,))
    fila = cursor.fetchone()
    if fila is None:
        return "El socio no existe."
    socio_id = fila[0]

    cursor.execute("SELECT id FROM actividades WHERE nombre = ?", (nombre_actividad,))
    fila = cursor.fetchone()
    if fila is None:
        return f"La actividad {nombre_actividad} no existe."
    actividad_id = fila[0]

    cursor.execute(
        "INSERT OR IGNORE INTO socio_actividad (socio_id, actividad_id) VALUES (?, ?)",
        (socio_id, actividad_id)
    )
    conexion.commit()
    return f"Te anotaste en {nombre_actividad}."


def desanotar_socio_actividad(conexion, usuario, nombre_actividad):
    """
    Elimina el vínculo entre un socio y una actividad en la tabla socio_actividad.
    Devuelve True si se eliminó el vínculo, False si no existía.
    """
    cursor = conexion.cursor()

    # Buscar el id del socio por su usuario
    cursor.execute("SELECT id FROM socios WHERE usuario = ?", (usuario,))
    fila_socio = cursor.fetchone()
    if fila_socio is None:
        return False

    # Buscar el id de la actividad por su nombre
    cursor.execute("SELECT id FROM actividades WHERE nombre = ?", (nombre_actividad,))
    fila_actividad = cursor.fetchone()
    if fila_actividad is None:
        return False

    # Eliminar el vínculo en la tabla intermedia
    cursor.execute(
        "DELETE FROM socio_actividad WHERE socio_id = ? AND actividad_id = ?",
        (fila_socio[0], fila_actividad[0]),
    )
    conexion.commit()
    return cursor.rowcount > 0


def listar_actividades_de_socio(conexion, usuario):
    """Devuelve una lista de objetos Actividad a los que está anotado el socio."""
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT a.nombre, a.dia, a.horario FROM actividades a
        JOIN socio_actividad sa ON sa.actividad_id = a.id
        JOIN socios s ON s.id = sa.socio_id
        WHERE s.usuario = ?
    """, (usuario,))

    return [Actividad(nombre, dia, horario)
            for nombre, dia, horario in cursor.fetchall()]


def _obtener_id_socio(conexion, usuario):
    """Devuelve el id del socio o None si no existe."""
    cursor = conexion.cursor()
    cursor.execute("SELECT id FROM socios WHERE usuario = ?", (usuario,))
    fila = cursor.fetchone()
    return fila[0] if fila else None


def anotar_socio_clubes(conexion, usuario, nombre_club):
    """Anota al socio en la actividad indicada."""
    cursor = conexion.cursor()

    cursor.execute("SELECT id FROM socios WHERE usuario = ?", (usuario,))
    fila = cursor.fetchone()
    if fila is None:
        return "El socio no existe."
    socio_id = fila[0]

    cursor.execute("SELECT club_id FROM clubes WHERE nombre = ?", (nombre_club,))
    fila = cursor.fetchone()
    if fila is None:
        return f"El club {nombre_club} no existe."
    club_id = fila[0]

    cursor.execute(
    "INSERT OR IGNORE INTO socio_club (socio_id, club_id) VALUES (?, ?)",
    (socio_id, club_id))
    conexion.commit()
    return f"Te anotaste en {nombre_club}."


    

def listar_clubes_de_socio(conexion, usuario):
    """Devuelve una lista de objetos Club a los que pertenece el socio."""
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT c.nombre, c.descripcion, c.ubicacion, c.presidente, c.fecha_fundacion
        FROM clubes c
        JOIN socio_club sc ON sc.club_id = c.club_id
        JOIN socios s ON s.id = sc.socio_id
        WHERE s.usuario = ?
    """, (usuario,))

    return [Club(nombre, descripcion, ubicacion, presidente, fecha_fundacion)
            for nombre, descripcion, ubicacion, presidente, fecha_fundacion
            in cursor.fetchall()]



def actualizar_estado_socio(conexion, usuario, nuevo_estado):
    """Actualiza el estado ("Activo" o "Suspendido") del socio.
    Devuelve True si se actualizó, False si el socio no existe."""
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE socios SET estado = ? WHERE usuario = ?",
        (nuevo_estado, usuario),
    )
    conexion.commit()
    return cursor.rowcount > 0


def listar_socios(conexion):
    """Devuelve una lista con todos los objetos Socio (vacía si no hay ninguno)."""
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT nombre_completo, edad, tipo_identificacion, identificacion,
               nacionalidad, fecha_inscripcion, estado, rol, usuario, contrasenia
        FROM socios
    """)
    return [construir_socio(fila) for fila in cursor.fetchall()]




def listar_cuotas(conexion, usuario):
    """Devuelve una lista de objetos Cuota del socio (vacía si no tiene)."""
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT c.periodo, c.estado, c.fecha_de_vencimiento
        FROM cuotas c
        JOIN socios s ON s.id = c.socio_id
        WHERE s.usuario = ?
    """, (usuario,))

    return [Cuota(periodo, estado, fecha_de_vencimiento)
            for periodo, estado, fecha_de_vencimiento
            in cursor.fetchall()]



def pagar_cuota(conexion, usuario, periodo):
    """Marca como pagada la cuota del período indicado."""
    cursor = conexion.cursor()

    socio_id = _obtener_id_socio(conexion, usuario)
    if socio_id is None:
        return "El socio no existe."

    cursor.execute(
        "SELECT estado FROM cuotas WHERE socio_id = ? AND periodo = ?",
        (socio_id, periodo)
    )
    fila = cursor.fetchone()
    if fila is None:
        return f"No existe la cuota del período {periodo}."
    if fila[0] == "Pagada":
        return f"La cuota {periodo} ya estaba pagada."

    cursor.execute(
        "UPDATE cuotas SET estado = 'Pagada' WHERE socio_id = ? AND periodo = ?",
        (socio_id, periodo)
    )
    conexion.commit()
    return f"Cuota {periodo} pagada."
