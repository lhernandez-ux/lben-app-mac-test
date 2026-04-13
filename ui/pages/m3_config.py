"""
ui/pages/m3_config.py
======================
Pantalla de configuración para el Modelo M3: Regresión Multivariable.
ADN Identico a M1.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from ui.theme import COLORS, FONTS, DIMS
from ui.components import SelectorFecha

class M3ConfigPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        self._vars_entries = [] # Para los nombres de variables
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_topbar()
        self._build_cuerpo()

    def _build_topbar(self):
        topbar = ctk.CTkFrame(self, fg_color=COLORS.bg_card, corner_radius=0, height=DIMS.topbar_height)
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)

        # Línea de acento
        ctk.CTkFrame(topbar, fg_color=COLORS.accent, height=2).place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        ctk.CTkButton(
            topbar, text="← Inicio", font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent", text_color=COLORS.primary,
            hover_color=COLORS.bg_main, width=90, height=32,
            command=lambda: self.app.navegar("home")
        ).grid(row=0, column=0, padx=16, pady=8, sticky="w")

        ctk.CTkLabel(
            topbar, text="Modelo M3: Regresión Multivariable — Configuración",
            font=(FONTS.family, FONTS.size_md, "bold"), text_color=COLORS.primary
        ).grid(row=0, column=1, sticky="w", padx=8)

        ctk.CTkButton(
            topbar, text="🚀 Ir a carga de datos",
            font=(FONTS.family, FONTS.size_sm), fg_color=COLORS.primary,
            text_color=COLORS.text_white, height=32,
            command=self._guardar_y_cargar
        ).grid(row=0, column=2, padx=16, pady=8, sticky="e")

    def _build_cuerpo(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS.bg_main, corner_radius=0)
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            scroll, fg_color=COLORS.bg_card, corner_radius=DIMS.card_radius,
            border_width=1, border_color=COLORS.border
        )
        card.grid(row=0, column=0, padx=48, pady=24, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        pad = {"padx": DIMS.padding_card, "pady": (0, 16)}

        # 1. Identificación
        self._seccion_label(card, "Identificación del Proyecto")
        self.entry_nombre = self._entry(card, "Nombre de la Entidad / Edificio / Proceso", row=1)
        
        fuente_frame = ctk.CTkFrame(card, fg_color="transparent")
        fuente_frame.grid(row=2, column=0, sticky="ew", **pad)
        fuente_frame.grid_columnconfigure((0, 1), weight=1)

        self.entry_fuente = self._entry_with_label(fuente_frame, "Fuente de Energía", "Ej: Electricidad", 0, 0)
        self.entry_unidad = self._entry_with_label(fuente_frame, "Unidad de Medida", "Ej: kWh", 0, 1)
        
        self.sel_zona = self._option_menu_with_label(fuente_frame, "Zona Climática", ["Cálida", "Templada", "Fría"], 1, 0)
        self.entry_area = self._entry_with_label(fuente_frame, "Área útil (m2)", "Ej: 1500", 1, 1)

        # 2. Periodo Base
        self._seccion_label(card, "Periodo Base (Histórico)", row=3)
        self.sel_pb_ini, self.sel_pb_fin, self.lbl_resumen_pb = self._date_range_picker(card, 4)

        # 3. Periodo de Reporte
        self._seccion_label(card, "Periodo de Reporte (Seguimiento)", row=6)
        f_mon = ctk.CTkFrame(card, fg_color="transparent")
        f_mon.grid(row=7, column=0, sticky="ew", padx=DIMS.padding_card, pady=(0, 4))
        self.sel_pr_ini = SelectorFecha(f_mon, label_text="Fecha Inicio de Seguimiento", command=self._actualizar_todos_los_resumenes)
        self.sel_pr_ini.grid(row=0, column=0, sticky="ew")

        # 4. Variables Independientes (ESPECÍFICO M3)
        self._seccion_label(card, "Variables Independientes (hasta 5)", row=9)
        vars_f = ctk.CTkFrame(card, fg_color="transparent")
        vars_f.grid(row=10, column=0, sticky="ew", padx=DIMS.padding_card, pady=(0, 16))
        vars_f.grid_columnconfigure((0, 1), weight=1)

        for i in range(5):
            e = ctk.CTkEntry(vars_f, placeholder_text=f"Nombre Variable {i+1}", height=38, corner_radius=8,
                             fg_color=COLORS.bg_main, border_color=COLORS.border)
            e.grid(row=i//2, column=i%2, sticky="ew", padx=4, pady=4)
            self._vars_entries.append(e)

        # Inicializar resúmenes
        self._actualizar_todos_los_resumenes()

        # Botón Acción
        self._build_botones(scroll)

    def _build_botones(self, parent):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="ew", padx=48, pady=(0, 32))

        ctk.CTkButton(
            btn_frame, text="📥  Confirmar y descargar plantilla M3",
            font=(FONTS.family, FONTS.size_md, "bold"),
            fg_color=COLORS.accent, text_color=COLORS.primary,
            height=44, command=self._confirmar_y_descargar
        ).pack(side="left")

    # --- Helpers ---
    def _seccion_label(self, parent, texto, row=0):
        ctk.CTkLabel(
            parent, text=texto, font=(FONTS.family, FONTS.size_sm, "bold"),
            text_color=COLORS.primary, anchor="w"
        ).grid(row=row, column=0, sticky="w", padx=DIMS.padding_card, pady=(16, 4))

    def _entry(self, parent, placeholder, row):
        e = ctk.CTkEntry(parent, placeholder_text=placeholder, font=(FONTS.family, FONTS.size_sm),
                         fg_color=COLORS.bg_main, border_color=COLORS.border, height=38, corner_radius=8)
        e.grid(row=row, column=0, sticky="ew", padx=DIMS.padding_card, pady=(0, 16))
        return e

    def _entry_with_label(self, parent, label, placeholder, row, col):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=col, sticky="ew", padx=4 if col==0 else (4,0), pady=(0, 16))
        f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(f, text=label, font=(FONTS.family, FONTS.size_xs), text_color=COLORS.text_secondary).grid(row=0, column=0, sticky="w")
        e = ctk.CTkEntry(f, placeholder_text=placeholder, height=38, corner_radius=8, fg_color=COLORS.bg_main, border_color=COLORS.border)
        e.grid(row=1, column=0, sticky="ew")
        return e

    def _option_menu_with_label(self, parent, label, options, row, col):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=col, sticky="ew", padx=4 if col==0 else (4,0), pady=(0, 16))
        f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(f, text=label, font=(FONTS.family, FONTS.size_xs), text_color=COLORS.text_secondary).grid(row=0, column=0, sticky="w")
        m = ctk.CTkOptionMenu(f, values=options, height=38, corner_radius=8, fg_color=COLORS.bg_main,
                               button_color=COLORS.primary, button_hover_color=COLORS.accent, text_color=COLORS.primary, dropdown_fg_color=COLORS.bg_card)
        m.grid(row=1, column=0, sticky="ew")
        return m

    def _date_range_picker(self, parent, row):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=0, sticky="ew", padx=DIMS.padding_card, pady=(0, 4))
        f.grid_columnconfigure((0, 1), weight=1)
        sel_ini = SelectorFecha(f, label_text="Fecha Inicio", command=self._actualizar_todos_los_resumenes)
        sel_ini.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        sel_fin = SelectorFecha(f, label_text="Fecha Fin", command=self._actualizar_todos_los_resumenes)
        sel_fin.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        lbl = ctk.CTkLabel(parent, text="", font=(FONTS.family, FONTS.size_xs, "italic"), text_color=COLORS.success, anchor="w")
        lbl.grid(row=row+1, column=0, sticky="w", padx=DIMS.padding_card, pady=(0, 16))
        return sel_ini, sel_fin, lbl

    def _actualizar_todos_los_resumenes(self):
        f1, f2 = self.sel_pb_ini.get_value(), self.sel_pb_fin.get_value()
        try:
            d1, d2 = datetime.strptime(f1, "%m/%Y"), datetime.strptime(f2, "%m/%Y")
            meses = (d2.year - d1.year) * 12 + (d2.month - d1.month) + 1
            if meses > 0: self.lbl_resumen_pb.configure(text=f"✓ Rango: {meses} meses seleccionados.", text_color=COLORS.success)
            else: self.lbl_resumen_pb.configure(text="✕ Fecha fin debe ser posterior a inicio.", text_color=COLORS.danger)
        except: pass

    def _guardar_y_cargar(self):
        self._confirmar_y_descargar(auto=True)
        self.app.navegar("m3_carga")

    def _confirmar_y_descargar(self, auto=False):
        vars_raw = [e.get().strip() for e in self._vars_entries]
        vars_ind = [v for v in vars_raw if v]
        
        data = {
            "nombre": self.entry_nombre.get().strip(),
            "fuente": self.entry_fuente.get().strip(),
            "unidad": self.entry_unidad.get().strip(),
            "zona": self.sel_zona.get(),
            "area": self.entry_area.get().strip(),
            "pb_ini": self.sel_pb_ini.get_value(),
            "pb_fin": self.sel_pb_fin.get_value(),
            "pr_ini": self.sel_pr_ini.get_value(),
            "vars_ind": vars_ind
        }

        self.app.session["m3_config"] = data
        if auto: return

        if not data["nombre"] or not vars_ind:
            messagebox.showwarning("Faltan datos", "Completa el nombre y al menos una variable independiente.")
            return

        from core.io_excel import generar_plantilla_m3
        if generar_plantilla_m3(data):
            pass
