"""
ui/pages/m1_resultados.py
=========================
Visualización de resultados del Modelo M1: Consumo Absoluto.
Incluye Ficha Técnica, LBEn Mensual, Desempeño y Seguimiento.
"""

import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from ui.theme import COLORS, FONTS, DIMS
from core.io_excel import escribir_resultados_m1 

class M1ResultadosPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        
        # Recuperar datos de sesión
        self.df_lben    = self.app.session.get("df_lben")
        self.df_mon     = self.app.session.get("df_monitoreo")
        self.df_base    = self.app.session.get("df_base_raw")
        self.df_base_f  = self.app.session.get("df_base_final")
        self.df_excl    = self.app.session.get("df_excluidos")
        self.metricas   = self.app.session.get("metricas_m1")
        self.config     = {
            "nombre": self.app.session.get("nombre", "Proyecto sin nombre"),
            "fuente": self.app.session.get("fuente", "N/A"),
            "unidad": self.app.session.get("unidad", "kWh"),
            "pb_ini": self.app.session.get("pb_ini"),
            "pb_fin": self.app.session.get("pb_fin")
        }

        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self._build_topbar()
        self._build_header_stats()
        self._build_tabs()

    def _build_topbar(self):
        topbar = ctk.CTkFrame(self, fg_color=COLORS.bg_card, corner_radius=0, height=DIMS.topbar_height)
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)

        ctk.CTkFrame(topbar, fg_color=COLORS.accent, height=2).place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        ctk.CTkButton(
            topbar, text="← Volver a Carga", font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent", text_color=COLORS.primary, hover_color=COLORS.bg_main,
            width=120, height=32, command=lambda: self.app.navegar("m1_carga")
        ).grid(row=0, column=0, padx=16, pady=8, sticky="w")

        ctk.CTkLabel(
            topbar, text=f"M1: {self.config['nombre']}",
            font=(FONTS.family, FONTS.size_md, "bold"), text_color=COLORS.primary
        ).grid(row=0, column=1, sticky="w", padx=8)

        ctk.CTkButton(
            topbar, text="💾 Generar Informe Final (Excel)",
            font=(FONTS.family, FONTS.size_sm, "bold"), fg_color=COLORS.primary,
            text_color="white", height=32, command=self._guardar_excel
        ).grid(row=0, column=2, padx=16, pady=8, sticky="e")

    def _build_header_stats(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(20, 0))
        frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._kpi_card(frame, 0, "Consumo Promedio Anual", 
                      f"{self.metricas['consumo_promedio_anual']:,.0f}", self.config['unidad'])
        
        self._kpi_card(frame, 1, "Potencial de Ahorro", 
                      f"{self.metricas['potencial_ahorro_pct']:.1f}%", "Anual", color=COLORS.success)
        
        self._kpi_card(frame, 2, "Fiabilidad de los Datos", 
                      f"{self.metricas['fiabilidad']:.1f}%", "Basado en Res. 016")

    def _kpi_card(self, parent, col, title, value, unit, color=None):
        c = ctk.CTkFrame(parent, fg_color=COLORS.bg_card, corner_radius=12, border_width=1, border_color=COLORS.border)
        c.grid(row=0, column=col, padx=10, sticky="nsew")
        
        ctk.CTkLabel(c, text=title, font=(FONTS.family, 12), text_color=COLORS.text_secondary).pack(pady=(15, 0))
        v_lbl = ctk.CTkLabel(c, text=value, font=(FONTS.family, 28, "bold"), text_color=color if color else COLORS.primary)
        v_lbl.pack(pady=(5, 0))
        ctk.CTkLabel(c, text=unit, font=(FONTS.family, 10, "bold"), text_color=COLORS.text_secondary).pack(pady=(0, 15))

    def _build_tabs(self):
        self.tabs = ctk.CTkTabview(
            self, fg_color=COLORS.bg_main, segmented_button_fg_color=COLORS.border,
            segmented_button_selected_color=COLORS.primary,
            segmented_button_selected_hover_color=COLORS.primary_dark,
            text_color=COLORS.primary
        )
        self.tabs.grid(row=2, column=0, sticky="nsew", padx=20, pady=20)
        
        self.tabs.add("📈 Línea Base (LBEn)")
        self.tabs.add("📊 Desempeño")
        self.tabs.add("📋 Tabla de Seguimiento")
        self.tabs.add("🛠️ Ajuste NR y Calidad")

        self._render_lben_tab()
        self._render_desempeno_tab()
        self._render_seguimiento_tab()
        self._render_ajuste_tab()

    def _render_lben_tab(self):
        tab = self.tabs.tab("📈 Línea Base (LBEn)")
        fig, ax = plt.subplots(figsize=(10, 5), facecolor=COLORS.bg_main)
        ax.set_facecolor("#F8FAF9")
        meses = self.df_lben['mes']
        valores = self.df_lben['lben']
        yerr = [valores - self.df_lben['lim_inf'], self.df_lben['lim_sup'] - valores]
        ax.bar(meses, valores, color=COLORS.primary, alpha=0.6, label="LBEn Mensual")
        ax.errorbar(meses, valores, yerr=yerr, fmt='none', ecolor=COLORS.danger, capsize=5)
        ax.step(meses, self.df_lben['min_hist'], where='mid', color=COLORS.success, linewidth=2, linestyle='--')
        ax.set_title(f"LBEn Mensual — {self.config['unidad']}", fontweight='bold')
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _render_desempeno_tab(self):
        tab = self.tabs.tab("📊 Desempeño")
        if self.df_mon is None or self.df_mon.empty: return
        fig, ax = plt.subplots(figsize=(10, 5), facecolor=COLORS.bg_main)
        ax.set_facecolor("#F8FAF9")
        ax.plot(self.df_mon['Fecha'], self.df_mon['LBEn_Mes'], label="Meta", color=COLORS.primary, linestyle='--')
        ax.plot(self.df_mon['Fecha'], self.df_mon['Ajustado'], label="Real (Adj)", color=COLORS.accent, marker='o')
        ax.legend()
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _render_seguimiento_tab(self):
        tab = self.tabs.tab("📋 Tabla de Seguimiento")
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        if self.df_mon is None: return
        headers = ["Fecha", "Real (Adj)", "LBEn", "Desv (kWh)", "Desv (%)"]
        h_frame = ctk.CTkFrame(scroll, fg_color=COLORS.primary); h_frame.pack(fill="x", pady=5)
        for i, h in enumerate(headers): ctk.CTkLabel(h_frame, text=h, text_color="white", width=120).grid(row=0, column=i)
        for _, row in self.df_mon.iterrows():
            f_frame = ctk.CTkFrame(scroll, fg_color=COLORS.bg_card); f_frame.pack(fill="x", pady=1)
            ctk.CTkLabel(f_frame, text=row['Fecha'], width=120).grid(row=0, column=0)
            ctk.CTkLabel(f_frame, text=f"{row['Ajustado']:,.1f}", width=120).grid(row=0, column=1)
            ctk.CTkLabel(f_frame, text=f"{row['LBEn_Mes']:,.1f}", width=120).grid(row=0, column=2)
            ctk.CTkLabel(f_frame, text=f"{row['Desemp_kWh']:,.1f}", width=120, text_color=COLORS.success if row['Desemp_kWh']<=0 else COLORS.danger).grid(row=0, column=3)
            ctk.CTkLabel(f_frame, text=f"{row['Desemp_Pct']:.1f}%", width=120).grid(row=0, column=4)

    def _render_ajuste_tab(self):
        tab = self.tabs.tab("🛠️ Ajuste NR y Calidad")
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent"); scroll.pack(fill="both", expand=True)
        ajustes = self.df_base[self.df_base.iloc[:, 5].astype(str).str.upper() == 'SI'] if self.df_base is not None else []
        if len(ajustes) == 0:
            ctk.CTkLabel(scroll, text="No hay ajustes NR en periodo base.").pack(pady=20)
        else:
            for _, row in ajustes.iterrows():
                ctk.CTkLabel(scroll, text=f"• {row['Fecha']}: Ajustado proporcionalmente", anchor="w").pack(fill="x", padx=40)

    def _guardar_excel(self):
        path = self.app.session.get("excel_path")
        # Llamar a la función actualizada con todos los parámetros
        ok = escribir_resultados_m1(
            path=path, 
            df_lben=self.df_lben, 
            df_mon=self.df_mon, 
            df_base_f=self.df_base_f,
            df_excluidos=self.df_excl,
            meta=self.metricas, 
            config=self.config
        )
        if ok: messagebox.showinfo("Éxito", f"Reporte guardado en:\n{path}")
        else: messagebox.showerror("Error", "No se pudo guardar el archivo.")
