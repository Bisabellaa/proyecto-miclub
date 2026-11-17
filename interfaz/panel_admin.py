import tkinter as tk
from tkinter import messagebox, ttk

from interfaz.tema import (
    ESTADO_ACTIVO,
    ESTADO_SUSPENDIDO,
    FILA_PAR,
    FUENTE,
    FUENTE_CHICA,
    FUENTE_NEGRITA,
    FUENTE_TITULO,
    PANEL,
    PRIMARIO,
    TEXTO,
    crear_boton,
    crear_boton_menu,
    estilizar_tablas,
)
from servicios.servicio_cuotas import listar_cuotas
from servicios.servicio_socios import (
    listar_socios,
    reactivar_socio,
    registrar_socio,
    suspender_socio,
)

CAMPOS_REGISTRO = [
    ("Nombre completo *", "nombre", ""),
    ("Edad", "edad", ""),
    ("Tipo de identificación", "tipo_identificacion", ""),
    ("Identificación *", "identificacion", ""),
    ("Nacionalidad", "nacionalidad", ""),
    ("Usuario único *", "usuario", ""),
    ("Contraseña *", "contrasenia", "*"),
]


class PanelAdmin(tk.Toplevel):
    """Ventana de administración que se abre sobre el login."""

    def __init__(self, master, socio):
        super().__init__(master)
        self.usuario = socio.get_usuario()
        self._usuarios = []

        self.title("Boca Juniors - Handball | Panel de Administración")
        self.geometry("900x620")
        self.minsize(820, 560)
        self.configure(bg=PANEL)
        estilizar_tablas(self)

        self._crear_menu()
        self.contenido = tk.Frame(self, bg=PANEL)
        self.contenido.pack(side="right", fill="both", expand=True, padx=12, pady=12)

        self.mostrar_inicio()

    def _crear_menu(self):
        self.menu = tk.Frame(self, bg=PANEL, width=210)
        self.menu.pack(side="left", fill="y")
        self.menu.pack_propagate(False)

        tk.Label(
            self.menu,
            text="MENÚ ADMIN",
            font=FUENTE_NEGRITA,
            bg=PANEL,
            fg=PRIMARIO,
        ).pack(pady=(25, 15))

        for texto, comando in self.botones_menu():
            crear_boton_menu(self.menu, texto, comando).pack(fill="x", padx=8, pady=3)

    def _refrescar_menu(self):
        for elemento in self.menu.winfo_children()[1:]:
            elemento.destroy()
        for texto, comando in self.botones_menu():
            crear_boton_menu(self.menu, texto, comando).pack(fill="x", padx=8, pady=3)

    def botones_menu(self):
        return [
            ("Inicio", self.mostrar_inicio),
            ("Socios", self.mostrar_socios),
            ("Registrar socio", self.mostrar_registro),
            ("Cerrar sesión", self.cerrar_sesion),
        ]

    def cerrar_sesion(self):
        self.master.al_cerrar_panel(self)

    def _limpiar(self):
        for elemento in self.contenido.winfo_children():
            elemento.destroy()

    def _crear_titulo(self, texto):
        tk.Label(
            self.contenido,
            text=texto,
            font=FUENTE_TITULO,
            bg=PANEL,
            fg=PRIMARIO,
        ).pack(pady=(15, 10))

    # ── Pantallas ──────────────────────────────────────────────

    def mostrar_inicio(self):
        self._limpiar()
        self._crear_titulo("PANEL DE ADMINISTRACIÓN")

        socios = listar_socios()
        activos = [s for s in socios if s.estado == "Activo"]
        suspendidos = [s for s in socios if s.estado == "Suspendido"]

        tarjeta = tk.Frame(self.contenido, bg=PANEL)
        tarjeta.pack(pady=20)

        self._crear_tarjeta(tarjeta, "Socios registrados", str(len(socios)),
                            PRIMARIO).grid(row=0, column=0, padx=12)

        self._crear_tarjeta(tarjeta, "Activos", str(len(activos)),
                            ESTADO_ACTIVO).grid(row=0, column=1, padx=12)

        self._crear_tarjeta(tarjeta, "Suspendidos", str(len(suspendidos)),
                            ESTADO_SUSPENDIDO).grid(row=0, column=2, padx=12)

        tk.Label(
            self.contenido,
            text=f"Sesión de {self.usuario}. Desde el menú podés gestionar los socios.",
            font=FUENTE,
            bg=PANEL,
            fg=TEXTO,
        ).pack(pady=15)

    def _crear_tarjeta(self, padre, titulo, valor, color):
        tarjeta = tk.Frame(padre, bg=PANEL, highlightbackground=FILA_PAR,
                           highlightthickness=1)
        tk.Label(
            tarjeta,
            text=str(valor),
            font=("Arial", 26, "bold"),
            bg=PANEL,
            fg=color,
        ).pack(padx=30, pady=(18, 2))
        tk.Label(
            tarjeta,
            text=titulo,
            font=FUENTE_CHICA,
            bg=PANEL,
            fg=TEXTO,
        ).pack(padx=30, pady=(0, 18))
        return tarjeta

    def mostrar_socios(self):
        self._limpiar()
        self._crear_titulo("SOCIOS DEL CLUB")

        columnas = ("usuario", "nombre", "estado", "inscripcion", "pendientes")
        tabla = ttk.Treeview(
            self.contenido,
            columns=columnas,
            show="headings",
            style="Club.Treeview",
            height=12,
        )
        tabla.heading("usuario", text="Usuario")
        tabla.heading("nombre", text="Nombre")
        tabla.heading("estado", text="Estado")
        tabla.heading("inscripcion", text="Inscripción")
        tabla.heading("pendientes", text="Cuotas pendientes")
        tabla.column("usuario", width=130, anchor="w")
        tabla.column("nombre", width=220, anchor="w")
        tabla.column("estado", width=110, anchor="center")
        tabla.column("inscripcion", width=130, anchor="center")
        tabla.column("pendientes", width=140, anchor="center")

        tabla.tag_configure("par", background=FILA_PAR)
        tabla.tag_configure("impar", background=PANEL)
        tabla.tag_configure("Activo", foreground=ESTADO_ACTIVO)
        tabla.tag_configure("Suspendido", foreground=ESTADO_SUSPENDIDO)
        tabla.pack(fill="both", expand=True, padx=30, pady=(5, 10))

        fila_botones = tk.Frame(self.contenido, bg=PANEL)
        fila_botones.pack(pady=(0, 10))

        crear_boton(
            fila_botones,
            "SUSPENDER",
            lambda: self._cambiar_estado(tabla, suspender_socio),
            ancho=14,
        ).pack(side="left", padx=6)

        crear_boton(
            fila_botones,
            "REACTIVAR",
            lambda: self._cambiar_estado(tabla, reactivar_socio),
            ancho=14,
        ).pack(side="left", padx=6)

        self._cargar_socios(tabla)

    def _cargar_socios(self, tabla):
        for fila in tabla.get_children():
            tabla.delete(fila)
        self._usuarios = []

        socios = listar_socios()

        if not socios:
            tk.Label(
                self.contenido,
                text="No hay socios registrados",
                font=FUENTE,
                bg=PANEL,
                fg=TEXTO,
            ).pack()
            return

        for indice, socio in enumerate(socios):
            pendientes = [
                cuota for cuota in listar_cuotas(socio.get_usuario())
                if cuota.get_estado() in ("Pendiente", "Vencida")
            ]
            rayado = "par" if indice % 2 == 0 else "impar"
            tabla.insert(
                "",
                "end",
                values=(
                    socio.get_usuario(),
                    socio.nombre_completo,
                    socio.estado,
                    socio.fecha_inscripcion,
                    len(pendientes),
                ),
                tags=(rayado, socio.estado),
            )
            self._usuarios.append(socio.get_usuario())

    def _usuario_seleccionado(self, tabla):
        seleccion = tabla.selection()
        if not seleccion or not self._usuarios:
            messagebox.showwarning("Aviso", "Seleccioná un socio primero.")
            return None
        return self._usuarios[tabla.index(seleccion[0])]

    def _cambiar_estado(self, tabla, servicio):
        usuario = self._usuario_seleccionado(tabla)
        if usuario is None:
            return

        mensaje = servicio(usuario)
        messagebox.showinfo("Gestión de socios", mensaje)
        self.mostrar_socios()

    def mostrar_registro(self):
        self._limpiar()
        self._crear_titulo("REGISTRAR NUEVO SOCIO")

        tk.Label(
            self.contenido,
            text="Los campos marcados con * son obligatorios. "
                 "El socio se crea con estado Activo.",
            font=FUENTE_CHICA,
            bg=PANEL,
            fg=TEXTO,
        ).pack()

        formulario = tk.Frame(self.contenido, bg=PANEL)
        formulario.pack(pady=15)

        campos = {}
        for fila, (etiqueta, clave, ocultar) in enumerate(CAMPOS_REGISTRO):
            tk.Label(
                formulario,
                text=f"{etiqueta}:",
                font=FUENTE_NEGRITA,
                bg=PANEL,
                fg=TEXTO,
            ).grid(row=fila, column=0, sticky="e", padx=(0, 12), pady=5)

            entrada = tk.Entry(
                formulario,
                font=FUENTE,
                width=26,
                show=ocultar,
            )
            entrada.grid(row=fila, column=1, pady=5)
            campos[clave] = entrada

        crear_boton(
            self.contenido,
            "GUARDAR SOCIO",
            lambda: self._guardar(campos),
            ancho=22,
        ).pack(pady=(5, 10))

    def _guardar(self, campos):
        try:
            socio = registrar_socio(
                campos["nombre"].get(),
                campos["edad"].get(),
                campos["tipo_identificacion"].get(),
                campos["identificacion"].get(),
                campos["nacionalidad"].get(),
                campos["usuario"].get(),
                campos["contrasenia"].get(),
            )
        except ValueError as error:
            messagebox.showerror("Datos inválidos", str(error))
            return

        messagebox.showinfo(
            "Registrar socio",
            f"El socio '{socio.get_usuario()}' se registró correctamente.",
        )
        self.mostrar_socios()
