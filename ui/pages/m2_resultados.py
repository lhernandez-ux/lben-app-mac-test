"""
ui/pages/m2_resultados.py
=========================
Dashboard de resultados para el Modelo M2: Cociente de Valores Medidos.
Estética premium unificada con ADN visual LBEn.
"""

import customtkinter as ctk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox
from ui.theme import COLORS, FONTS, DIMS
from core.io_excel import escribir_resultados_m2
from core.models.m2_cociente import calcular_resumen_metricas_m2

class M2ResultadosPage(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS.bg_main, **kwargs)
        self.app = parent
        
        # Recuperar datos de sesión (Usando llaves estandarizadas)
        self.df_lben      = self.app.session.get("df_lben")
        self.df_mon       = self.app.session.get("df_monitoreo")
        self.df_base_raw  = self.app.session.get("df_base_raw")
        self.df_base_f    = self.app.session.get("df_base_final")
        self.df_exc       = self.app.session.get("df_excluidos")
        self.config       = self.app.session

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

        ctk.CTkFrame(topbar, fg_color=COLORS.accent, height=2).place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        ctk.CTkButton(
            topbar, text="« Carga de datos", font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent", text_color=COLORS.primary,
            hover_color=COLORS.bg_main, width=120, height=32,
            command=lambda: self.app.navigate_back("m2_carga") if hasattr(self.app, 'navigate_back') else self.app.navegar("m2_carga")
        ).grid(row=0, column=0, padx=16, pady=8, sticky="w")

        ctk.CTkLabel(
            topbar, text="Modelo M2: Cociente de Valores — Resultados y Seguimiento",
            font=(FONTS.family, FONTS.size_md, "bold"), text_color=COLORS.primary
        ).grid(row=0, column=1, sticky="w", padx=8)

        # Botón Inicio
        ctk.CTkButton(
            topbar, text="🏠 Inicio", font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent", text_color=COLORS.primary,
            hover_color=COLORS.accent, width=80, height=32,
            command=lambda: self.app.navegar("home")
        ).grid(row=0, column=2, padx=16, pady=8, sticky="e")

    def _build_cuerpo(self):
        self.tabs = ctk.CTkTabview(
            self, fg_color="transparent", 
            segmented_button_selected_color=COLORS.primary,
            segmented_button_selected_hover_color=COLORS.primary_dark,
            segmented_button_unselected_color=COLORS.bg_card,
            text_color=COLORS.text_white
        )
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        self.tabs.add("📋 Identificación")
        self.tabs.add("📈 Línea Base")
        self.tabs.add("👁️ Monitoreo")
        self.tabs.add("📊 CUSUM")

        self._render_identificacion_tab()
        self._render_lben_tab()
        self._render_monitoreo_tab()
        self._render_cusum_tab()

    def _render_identificacion_tab(self):
        tab = self.tabs.tab("📋 Identificación")
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        m = calcular_resumen_metricas_m2(self.df_lben, self.df_base_raw)
        
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=20)
        
        self.btn_exportar = ctk.CTkButton(
            btn_frame, text="📥 Descargar Resultados Excel",
            font=(FONTS.family, FONTS.size_md, "bold"),
            fg_color=COLORS.accent, text_color=COLORS.primary,
            height=44, command=self._exportar_excel
        )
        self.btn_exportar.pack(side="left")

        # Tablas de resumen
        self._tabla_simple(scroll, "Ficha Técnica", [
            ("Ubicación / Entidad", self.config.get('nombre', '---')),
            ("Fuente", self.config.get('fuente', '---')),
            ("Unidad", self.config.get('unidad', '---')),
            ("Variable Relevante (X)", self.config.get('var_relevante_nom', '---')),
            ("Área Útil", self.config.get('area', '---')),
        ])

        self._tabla_simple(scroll, "Métricas del Modelo M2", [
            ("N datos usados", f"{m['n_final']}"),
            ("Consumo promedio anual", f"{m['consumo_promedio_anual']:,.2f} kWh"),
            ("Potencial ahorro anual", f"{m['potencial_ahorro_kwh']:,.2f} kWh"),
            ("Ahorro potencial (%)", f"{m['potencial_ahorro_pct']:.1f}%"),
            ("Meta 15% Ley", f"{m['meta_15']:,.2f} kWh"),
        ], pady=(20, 0))

    def _tabla_simple(self, parent, title, rows, pady=0):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=30, pady=pady)
        ctk.CTkLabel(frame, text=title, font=(FONTS.family, 14, "bold"), text_color=COLORS.primary, anchor="w").pack(fill="x", pady=(0, 6))
        card = ctk.CTkFrame(frame, fg_color=COLORS.bg_card, corner_radius=DIMS.card_radius, border_width=1, border_color=COLORS.border)
        card.pack(fill="x")
        for i, (label, val) in enumerate(rows):
            f = ctk.CTkFrame(card, fg_color="transparent", height=32)
            f.pack(fill="x", padx=16, pady=4)
            ctk.CTkLabel(f, text=label, font=(FONTS.family, 11), text_color=COLORS.text_secondary).pack(side="left")
            ctk.CTkLabel(f, text=str(val), font=(FONTS.family, 11, "bold"), text_color=COLORS.text_primary).pack(side="right")

    def _render_lben_tab(self):
        tab = self.tabs.tab("📈 Línea Base")
        fig, ax = plt.subplots(figsize=(9, 4.5), facecolor=COLORS.bg_card)
        ax.set_facecolor("#F8FAF9")
        ax.plot(range(1,13), self.df_lben['lben'], color=COLORS.primary, linewidth=2.5, marker='o', label="LBEn Ratio")
        ax.fill_between(range(1,13), self.df_lben['lim_inf'], self.df_lben['lim_sup'], color=COLORS.primary, alpha=0.15, label="Límites Control")
        ax.set_xticks(range(1,13)); ax.set_xticklabels(["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"])
        ax.legend(); ax.grid(alpha=0.2)
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)

    def _render_monitoreo_tab(self):
        tab = self.tabs.tab("👁️ Monitoreo")
        if self.df_mon is None or self.df_mon.empty: return
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        self._tabla_simple(scroll, "Consumo Real vs LBEn", [
            ("Ahorro Acumulado", f"{self.df_mon['Desemp_kWh'].sum():,.2f} kWh"),
            ("Ahorro Económico", f"{self.df_mon['Desemp_COP'].sum():,.2f} COP"),
            ("Impacto Ambiental", f"{self.df_mon['Desemp_CO2'].sum():,.2f} kgCO2"),
        ], pady=20)

    def _render_cusum_tab(self):
        tab = self.tabs.tab("📊 CUSUM")
        if self.df_mon is None or self.df_mon.empty: return
        fig, ax = plt.subplots(figsize=(9, 4.5), facecolor=COLORS.bg_card)
        ax.set_facecolor("#F8FAF9")
        ax.plot(self.df_mon.index, self.df_mon['CUSUM_kWh'], color=COLORS.primary, linewidth=2, marker='o', label="CUSUM kWh")
        ax.axhline(0, color='black', alpha=0.5); ax.fill_between(self.df_mon.index, self.df_mon['CUSUM_kWh'], 0, where=(self.df_mon['CUSUM_kWh'] < 0), color=COLORS.success, alpha=0.3)
        ax.fill_between(self.df_mon.index, self.df_mon['CUSUM_kWh'], 0, where=(self.df_mon['CUSUM_kWh'] > 0), color=COLORS.danger, alpha=0.3)
        ax.set_title("Evolución de Ahorros Acumulados (kWh)", fontdict={'weight':'bold'})
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)

    def _exportar_excel(self):
        path = self.app.session.get("excel_path")
        if not path: return
        self.btn_exportar.configure(state="disabled", text="ESCRIBIENDO...")
        meta_calc = calcular_resumen_metricas_m2(self.df_lben, self.df_base_raw)
        if escribir_resultados_m2(path, self.df_lben, self.df_mon, self.df_base_f, self.df_exc, meta_calc, self.app.session):
            messagebox.showinfo("Éxito", f"Excel actualizado:\n{path}")
        else: messagebox.showerror("Error", "No se pudo escribir el archivo.")
        self.btn_exportar.configure(state="normal", text="📥 Descargar Resultados Excel")
