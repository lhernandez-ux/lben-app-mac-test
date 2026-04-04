"""
ui/pages/exploratorio_config.py
================================
Pantalla de configuración del análisis exploratorio.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from ui.theme import COLORS, FONTS, DIMS


class ExploratorioConfigPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        self.vars_independientes = []  # lista de CTkEntry dinámicas
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_topbar()
        self._build_cuerpo()

    # ── Topbar ────────────────────────────────────────────────────────────────
    def _build_topbar(self):
        topbar = ctk.CTkFrame(
            self, fg_color=COLORS.bg_card,
            corner_radius=0, height=DIMS.topbar_height
        )
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)

        # Línea acento inferior
        ctk.CTkFrame(
            topbar, fg_color=COLORS.accent,
            height=2, corner_radius=0
        ).place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        # Botón regresar
        ctk.CTkButton(
            topbar,
            text="← Inicio",
            font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent",
            text_color=COLORS.primary,
            hover_color=COLORS.bg_main,
            width=90, height=32,
            corner_radius=DIMS.button_radius,
            command=lambda: self.app.navegar("home")
        ).grid(row=0, column=0, padx=16, pady=8, sticky="w")

        # Título
        ctk.CTkLabel(
            topbar,
            text="Análisis Exploratorio — Nuevo Proyecto",
            font=(FONTS.family, FONTS.size_md, "bold"),
            text_color=COLORS.primary
        ).grid(row=0, column=1, sticky="w", padx=8)

        # Botón ya tengo archivo
        ctk.CTkButton(
            topbar,
            text="🚀 Ya tengo archivo → Cargar datos",
            font=(FONTS.family, FONTS.size_sm),
            fg_color=COLORS.primary,
            text_color=COLORS.text_white,
            hover_color=COLORS.primary_dark,
            corner_radius=DIMS.button_radius,
            height=32,
            command=lambda: self.app.navegar("exploratorio_carga")
        ).grid(row=0, column=2, padx=16, pady=8, sticky="e")

    # ── Cuerpo scrollable ─────────────────────────────────────────────────────
    def _build_cuerpo(self):
        scroll = ctk.CTkScrollableFrame(
            self, fg_color=COLORS.bg_main, corner_radius=0
        )
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # Card principal
        card = ctk.CTkFrame(
            scroll, fg_color=COLORS.bg_card,
            corner_radius=DIMS.card_radius,
            border_width=1, border_color=COLORS.border
        )
        card.grid(row=0, column=0, padx=48, pady=24, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        pad = {"padx": DIMS.padding_card, "pady": (0, 16)}

        # ── Nombre del proyecto ───────────────────────────────────────────────
        self._seccion_label(card, "Nombre del proyecto")
        self.entry_nombre = self._entry(
            card, placeholder="Ej: Edificio Central — 2024"
        )
        self.entry_nombre.grid(row=2, column=0, sticky="ew", **pad)

        # ── Periodo de análisis ───────────────────────────────────────────────
        self._seccion_label(card, "Periodo de análisis", row=3)

        fechas_frame = ctk.CTkFrame(card, fg_color="transparent")
        fechas_frame.grid(row=4, column=0, sticky="ew", **pad)
        fechas_frame.grid_columnconfigure((0, 1), weight=1)

        # Fecha inicio
        fi_frame = ctk.CTkFrame(fechas_frame, fg_color="transparent")
        fi_frame.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        fi_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            fi_frame, text="Fecha inicio (MM/AAAA)",
            font=(FONTS.family, FONTS.size_xs),
            text_color=COLORS.text_secondary, anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.entry_fecha_ini = self._entry(
            fi_frame, placeholder="Ej: 01/2022"
        )
        self.entry_fecha_ini.grid(row=1, column=0, sticky="ew")

        # Fecha fin
        ff_frame = ctk.CTkFrame(fechas_frame, fg_color="transparent")
        ff_frame.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        ff_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            ff_frame, text="Fecha fin (MM/AAAA)",
            font=(FONTS.family, FONTS.size_xs),
            text_color=COLORS.text_secondary, anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.entry_fecha_fin = self._entry(
            ff_frame, placeholder="Ej: 12/2024"
        )
        self.entry_fecha_fin.grid(row=1, column=0, sticky="ew")

        # ── Variable dependiente ──────────────────────────────────────────────
        self._seccion_label(card, "Variable dependiente (consumo)", row=5)

        ctk.CTkLabel(
            card,
            text="Debe coincidir exactamente con el encabezado en la factura.",
            font=(FONTS.family, FONTS.size_xs),
            text_color=COLORS.text_secondary, anchor="w"
        ).grid(row=6, column=0, sticky="w", padx=DIMS.padding_card, pady=(0, 4))

        self.entry_var_dep = self._entry(
            card, placeholder="Ej: Consumo_kWh"
        )
        self.entry_var_dep.grid(row=7, column=0, sticky="ew", **pad)

        # ── Variables independientes ──────────────────────────────────────────
        self._seccion_label(card, "Variables independientes", row=8)

        ctk.CTkLabel(
            card,
            text="Agrega todas las variables que creas que pueden influir "
                 "en el consumo (Ej: Temperatura, Producción).",
            font=(FONTS.family, FONTS.size_xs),
            text_color=COLORS.text_secondary, anchor="w",
            wraplength=700, justify="left"
        ).grid(row=9, column=0, sticky="w",
               padx=DIMS.padding_card, pady=(0, 8))

        # Frame dinámico para variables
        self.vars_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.vars_frame.grid(row=10, column=0, sticky="ew",
                             padx=DIMS.padding_card, pady=(0, 8))
        self.vars_frame.grid_columnconfigure(0, weight=1)

        # Primera variable por defecto
        self._agregar_variable()

        # Botón agregar variable
        ctk.CTkButton(
            card,
            text="+ Agregar variable candidata",
            font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent",
            text_color=COLORS.primary,
            hover_color=COLORS.bg_main,
            border_width=1,
            border_color=COLORS.primary,
            corner_radius=DIMS.button_radius,
            height=32,
            command=self._agregar_variable
        ).grid(row=11, column=0, sticky="w",
               padx=DIMS.padding_card, pady=(0, 20))

        # ── Botones de acción ─────────────────────────────────────────────────
        self._build_botones(scroll)

    def _build_botones(self, parent):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="ew", padx=48, pady=(0, 32))
        btn_frame.grid_columnconfigure(1, weight=1)

        # Confirmar + Descargar plantilla
        ctk.CTkButton(
            btn_frame,
            text="📥  Confirmar y descargar plantilla",
            font=(FONTS.family, FONTS.size_md, "bold"),
            fg_color=COLORS.accent,
            text_color=COLORS.primary,
            hover_color="#D4E800",
            corner_radius=DIMS.button_radius,
            height=44,
            command=self._confirmar_y_descargar
        ).grid(row=0, column=0, sticky="w")

    # ── Helpers UI ────────────────────────────────────────────────────────────
    def _seccion_label(self, parent, texto, row=0):
        ctk.CTkLabel(
            parent, text=texto,
            font=(FONTS.family, FONTS.size_sm, "bold"),
            text_color=COLORS.primary, anchor="w"
        ).grid(row=row, column=0, sticky="w",
               padx=DIMS.padding_card, pady=(16, 4))

    def _entry(self, parent, placeholder=""):
        return ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            font=(FONTS.family, FONTS.size_sm),
            fg_color=COLORS.bg_main,
            border_color=COLORS.border,
            text_color=COLORS.text_primary,
            height=38,
            corner_radius=8
        )

    def _agregar_variable(self):
        idx = len(self.vars_independientes) + 1
        fila = ctk.CTkFrame(self.vars_frame, fg_color="transparent")
        fila.grid(row=idx - 1, column=0, sticky="ew", pady=4)
        fila.grid_columnconfigure(0, weight=1)

        entry = ctk.CTkEntry(
            fila,
            placeholder_text=f"Variable {idx} (Ej: Temperatura_C)",
            font=(FONTS.family, FONTS.size_sm),
            fg_color=COLORS.bg_main,
            border_color=COLORS.border,
            text_color=COLORS.text_primary,
            height=38,
            corner_radius=8
        )
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        # Botón eliminar (solo si no es la primera)
        if idx > 1:
            ctk.CTkButton(
                fila,
                text="✕",
                font=(FONTS.family, FONTS.size_sm),
                fg_color=COLORS.danger,
                text_color="white",
                hover_color="#C0392B",
                width=36, height=38,
                corner_radius=8,
                command=lambda f=fila, e=entry: self._eliminar_variable(f, e)
            ).grid(row=0, column=1)

        self.vars_independientes.append(entry)

    def _eliminar_variable(self, fila, entry):
        self.vars_independientes.remove(entry)
        fila.destroy()

    # ── Lógica de confirmación ────────────────────────────────────────────────
    def _confirmar_y_descargar(self):
        nombre    = self.entry_nombre.get().strip()
        fecha_ini = self.entry_fecha_ini.get().strip()
        fecha_fin = self.entry_fecha_fin.get().strip()
        var_dep   = self.entry_var_dep.get().strip()
        vars_ind  = [e.get().strip() for e in self.vars_independientes
                     if e.get().strip()]

        # Validaciones
        if not nombre:
            messagebox.showwarning("Campo requerido",
                                   "Ingresa el nombre del proyecto.")
            return
        if not fecha_ini or not fecha_fin:
            messagebox.showwarning("Campo requerido",
                                   "Ingresa las fechas de inicio y fin.")
            return
        if not self._validar_fecha(fecha_ini) or \
           not self._validar_fecha(fecha_fin):
            messagebox.showerror("Formato incorrecto",
                                 "Las fechas deben tener formato MM/AAAA.\n"
                                 "Ejemplo: 01/2022")
            return
        if not var_dep:
            messagebox.showwarning("Campo requerido",
                                   "Ingresa el nombre de la variable dependiente.")
            return
        if not vars_ind:
            messagebox.showwarning("Campo requerido",
                                   "Agrega al menos una variable independiente.")
            return

        # Guardar en sesión
        self.app.session["proyecto_nombre"]    = nombre
        self.app.session["fecha_inicio"]       = fecha_ini
        self.app.session["fecha_fin"]          = fecha_fin
        self.app.session["var_dependiente"]    = var_dep
        self.app.session["vars_independientes"] = vars_ind

        # Generar y descargar plantilla
        from core.io_excel import generar_plantilla_exploratoria
        generar_plantilla_exploratoria(
            nombre_proyecto = nombre,
            fecha_ini       = fecha_ini,
            fecha_fin       = fecha_fin,
            var_dep         = var_dep,
            vars_ind        = vars_ind
        )

    def _validar_fecha(self, fecha_str: str) -> bool:
        try:
            datetime.strptime(fecha_str, "%m/%Y")
            return True
        except ValueError:
            return False