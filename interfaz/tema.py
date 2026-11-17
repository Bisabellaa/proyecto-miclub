"""Constantes de diseño (tema Boca Juniors) compartidas por la interfaz."""
from pathlib import Path

# Colores
PRIMARIO = "#001F3F"        # Azul Boca
PRIMARIO_HOVER = "#003366"
FONDO = "#0A182E"           # Azul oscuro de fondo
PANEL = "#0E2240"
TEXTO = "#E2E8F0"
TEXTO_CLARO = "#FFFFFF"
FILA_PAR = "#13294B"

# Colores de estados
ESTADO_ACTIVO = "#4ADE80"
ESTADO_SUSPENDIDO = "#F87171"
ESTADO_PENDIENTE = "#FBBF24"
ESTADO_VENCIDO = "#F87171"

# Textos institucionales
NOMBRE_CLUB = "Boca Juniors"
LEMA_CLUB = "H A N D B A L L"
SUBTITULO = "Sistema de gestión de socios"
ETIQUETA = "La mitad +1 del corazón"

# Fuentes
FUENTE = ("Arial", 12)
FUENTE_CHICA = ("Arial", 10)
FUENTE_MENU = ("Arial", 11)
FUENTE_NEGRITA = ("Arial", 12, "bold")
FUENTE_SUBTITULO = ("Arial", 16, "bold")
FUENTE_TITULO = ("Arial", 18, "bold")
FUENTE_GRANDE = ("Arial", 28, "bold")
FUENTE_TABLA = ("Arial", 11)

RUTA_LOGO = Path(__file__).parent / "logo.png"


def crear_boton(padre, texto, comando, ancho=25, borde=False):
    """Botón principal del club (color primario, sin relieve)."""
    import tkinter as tk

    return tk.Button(
        padre,
        text=texto,
        command=comando,
        bg=PRIMARIO,
        fg=TEXTO_CLARO,
        font=FUENTE_NEGRITA,
        width=ancho,
        relief="solid" if borde else "flat",
        bd=1 if borde else 0,
        cursor="hand2",
        activebackground=PRIMARIO_HOVER,
        activeforeground=TEXTO_CLARO,
    )


def crear_boton_menu(padre, texto, comando):
    """Botón del menú lateral."""
    import tkinter as tk

    return tk.Button(
        padre,
        text=texto,
        command=comando,
        font=FUENTE_MENU,
        bg=PANEL,
        fg=TEXTO,
        activebackground=PRIMARIO,
        activeforeground=TEXTO_CLARO,
        relief="flat",
        anchor="w",
        padx=20,
        pady=12,
        cursor="hand2",
    )


def estilizar_tablas(ventana):
    """Aplica el tema del club a las tablas (ttk.Treeview)."""
    import tkinter as tk
    from tkinter import ttk

    estilo = ttk.Style(ventana)
    estilo.configure(
        "Club.Treeview",
        background=PANEL,
        fieldbackground=PANEL,
        foreground=TEXTO,
        rowheight=28,
        font=FUENTE_TABLA,
    )
    estilo.configure(
        "Club.Treeview.Heading",
        background=PRIMARIO,
        foreground=TEXTO_CLARO,
        font=FUENTE_NEGRITA,
        relief="flat",
    )
    estilo.map(
        "Club.Treeview",
        background=[("selected", PRIMARIO_HOVER)],
        foreground=[("selected", TEXTO_CLARO)],
    )
