"""
ui/pages/m1_config.py
======================
Pantalla de configuración para el Modelo M1: Consumo Absoluto.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from ui.theme import COLORS, FONTS, DIMS
from ui.components import SelectorFecha

class M1ConfigPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_topbar()
        self._build_cuerpo()

    def _build_topbar(self):
        topbar = ctk.CTkFrame(
            self, fg_color=COLORS.bg_card,
            corner_radius=0, height=DIMS.topbar_height
        )
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
            topbar, text="Modelo M1: Consumo Absoluto — Configuración",
            font=(FONTS.family, FONTS.size_md, "bold"), text_color=COLORS.primary
        ).grid(row=0, column=1, sticky="w", padx=8)

        ctk.CTkButton(
            topbar, text="🚀 Cargar datos existentes",
            font=(FONTS.family, FONTS.size_sm), fg_color=COLORS.primary,
            text_color=COLORS.text_white, height=32,
            command=lambda: self.app.navegar("m1_carga")
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
        
        # Fuente y Unidad en la misma fila
        fuente_frame = ctk.CTkFrame(card, fg_color="transparent")
        fuente_frame.grid(row=2, column=0, sticky="ew", **pad)
        fuente_frame.grid_columnconfigure((0, 1), weight=1)

        self.entry_fuente = self._entry_with_label(fuente_frame, "Fuente de Energía", "Ej: Electricidad", 0, 0)
        self.entry_unidad = self._entry_with_label(fuente_frame, "Unidad de Medida", "Ej: kWh", 0, 1)

        # 2. Periodo Base
        self._seccion_label(card, "Periodo Base (Histórico)", row=3)
        # _date_range_picker usa row y row+1 (4 y 5)
        self.sel_pb_ini, self.sel_pb_fin, self.lbl_resumen_pb = self._date_range_picker(card, 4)

        # 3. Periodo de Reporte
        self._seccion_label(card, "Periodo de Reporte (Seguimiento)", row=6)
        # _date_range_picker usa row y row+1 (7 y 8)
        self.sel_pr_ini, self.sel_pr_fin, self.lbl_resumen_pr = self._date_range_picker(card, 7)

        # Inicializar resúmenes
        self._actualizar_todos_los_resumenes()

        # Botón Acción
        self._build_botones(scroll)

    def _build_botones(self, parent):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="ew", padx=48, pady=(0, 32))

        ctk.CTkButton(
            btn_frame, text="📥  Confirmar y descargar plantilla M1",
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
        f.grid(row=row, column=col, sticky="ew", padx=4 if col==0 else (4,0))
        f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(f, text=label, font=(FONTS.family, FONTS.size_xs), text_color=COLORS.text_secondary).grid(row=0, column=0, sticky="w")
        e = ctk.CTkEntry(f, placeholder_text=placeholder, height=38, corner_radius=8, fg_color=COLORS.bg_main, border_color=COLORS.border)
        e.grid(row=1, column=0, sticky="ew")
        return e

    def _date_range_picker(self, parent, row):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=0, sticky="ew", padx=DIMS.padding_card, pady=(0, 4))
        f.grid_columnconfigure((0, 1), weight=1)
        
        sel_ini = SelectorFecha(f, label_text="Fecha Inicio", command=self._actualizar_todos_los_resumenes)
        sel_ini.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        
        sel_fin = SelectorFecha(f, label_text="Fecha Fin", command=self._actualizar_todos_los_resumenes)
        sel_fin.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        lbl = ctk.CTkLabel(parent, text="", font=(FONTS.family, FONTS.size_xs, "italic"),
                           text_color=COLORS.success, anchor="w")
        lbl.grid(row=row+1, column=0, sticky="w", padx=DIMS.padding_card, pady=(0, 16))
        
        return sel_ini, sel_fin, lbl

    def _confirmar_y_descargar(self):
        # Lógica de guardado en sesión y llamada a io_excel
        data = {
            "nombre": self.entry_nombre.get().strip(),
            "fuente": self.entry_fuente.get().strip(),
            "unidad": self.entry_unidad.get().strip(),
            "pb_ini": self.sel_pb_ini.get_value(),
            "pb_fin": self.sel_pb_fin.get_value(),
            "pr_ini": self.sel_pr_ini.get_value(),
            "pr_fin": self.sel_pr_fin.get_value(),
        }

        if not data["nombre"] or not data["fuente"] or not data["unidad"]:
            messagebox.showwarning("Campos faltantes", "Por favor completa la identificación del proyecto.")
            return

        # Validar lógica de rangos
        if not self._validar_rango(data["pb_ini"], data["pb_fin"]):
            messagebox.showerror("Rango inválido", "En Periodo Base, la fecha fin debe ser posterior a inicio.")
            return
        if not self._validar_rango(data["pr_ini"], data["pr_fin"]):
            messagebox.showerror("Rango inválido", "En Periodo Reporte, la fecha fin debe ser posterior a inicio.")
            return

        # Guardar en sesión
        self.app.session.update(data)
        
        from core.io_excel import generar_plantilla_m1
        if generar_plantilla_m1(data):
            pass

    def _actualizar_todos_los_resumenes(self):
        self._actualizar_etiqueta_rango(self.sel_pb_ini, self.sel_pb_fin, self.lbl_resumen_pb)
        self._actualizar_etiqueta_rango(self.sel_pr_ini, self.sel_pr_fin, self.lbl_resumen_pr)

    def _actualizar_etiqueta_rango(self, sel_ini, sel_fin, lbl):
        f1 = sel_ini.get_value()
        f2 = sel_fin.get_value()
        try:
            d1 = datetime.strptime(f1, "%m/%Y")
            d2 = datetime.strptime(f2, "%m/%Y")
            meses = (d2.year - d1.year) * 12 + (d2.month - d1.month) + 1
            meses_abr = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
            f1_txt = f"{meses_abr[d1.month-1]}-{d1.year}"
            f2_txt = f"{meses_abr[d2.month-1]}-{d2.year}"
            
            if meses > 0:
                lbl.configure(text=f"✓ {f1_txt} → {f2_txt} ({meses} meses)", text_color=COLORS.success)
            else:
                lbl.configure(text="✕ Rango inválido", text_color=COLORS.danger)
        except: pass

    def _validar_rango(self, f1_str, f2_str):
        try:
            d1 = datetime.strptime(f1_str, "%m/%Y")
            d2 = datetime.strptime(f2_str, "%m/%Y")
            return d2 >= d1
        except: return False
