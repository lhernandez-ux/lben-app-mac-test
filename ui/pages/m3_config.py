"""
ui/pages/m3_config.py
======================
Pantalla de configuración para el Modelo M3: Regresión Multivariable.
ADN idéntico a M1 + selector dinámico de variables (igual que exploratorio).
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from ui.theme import COLORS, FONTS, DIMS
from ui.components import SelectorFecha

MAX_VARS = 5

class M3ConfigPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        self.vars_independientes = []  # lista de CTkEntry dinámicas (igual que exploratorio)
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

        # Línea de acento inferior
        ctk.CTkFrame(topbar, fg_color=COLORS.accent, height=2).place(
            relx=0, rely=1.0, relwidth=1.0, anchor="sw"
        )

        ctk.CTkButton(
            topbar, text="← Inicio",
            font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent", text_color=COLORS.primary,
            hover_color=COLORS.bg_main, width=90, height=32,
            command=lambda: self.app.navegar("home")
        ).grid(row=0, column=0, padx=16, pady=8, sticky="w")

        ctk.CTkLabel(
            topbar,
            text="Modelo M3: Regresión Multivariable — Configuración",
            font=(FONTS.family, FONTS.size_md, "bold"),
            text_color=COLORS.primary
        ).grid(row=0, column=1, sticky="w", padx=8)

        ctk.CTkButton(
            topbar, text="🚀 Ir a carga de datos",
            font=(FONTS.family, FONTS.size_sm),
            fg_color=COLORS.primary, text_color=COLORS.text_white,
            height=32, command=self._guardar_y_cargar
        ).grid(row=0, column=2, padx=16, pady=8, sticky="e")

    # ── Cuerpo ────────────────────────────────────────────────────────────────
    def _build_cuerpo(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS.bg_main, corner_radius=0)
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            scroll, fg_color=COLORS.bg_card,
            corner_radius=DIMS.card_radius,
            border_width=1, border_color=COLORS.border
        )
        card.grid(row=0, column=0, padx=48, pady=24, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        pad = {"padx": DIMS.padding_card, "pady": (0, 16)}

        # ── 1. Identificación ─────────────────────────────────────────────────
        self._seccion_label(card, "Identificación del Proyecto")
        self.entry_nombre = self._entry(card, "Nombre de la Entidad / Edificio / Proceso", row=1)

        fuente_frame = ctk.CTkFrame(card, fg_color="transparent")
        fuente_frame.grid(row=2, column=0, sticky="ew", **pad)
        fuente_frame.grid_columnconfigure((0, 1), weight=1)

        self.entry_fuente = self._entry_with_label(fuente_frame, "Fuente de Energía", "Ej: Electricidad", 0, 0)
        self.sel_unidad = self._option_menu_with_label(fuente_frame, "Unidad de Medida", ["kWh", "MWh", "GJ", "MMBTU"], 0, 1)

        self.sel_zona = self._option_menu_with_label(
            fuente_frame, "Zona Climática", ["Cálida", "Templada", "Fría"], 1, 0
        )
        # Área útil con "No disponible" por defecto (igual que M1 y M2)
        self.entry_area = self._entry_with_label(fuente_frame, "Área útil (m2)", "No disponible", 1, 1)
        self.entry_area.insert(0, "No disponible")

        # ── 2. Periodo Base ───────────────────────────────────────────────────
        self._seccion_label(card, "Periodo Base (Histórico)", row=3)
        self.sel_pb_ini, self.sel_pb_fin, self.lbl_resumen_pb = self._date_range_picker(card, 4)

        # ── 3. Periodo de Reporte ─────────────────────────────────────────────
        self._seccion_label(card, "Periodo de Reporte (Seguimiento)", row=6)
        f_mon = ctk.CTkFrame(card, fg_color="transparent")
        f_mon.grid(row=7, column=0, sticky="ew", padx=DIMS.padding_card, pady=(0, 4))
        self.sel_pr_ini = SelectorFecha(
            f_mon, label_text="Fecha Inicio de Seguimiento",
            command=self._actualizar_todos_los_resumenes
        )
        self.sel_pr_ini.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            card,
            text="✓ La plantilla se generará automáticamente hasta Diciembre 2050",
            font=(FONTS.family, FONTS.size_xs, "italic"),
            text_color=COLORS.success
        ).grid(row=8, column=0, sticky="w", padx=DIMS.padding_card, pady=(0, 16))

        # ── 4. Variables Independientes (selector dinámico como exploratorio) ─
        self._seccion_label(card, "Variables Independientes", row=9)

        ctk.CTkLabel(
            card,
            text="Agrega todas las variables que creas que pueden influir en el consumo "
                 "(Ej: Temperatura, Producción). Máximo 5.",
            font=(FONTS.family, FONTS.size_xs),
            text_color=COLORS.text_secondary,
            anchor="w", wraplength=700, justify="left"
        ).grid(row=10, column=0, sticky="w", padx=DIMS.padding_card, pady=(0, 4))

        # Frame dinámico para variables
        self.vars_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.vars_frame.grid(row=11, column=0, sticky="ew", padx=DIMS.padding_card, pady=0)
        self.vars_frame.grid_columnconfigure(0, weight=1)

        # Primera variable por defecto (igual que exploratorio)
        self._agregar_variable()

        # Botón + Agregar
        self.btn_agregar = ctk.CTkButton(
            card,
            text="+ Agregar variable independiente",
            font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent", text_color=COLORS.primary,
            hover_color=COLORS.bg_main,
            border_width=1, border_color=COLORS.primary,
            corner_radius=DIMS.button_radius,
            height=32,
            command=self._agregar_variable
        )
        self.btn_agregar.grid(row=12, column=0, sticky="w", padx=DIMS.padding_card, pady=(8, 20))

        # Inicializar resúmenes de fecha
        self._actualizar_todos_los_resumenes()

        # ── Botón principal ───────────────────────────────────────────────────
        self._build_botones(scroll)

    def _build_botones(self, parent):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="ew", padx=48, pady=(0, 32))

        ctk.CTkButton(
            btn_frame,
            text="📥  Confirmar y descargar plantilla M3",
            font=(FONTS.family, FONTS.size_md, "bold"),
            fg_color=COLORS.accent, text_color=COLORS.primary,
            height=44, command=self._confirmar_y_descargar
        ).pack(side="left")

    # ── Helpers UI ────────────────────────────────────────────────────────────
    def _seccion_label(self, parent, texto, row=0):
        ctk.CTkLabel(
            parent, text=texto,
            font=(FONTS.family, FONTS.size_sm, "bold"),
            text_color=COLORS.primary, anchor="w"
        ).grid(row=row, column=0, sticky="w", padx=DIMS.padding_card, pady=(16, 4))

    def _entry(self, parent, placeholder, row):
        e = ctk.CTkEntry(
            parent, placeholder_text=placeholder,
            font=(FONTS.family, FONTS.size_sm),
            fg_color=COLORS.bg_main, border_color=COLORS.border,
            height=38, corner_radius=8
        )
        e.grid(row=row, column=0, sticky="ew", padx=DIMS.padding_card, pady=(0, 16))
        return e

    def _entry_with_label(self, parent, label, placeholder, row, col):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=col, sticky="ew",
               padx=4 if col == 0 else (4, 0), pady=(0, 16))
        f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            f, text=label,
            font=(FONTS.family, FONTS.size_xs),
            text_color=COLORS.text_secondary
        ).grid(row=0, column=0, sticky="w")
        e = ctk.CTkEntry(
            f, placeholder_text=placeholder,
            height=38, corner_radius=8,
            fg_color=COLORS.bg_main, border_color=COLORS.border
        )
        e.grid(row=1, column=0, sticky="ew")
        return e

    def _option_menu_with_label(self, parent, label, options, row, col):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=col, sticky="ew",
               padx=4 if col == 0 else (4, 0), pady=(0, 16))
        f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            f, text=label,
            font=(FONTS.family, FONTS.size_xs),
            text_color=COLORS.text_secondary
        ).grid(row=0, column=0, sticky="w")
        m = ctk.CTkOptionMenu(
            f, values=options, height=38, corner_radius=8,
            fg_color=COLORS.bg_main,
            button_color=COLORS.primary,
            button_hover_color=COLORS.accent,
            text_color=COLORS.primary,
            dropdown_fg_color=COLORS.bg_card
        )
        m.grid(row=1, column=0, sticky="ew")
        return m

    def _date_range_picker(self, parent, row):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=0, sticky="ew", padx=DIMS.padding_card, pady=(0, 4))
        f.grid_columnconfigure((0, 1), weight=1)

        sel_ini = SelectorFecha(f, label_text="Fecha Inicio",
                                command=self._actualizar_todos_los_resumenes)
        sel_ini.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        sel_fin = SelectorFecha(f, label_text="Fecha Fin",
                                command=self._actualizar_todos_los_resumenes)
        sel_fin.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        lbl = ctk.CTkLabel(
            parent, text="",
            font=(FONTS.family, FONTS.size_xs, "italic"),
            text_color=COLORS.success, anchor="w"
        )
        lbl.grid(row=row + 1, column=0, sticky="w", padx=DIMS.padding_card, pady=(0, 16))
        return sel_ini, sel_fin, lbl

    # ── Selector dinámico de variables (idéntico a exploratorio) ──────────────
    def _agregar_variable(self):
        if len(self.vars_independientes) >= MAX_VARS:
            messagebox.showinfo(
                "Límite alcanzado",
                f"El modelo admite un máximo de {MAX_VARS} variables independientes."
            )
            return

        idx = len(self.vars_independientes) + 1
        fila = ctk.CTkFrame(self.vars_frame, fg_color="transparent")
        fila.grid(row=idx - 1, column=0, sticky="ew", pady=4)
        fila.grid_columnconfigure(0, weight=1)

        entry = ctk.CTkEntry(
            fila,
            placeholder_text=f"Variable {idx} (Ej: Temperatura_C)",
            font=(FONTS.family, FONTS.size_sm),
            fg_color=COLORS.bg_main, border_color=COLORS.border,
            text_color=COLORS.text_primary,
            height=38, corner_radius=8
        )
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        # Botón ✕ rojo (igual que en exploratorio)
        ctk.CTkButton(
            fila, text="✕",
            font=(FONTS.family, FONTS.size_sm),
            fg_color=COLORS.danger, text_color="white",
            hover_color="#C0392B",
            width=36, height=38, corner_radius=8,
            command=lambda fl=fila, en=entry: self._eliminar_variable(fl, en)
        ).grid(row=0, column=1)

        self.vars_independientes.append(entry)

    def _eliminar_variable(self, fila, entry):
        self.vars_independientes.remove(entry)
        fila.destroy()

    # ── Lógica ────────────────────────────────────────────────────────────────
    def _actualizar_todos_los_resumenes(self):
        f1 = self.sel_pb_ini.get_value()
        f2 = self.sel_pb_fin.get_value()
        try:
            d1 = datetime.strptime(f1, "%m/%Y")
            d2 = datetime.strptime(f2, "%m/%Y")
            meses = (d2.year - d1.year) * 12 + (d2.month - d1.month) + 1
            meses_abr = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]
            if meses > 0:
                self.lbl_resumen_pb.configure(
                    text=f"✓ {meses_abr[d1.month-1]}-{d1.year} → {meses_abr[d2.month-1]}-{d2.year} ({meses} meses)",
                    text_color=COLORS.success
                )
            else:
                self.lbl_resumen_pb.configure(
                    text="✕ Fecha fin debe ser posterior al inicio",
                    text_color=COLORS.danger
                )
        except:
            pass

    def _guardar_y_cargar(self):
        self._confirmar_y_descargar(auto=True)
        self.app.navegar("m3_carga")

    def _confirmar_y_descargar(self, auto=False):
        vars_ind = [e.get().strip() for e in self.vars_independientes if e.get().strip()]

        data = {
            "nombre":  self.entry_nombre.get().strip(),
            "fuente":  self.entry_fuente.get().strip(),
            "unidad": self.sel_unidad.get(),
            "zona":    self.sel_zona.get(),
            "area":    self.entry_area.get().strip() or "No disponible",
            "pb_ini":  self.sel_pb_ini.get_value(),
            "pb_fin":  self.sel_pb_fin.get_value(),
            "pr_ini":  self.sel_pr_ini.get_value(),
            "vars_ind": vars_ind
        }

        self.app.session["m3_config"] = data
        if auto:
            return

        if not data["nombre"]:
            messagebox.showwarning("Campo requerido", "Ingresa el nombre del proyecto.")
            return
        if not vars_ind:
            messagebox.showwarning("Campo requerido", "Agrega al menos una variable independiente.")
            return

        from core.io_excel import generar_plantilla_m3
        generar_plantilla_m3(data)
