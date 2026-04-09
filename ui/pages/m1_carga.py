"""
ui/pages/m1_carga.py
====================
Pantalla de carga y validación de datos para el Modelo M1.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from ui.theme import COLORS, FONTS, DIMS
import pandas as pd

class M1CargaPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        self.df_base = None
        self.df_monitoreo = None
        self.meta = {}
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

        ctk.CTkFrame(topbar, fg_color=COLORS.accent, height=2).place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        ctk.CTkButton(
            topbar, text="← Configuración", font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent", text_color=COLORS.primary, hover_color=COLORS.bg_main,
            width=120, height=32, command=lambda: self.app.navegar("m1_config")
        ).grid(row=0, column=0, padx=16, pady=8, sticky="w")

        ctk.CTkLabel(
            topbar, text="Modelo M1: Carga de Datos",
            font=(FONTS.family, FONTS.size_md, "bold"), text_color=COLORS.primary
        ).grid(row=0, column=1, sticky="w", padx=8)

    def _build_cuerpo(self):
        self.cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        self.cuerpo.grid(row=1, column=0, sticky="nsew", padx=48, pady=24)
        self.cuerpo.grid_columnconfigure(0, weight=1)

        # ── Zona de Carga ─────────────────────────────────────────────────────
        self.zona_carga = ctk.CTkFrame(self.cuerpo, fg_color=COLORS.bg_card, corner_radius=DIMS.card_radius, border_width=1, border_color=COLORS.border)
        self.zona_carga.grid(row=0, column=0, sticky="ew", pady=(0, 24))
        self.zona_carga.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.zona_carga, text="Selecciona el archivo Excel M1 con tus datos",
            font=(FONTS.family, FONTS.size_sm), text_color=COLORS.text_secondary
        ).pack(pady=(20, 10))

        self.btn_seleccionar = ctk.CTkButton(
            self.zona_carga, text="📂 Seleccionar Archivo",
            font=(FONTS.family, FONTS.size_md, "bold"), fg_color=COLORS.primary,
            height=40, command=self._seleccionar_archivo
        )
        self.btn_seleccionar.pack(pady=(0, 20))

        # ── Zona de Resumen (oculta inicialmente) ─────────────────────────────
        self.zona_resumen = ctk.CTkFrame(self.cuerpo, fg_color="transparent")
        self.zona_resumen.grid_columnconfigure((0, 1), weight=1)

    def _seleccionar_archivo(self):
        path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if not path: return

        from core.io_excel import leer_excel_m1
        df_b, df_m, meta, errores = leer_excel_m1(path)

        if errores:
            messagebox.showerror("Errores en el archivo", "\n".join(errores))
            return

        self.df_base = df_b
        self.df_monitoreo = df_m
        self.meta = meta
        self.app.session["excel_path"] = path
        
        self._mostrar_resumen()

    def _mostrar_resumen(self):
        # Limpiar zona resumen
        for widget in self.zona_resumen.winfo_children(): widget.destroy()
        self.zona_resumen.grid(row=1, column=0, sticky="nsew")

        # Card Info Proyecto
        card_info = ctk.CTkFrame(self.zona_resumen, fg_color=COLORS.bg_card, corner_radius=DIMS.card_radius, border_width=1, border_color=COLORS.border)
        card_info.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        
        ctk.CTkLabel(card_info, text="Información del Proyecto", font=(FONTS.family, FONTS.size_sm, "bold"), text_color=COLORS.primary).pack(pady=10)
        
        info_text = (
            f"📍 Entidad: {self.meta.get('entidad', 'N/A')}\n"
            f"⚡ Fuente: {self.meta.get('fuente', 'N/A')}\n"
            f"📏 Unidad: {self.meta.get('unidad', 'N/A')}\n"
            f"📅 Periodo Base: {self.meta.get('periodo_base_text', 'N/A')}"
        )
        ctk.CTkLabel(card_info, text=info_text, justify="left", font=(FONTS.family, FONTS.size_xs), text_color=COLORS.text_primary).pack(padx=20, pady=(0, 20))

        # Card Estadísticas Datos
        card_stats = ctk.CTkFrame(self.zona_resumen, fg_color=COLORS.bg_card, corner_radius=DIMS.card_radius, border_width=1, border_color=COLORS.border)
        card_stats.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        
        ctk.CTkLabel(card_stats, text="Resumen de Datos", font=(FONTS.family, FONTS.size_sm, "bold"), text_color=COLORS.primary).pack(pady=10)
        
        stats_text = (
            f"📊 Registros Periodo Base: {len(self.df_base)}\n"
            f"📈 Registros Monitoreo: {len(self.df_monitoreo)}\n"
            f"✅ Columnas encontradas: {len(self.df_base.columns)}"
        )
        ctk.CTkLabel(card_stats, text=stats_text, justify="left", font=(FONTS.family, FONTS.size_xs), text_color=COLORS.text_primary).pack(padx=20, pady=(0, 20))

        # Botón Procesar
        ctk.CTkButton(
            self.cuerpo, text="⚙️ Calcular Línea Base y Desempeño",
            font=(FONTS.family, FONTS.size_md, "bold"), fg_color=COLORS.accent,
            text_color=COLORS.primary, height=48, command=self._procesar_m1
        ).grid(row=2, column=0, pady=32)

    def _procesar_m1(self):
        # Guardar en sesión para el siguiente paso
        self.app.session["df_base"] = self.df_base
        self.app.session["df_monitoreo"] = self.df_monitoreo
        self.app.session["meta_m1"] = self.meta
        
        # Navegar a resultados (pendiente crear en Paso 5)
        self.app.navegar("m1_resultados")
