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
import webbrowser
import os
import plotly.graph_objects as go
import numpy as np

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
            "zona": self.app.session.get("zona", "N/A"),
            "area": self.app.session.get("area", "No disponible"),
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
            topbar, text="💾 Actualizar archivo (Excel)",
            font=(FONTS.family, FONTS.size_sm, "bold"), fg_color=COLORS.primary,
            text_color="white", height=32, command=self._guardar_excel
        ).grid(row=0, column=2, padx=16, pady=8, sticky="e")

    def _build_header_stats(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(20, 0))
        frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._kpi_card(frame, 0, "Consumo Promedio Anual", 
                      f"{self.metricas['consumo_promedio_anual']:,.0f}", self.config['unidad'])
        
        self._kpi_card(frame, 1, "Ahorro Potencial Anual", 
                      f"{self.metricas['potencial_ahorro_kwh']:,.0f}", self.config['unidad'], color=COLORS.success)
        
        self._kpi_card(frame, 2, "Ahorro Potencial (%)", 
                      f"{self.metricas['potencial_ahorro_pct']:.1f}%", "Estimado")

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
        
        self.tabs.add("📝 Identificación")
        self.tabs.add("📈 Línea Base (LBEn)")
        self.tabs.add("📊 Potenciales")
        self.tabs.add("📋 Monitoreo")

        self._render_identificacion_tab()
        self._render_lben_tab()
        self._render_potenciales_tab()
        self._render_monitoreo_tab()

    def _render_identificacion_tab(self):
        tab = self.tabs.tab("📝 Identificación")
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # 1. Tabla ID Proyecto
        self._tabla_simple(scroll, "IDENTIFICACIÓN DEL PROYECTO", [
            ("Nombre Edificio / Entidad", self.config['nombre']),
            ("Fuente de Energía", self.config['fuente']),
            ("Unidad de Energía", self.config['unidad']),
            ("Zona Climática", self.config['zona']),
            ("Área útil (m2)", self.config['area'])
        ])

        # 2. Tabla Métricas Modelo
        m = self.metricas
        self._tabla_simple(scroll, "MÉTRICAS DEL MODELO", [
            ("Tipo de Modelo", self.app.session.get("tipo_modelo", "M1 (Consumo Absoluto)")),
            ("N datos iniciales", f"{m['n_inicial']}"),
            ("N datos filtrado estadístico", f"{m['n_filt_est']}"),
            ("N datos filtrado manual", f"{m['n_filt_man']}"),
            ("N datos usados en modelo", f"{m['n_final']}"),
            ("Fiabilidad [%]", f"{m['fiabilidad']:.1f}%"),
            ("Periodo base (inicio)", self.config['pb_ini']),
            ("Periodo base (fin)", self.config['pb_fin']),
            ("Consumo promedio anual", f"{m['consumo_promedio_anual']:,.2f}"),
            ("Potencial ahorro anual (kWh)", f"{m['potencial_ahorro_kwh']:,.2f}"),
            ("Potencial ahorro anual (%)", f"{m['potencial_ahorro_pct']:.1f}%"),
            ("Meta 15% Promedio Base", f"{m['meta_15']:,.2f}")
        ], pady=(20, 0))

    def _tabla_simple(self, parent, title, rows, pady=0):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=pady)
        
        lbl_title = ctk.CTkLabel(frame, text=title, font=(FONTS.family, 14, "bold"), text_color=COLORS.primary, anchor="w")
        lbl_title.pack(fill="x", pady=(0, 10))

        content = ctk.CTkFrame(frame, fg_color=COLORS.bg_card, corner_radius=8, border_width=1, border_color=COLORS.border)
        content.pack(fill="x")
        
        for i, (label, value) in enumerate(rows):
            row_f = ctk.CTkFrame(content, fg_color="transparent", height=35)
            row_f.pack(fill="x", padx=15, pady=2)
            
            # Línea divisoria
            if i > 0: ctk.CTkFrame(content, fg_color=COLORS.border, height=1).pack(fill="x", padx=10)

            ctk.CTkLabel(row_f, text=label, font=(FONTS.family, 11), text_color=COLORS.text_secondary, anchor="w").place(relx=0, rely=0.5, anchor="w")
            ctk.CTkLabel(row_f, text=value, font=(FONTS.family, 11, "bold"), text_color=COLORS.text_primary, anchor="e").place(relx=1.0, rely=0.5, anchor="e")

    def _render_lben_tab(self):
        tab = self.tabs.tab("📈 Línea Base (LBEn)")
        for w in tab.winfo_children(): w.destroy()
        
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # 1. Header con Botón Interactivo
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(header, text="Comportamiento de la Línea Base", font=(FONTS.family, 14, "bold"), text_color=COLORS.primary).pack(side="left")
        
        ctk.CTkButton(header, text="🌐 Ver interactivo en navegador", font=(FONTS.family, 10, "bold"),
                      fg_color="transparent", border_width=1, border_color=COLORS.primary,
                      text_color=COLORS.primary, height=28, command=self._abrir_plotly_lben).pack(side="right")

        # 2. Gráfico Matplotlib Estilizado
        fig_frame = ctk.CTkFrame(scroll, fg_color=COLORS.bg_card, corner_radius=12, border_width=1, border_color=COLORS.border)
        fig_frame.pack(fill="x", pady=10)

        fig, ax = plt.subplots(figsize=(10, 5), facecolor=COLORS.bg_card)
        ax.set_facecolor("#F8FAF9")
        
        # Preparar Datos
        df_pts = self.df_base_f.copy()
        
        # Diccionario de traducción para meses en español
        meses_es_en = {
            'Ene': 'Jan', 'Feb': 'Feb', 'Mar': 'Mar', 'Abr': 'Apr',
            'May': 'May', 'Jun': 'Jun', 'Jul': 'Jul', 'Ago': 'Aug',
            'Sep': 'Sep', 'Oct': 'Oct', 'Nov': 'Nov', 'Dic': 'Dec'
        }
        
        def safe_to_datetime(val):
            if isinstance(val, str):
                for es, en in meses_es_en.items():
                    if es in val: val = val.replace(es, en)
            return pd.to_datetime(val, errors='coerce')

        df_pts['Fecha_DT'] = df_pts['Fecha'].apply(safe_to_datetime)
        df_pts['mes_n'] = df_pts['Fecha_DT'].dt.month
        df_pts['año'] = df_pts['Fecha_DT'].dt.year
        
        meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        x_ticks = range(1, 13)

        # A. Puntos Individuales por Año
        years = df_pts['año'].unique()
        for yr in years:
            data_yr = df_pts[df_pts['año'] == yr]
            ax.scatter(data_yr['mes_n'], data_yr['Ajustado'], alpha=0.6, label=f"Año {yr}", edgecolors='white', s=40)

        # B. Línea Promedio (LBEn)
        ax.plot(x_ticks, self.df_lben['lben'], color=COLORS.primary, linewidth=2.5, label="Promedio (LBEn)", marker='o', markersize=6)
        
        # C. Línea Meta (Mínimos)
        ax.plot(x_ticks, self.df_lben['min_hist'], color=COLORS.success, linewidth=2, linestyle='--', label="Línea Meta")

        # D. Sombreado de Confianza (+-10%)
        ax.fill_between(x_ticks, self.df_lben['lim_inf'], self.df_lben['lim_sup'], color=COLORS.primary, alpha=0.1, label="Confianza (±10%)")

        ax.set_xticks(x_ticks)
        ax.set_xticklabels(meses_nombres)
        ax.grid(True, linestyle=':', alpha=0.4)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=4, fontsize=8)
        ax.set_ylabel(self.config['unidad'])
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=fig_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # 3. Tabla LBEn Mensual
        self._tabla_lben_datos(scroll)

    def _tabla_lben_datos(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(frame, text="TABLA LBEn MENSUAL", font=(FONTS.family, 13, "bold"), text_color=COLORS.primary, anchor="w").pack(fill="x", pady=(0, 10))

        # Contenedor con Scroll Lateral si es necesario
        tbl_container = ctk.CTkScrollableFrame(frame, fg_color=COLORS.bg_card, height=450, orientation="horizontal", border_width=1, border_color=COLORS.border)
        tbl_container.pack(fill="x")

        headers = ["Mes", "LBEn (kWh/mes)", "N Datos", "Límite Inf. (kWh)", "Límite Sup. (kWh)"]
        h_frame = ctk.CTkFrame(tbl_container, fg_color=COLORS.primary, height=35)
        h_frame.pack(fill="x")
        
        for i, h in enumerate(headers):
            ctk.CTkLabel(h_frame, text=h, text_color="white", font=(FONTS.family, 11, "bold"), width=150).grid(row=0, column=i, padx=5)

        for _, row in self.df_lben.iterrows():
            r_frame = ctk.CTkFrame(tbl_container, fg_color="transparent")
            r_frame.pack(fill="x", pady=1)
            
            ctk.CTkLabel(r_frame, text=row['mes'], width=150, font=(FONTS.family, 11)).grid(row=0, column=0, padx=5)
            ctk.CTkLabel(r_frame, text=f"{row['lben']:,.2f}", width=150, font=(FONTS.family, 11, "bold")).grid(row=0, column=1, padx=5)
            ctk.CTkLabel(r_frame, text=f"{int(row['n_usados'])}", width=150, font=(FONTS.family, 11)).grid(row=0, column=2, padx=5)
            ctk.CTkLabel(r_frame, text=f"{row['lim_inf']:,.2f}", width=150, font=(FONTS.family, 11), text_color=COLORS.text_secondary).grid(row=0, column=3, padx=5)
            ctk.CTkLabel(r_frame, text=f"{row['lim_sup']:,.2f}", width=150, font=(FONTS.family, 11), text_color=COLORS.text_secondary).grid(row=0, column=4, padx=5)
            
            ctk.CTkFrame(tbl_container, fg_color=COLORS.border, height=1).pack(fill="x")

    def _abrir_plotly_lben(self):
        try:
            df_pts = self.df_base_f.copy()
            meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
            
            # Traducción para Plotly
            meses_es_en = {'Ene':'Jan','Feb':'Feb','Mar':'Mar','Abr':'Apr','May':'May','Jun':'Jun',
                           'Jul':'Jul','Ago':'Aug','Sep':'Sep','Oct':'Oct','Nov':'Nov','Dic':'Dec'}
            
            def safe_to_datetime(val):
                if isinstance(val, str):
                    for es, en in meses_es_en.items():
                        if es in val: val = val.replace(es, en)
                return pd.to_datetime(val, errors='coerce')
            
            df_pts['Fecha_DT'] = df_pts['Fecha'].apply(safe_to_datetime)
            df_pts['mes_n'] = df_pts['Fecha_DT'].dt.month
            df_pts['año'] = df_pts['Fecha_DT'].dt.year
            
            fig = go.Figure()
            
            # Sombreado Confianza
            fig.add_trace(go.Scatter(
                x=meses_nombres + meses_nombres[::-1],
                y=list(self.df_lben['lim_sup']) + list(self.df_lben['lim_inf'])[::-1],
                fill='toself', fillcolor='rgba(0,100,80,0.1)', line_color='rgba(255,255,255,0)',
                name='Intervalo de confianza (±10%)', hoverinfo='skip'
            ))

            # Puntos Reales
            for yr in df_pts['año'].unique():
                d_yr = df_pts[df_pts['año'] == yr]
                fig.add_trace(go.Scatter(x=[meses_nombres[m-1] for m in d_yr['mes_n']], y=d_yr['Ajustado'],
                                         mode='markers', name=f'Año {yr}', marker=dict(size=8, opacity=0.7)))

            # Línea LBEn
            fig.add_trace(go.Scatter(x=meses_nombres, y=self.df_lben['lben'], name='LBEn (Promedio)',
                                     line=dict(color='rgb(31, 119, 180)', width=4), marker=dict(size=10)))
            
            # Línea Meta
            fig.add_trace(go.Scatter(x=meses_nombres, y=self.df_lben['min_hist'], name='Línea Meta',
                                     line=dict(color='rgb(44, 160, 44)', width=2, dash='dash')))

            fig.update_layout(title=f"Línea Base Energética — {self.config['nombre']}",
                              xaxis_title="Mes", yaxis_title=self.config['unidad'],
                              template="plotly_white", hovermode="x unified")
            
            path = os.path.join(os.getcwd(), "temp_graph_lben.html")
            fig.write_html(path)
            webbrowser.open(f"file://{path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el interactivo: {e}")

    def _render_potenciales_tab(self):
        tab = self.tabs.tab("📊 Potenciales")
        for w in tab.winfo_children(): w.destroy()
        
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(scroll, text="TABLA DE AHORRO POTENCIAL", font=(FONTS.family, 14, "bold"), text_color=COLORS.primary, anchor="w").pack(fill="x", pady=(0, 10))

        # Tabla de Ahorro Potencial
        tbl_container = ctk.CTkScrollableFrame(scroll, fg_color=COLORS.bg_card, height=600, orientation="horizontal", border_width=1, border_color=COLORS.border)
        tbl_container.pack(fill="x")

        headers = ["Mes", "LBEn (kWh/mes)", "Mínimo Histórico (kWh)", "Ahorro Potencial (kWh)", "Ahorro Potencial (%)"]
        h_frame = ctk.CTkFrame(tbl_container, fg_color=COLORS.primary, height=35)
        h_frame.pack(fill="x")
        
        for i, h in enumerate(headers):
            ctk.CTkLabel(h_frame, text=h, text_color="white", font=(FONTS.family, 11, "bold"), width=160).grid(row=0, column=i, padx=5)

        for _, row in self.df_lben.iterrows():
            ahorro_kwh = row['lben'] - row['min_hist']
            ahorro_pct = (ahorro_kwh / row['lben'] * 100) if row['lben'] > 0 else 0
            
            r_frame = ctk.CTkFrame(tbl_container, fg_color="transparent")
            r_frame.pack(fill="x", pady=1)
            
            ctk.CTkLabel(r_frame, text=row['mes'], width=160, font=(FONTS.family, 11)).grid(row=0, column=0, padx=5)
            ctk.CTkLabel(r_frame, text=f"{row['lben']:,.2f}", width=160, font=(FONTS.family, 11)).grid(row=0, column=1, padx=5)
            ctk.CTkLabel(r_frame, text=f"{row['min_hist']:,.2f}", width=160, font=(FONTS.family, 11), text_color=COLORS.text_secondary).grid(row=0, column=2, padx=5)
            ctk.CTkLabel(r_frame, text=f"{ahorro_kwh:,.2f}", width=160, font=(FONTS.family, 11, "bold"), text_color=COLORS.success).grid(row=0, column=3, padx=5)
            ctk.CTkLabel(r_frame, text=f"{ahorro_pct:.1f}%", width=160, font=(FONTS.family, 11, "bold"), text_color=COLORS.success).grid(row=0, column=4, padx=5)
            
            ctk.CTkFrame(tbl_container, fg_color=COLORS.border, height=1).pack(fill="x")

        # Fila de Totales
        m = self.metricas
        sum_min = self.df_lben['min_hist'].sum()
        t_frame = ctk.CTkFrame(tbl_container, fg_color="#F0F4F2", height=40)
        t_frame.pack(fill="x", pady=(5, 0))
        ctk.CTkLabel(t_frame, text="PROMEDIO ANUAL", width=160, font=(FONTS.family, 11, "bold")).grid(row=0, column=0, padx=5)
        ctk.CTkLabel(t_frame, text=f"{m['consumo_promedio_anual']:,.2f}", width=160, font=(FONTS.family, 11, "bold")).grid(row=0, column=1, padx=5)
        ctk.CTkLabel(t_frame, text=f"{sum_min:,.2f}", width=160, font=(FONTS.family, 11, "bold"), text_color=COLORS.text_secondary).grid(row=0, column=2, padx=5)
        ctk.CTkLabel(t_frame, text=f"{m['potencial_ahorro_kwh']:,.2f}", width=160, font=(FONTS.family, 11, "bold"), text_color=COLORS.success).grid(row=0, column=3, padx=5)
        ctk.CTkLabel(t_frame, text=f"{m['potencial_ahorro_pct']:.1f}%", width=160, font=(FONTS.family, 11, "bold"), text_color=COLORS.success).grid(row=0, column=4, padx=5)

    def _render_monitoreo_tab(self):
        tab = self.tabs.tab("📋 Monitoreo")
        for w in tab.winfo_children(): w.destroy()
        
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # 1. Tabla de Monitoreo
        self._tabla_monitoreo_detallada(scroll)

        # 2. Gráficas de Monitoreo
        self._graficas_monitoreo(scroll)

    def _tabla_monitoreo_detallada(self, parent):
        ctk.CTkLabel(parent, text="DATOS DE MONITOREO", font=(FONTS.family, 14, "bold"), text_color=COLORS.primary, anchor="w").pack(fill="x", pady=(10, 10))
        
        # 1. Contenedor Horizontal Exterior (para las columnas)
        # Aumentamos un poco el alto para contener el scroll vertical interno
        h_scroll = ctk.CTkScrollableFrame(parent, fg_color=COLORS.bg_card, height=450, orientation="horizontal", border_width=1, border_color=COLORS.border)
        h_scroll.pack(fill="x")

        # 2. Frame interno para organizar Header y Body verticalmente
        inner_frame = ctk.CTkFrame(h_scroll, fg_color="transparent")
        inner_frame.pack(fill="both", expand=True)

        headers = [
            "Fecha", "Norm. (kWh)", "Adj. (kWh)", "LBEn (kWh)", 
            "Desemp. (kWh)", "Desemp. (%)", "CUSUM (kWh)", 
            "Avance Pot. (%)", "Avance 15% (%)", 
            "Econ. (COP)", "Econ. Acum. (COP)", 
            "Amb. (kgCO2e)", "Amb. Acum. (kgCO2e)"
        ]
        
        h_frame = ctk.CTkFrame(inner_frame, fg_color=COLORS.primary, height=40)
        h_frame.pack(fill="x")
        
        col_width = 135
        for i, h in enumerate(headers):
            ctk.CTkLabel(h_frame, text=h, text_color="white", font=(FONTS.family, 10, "bold"), width=col_width).grid(row=0, column=i, padx=5)

        # 3. Contenedor Vertical para las filas (el scroll exclusivo)
        v_scroll = ctk.CTkScrollableFrame(inner_frame, fg_color="transparent", height=380, orientation="vertical")
        v_scroll.pack(fill="both", expand=True)

        for _, row in self.df_mon.iterrows():
            r_frame = ctk.CTkFrame(v_scroll, fg_color="transparent")
            r_frame.pack(fill="x", pady=1)
            
            color_des = COLORS.success if row['Desemp_kWh'] <= 0 else COLORS.danger
            
            vals = [
                row['Fecha'],
                f"{row['Normalizado']:,.1f}",
                f"{row['Ajustado']:,.1f}",
                f"{row['LBEn_Mes']:,.1f}",
                f"{row['Desemp_kWh']:,.1f}",
                f"{row['Desemp_Pct']:.1f}%",
                f"{row['CUSUM_kWh']:,.1f}",
                f"{row['Avance_Pot']:.1f}%",
                f"{row['Avance_15']:.1f}%",
                f"{row['Desemp_COP']:,.0f}",
                f"{row['CUSUM_COP']:,.0f}",
                f"{row['Desemp_CO2']:,.1f}",
                f"{row['CUSUM_CO2']:,.1f}"
            ]

            for i, v in enumerate(vals):
                txt_c = color_des if i in [4, 5, 6, 9, 10, 11, 12] else COLORS.text_primary
                ctk.CTkLabel(r_frame, text=v, width=col_width, font=(FONTS.family, 10), text_color=txt_c).grid(row=0, column=i, padx=5)
            
            ctk.CTkFrame(v_scroll, fg_color=COLORS.border, height=1).pack(fill="x")

    def _graficas_monitoreo(self, parent):
        # Gráfico 1: Seguimiento Real vs Meta
        h1 = ctk.CTkFrame(parent, fg_color="transparent")
        h1.pack(fill="x", pady=(10, 5))
        ctk.CTkLabel(h1, text="Seguimiento Energético: Real vs Meta", font=(FONTS.family, 12, "bold"), text_color=COLORS.primary).pack(side="left")
        ctk.CTkButton(h1, text="🌐 Ver interactivo", font=(FONTS.family, 9, "bold"), fg_color="transparent", border_width=1, border_color=COLORS.primary, text_color=COLORS.primary, height=24, command=self._abrir_plotly_seguimiento).pack(side="right")

        f1 = ctk.CTkFrame(parent, fg_color=COLORS.bg_card, corner_radius=12, border_width=1, border_color=COLORS.border)
        f1.pack(fill="x", pady=(0, 20))
        
        fig1, ax1 = plt.subplots(figsize=(10, 4), facecolor=COLORS.bg_card)
        ax1.set_facecolor("#F8FAF9")
        
        fechas = self.df_mon['Fecha']
        ax1.plot(fechas, self.df_mon['LBEn_Mes'], color=COLORS.primary, linestyle='--', label="Línea Base (Meta)", linewidth=2)
        ax1.plot(fechas, self.df_mon['Ajustado'], color=COLORS.danger, marker='o', label="Consumo Real", linewidth=2)
        
        # Sombreado Confianza (±10%)
        lben = self.df_mon['LBEn_Mes']
        ax1.fill_between(fechas, lben*0.9, lben*1.1, color=COLORS.primary, alpha=0.1, label="Zona de Control")
        
        # ax1.set_title("Seguimiento Energético: Real vs Meta", fontsize=12, fontweight='bold')
        ax1.legend(loc='upper right', fontsize=8)
        ax1.grid(True, linestyle=':', alpha=0.3)
        plt.tight_layout()
        
        canvas1 = FigureCanvasTkAgg(fig1, master=f1)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Gráfico 2: CUSUM (Cromático)
        h2 = ctk.CTkFrame(parent, fg_color="transparent")
        h2.pack(fill="x", pady=(10, 5))
        ctk.CTkLabel(h2, text="Desempeño Energético Acumulado (CUSUM kWh)", font=(FONTS.family, 12, "bold"), text_color=COLORS.primary).pack(side="left")
        ctk.CTkButton(h2, text="🌐 Ver interactivo", font=(FONTS.family, 9, "bold"), fg_color="transparent", border_width=1, border_color=COLORS.primary, text_color=COLORS.primary, height=24, command=self._abrir_plotly_cusum).pack(side="right")

        f2 = ctk.CTkFrame(parent, fg_color=COLORS.bg_card, corner_radius=12, border_width=1, border_color=COLORS.border)
        f2.pack(fill="x", pady=(0, 20))
        
        fig2, ax2 = plt.subplots(figsize=(10, 4), facecolor=COLORS.bg_card)
        ax2.set_facecolor("#F8FAF9")
        
        y_cusum = self.df_mon['CUSUM_kWh'].values
        x_indices = range(len(y_cusum))
        
        # Dibujar por segmentos para aplicar color ahorro/sobreconsumo
        for i in range(len(y_cusum)-1):
            # AHORRO (Verde): si el CUSUM baja (más negativo) o se mantiene abajo
            # SOBRECONSUMO (Rojo): si el CUSUM sube
            color = COLORS.success if y_cusum[i+1] <= y_cusum[i] else COLORS.danger
            ax2.plot([fechas.iloc[i], fechas.iloc[i+1]], [y_cusum[i], y_cusum[i+1]], color=color, linewidth=3, marker='o', markersize=4)

        ax2.axhline(0, color=COLORS.text_secondary, linestyle='-', alpha=0.5)
        # ax2.set_title("Desempeño Energético Acumulado (CUSUM kWh)", fontsize=12, fontweight='bold')
        ax2.grid(True, linestyle=':', alpha=0.3)
        plt.tight_layout()
        
        canvas2 = FigureCanvasTkAgg(fig2, master=f2)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def _abrir_plotly_seguimiento(self):
        try:
            fig = go.Figure()
            fechas = self.df_mon['Fecha']
            lben = self.df_mon['LBEn_Mes']
            real = self.df_mon['Ajustado']

            # Sombreado
            fig.add_trace(go.Scatter(x=list(fechas)+list(fechas)[::-1], y=list(lben*1.1)+list(lben*0.9)[::-1], fill='toself', fillcolor='rgba(0,100,80,0.1)', line_color='rgba(255,255,255,0)', name='Zona Control (±10%)', hoverinfo='skip'))
            fig.add_trace(go.Scatter(x=fechas, y=lben, name='LBEn (Meta)', line=dict(color='rgb(31, 119, 180)', width=2, dash='dash')))
            fig.add_trace(go.Scatter(x=fechas, y=real, name='Consumo Real', line=dict(color='rgb(214, 39, 40)', width=3), marker=dict(size=8)))

            fig.update_layout(title="Seguimiento Energético vs Meta", xaxis_title="Fecha", yaxis_title=self.config['unidad'], template="plotly_white", hovermode="x unified")
            path = os.path.join(os.getcwd(), "temp_graph_seguimiento.html")
            fig.write_html(path)
            webbrowser.open(f"file://{path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el interactivo: {e}")

    def _abrir_plotly_cusum(self):
        try:
            fig = go.Figure()
            fechas = self.df_mon['Fecha']
            y_cusum = self.df_mon['CUSUM_kWh'].values
            
            for i in range(len(y_cusum)-1):
                color = 'rgb(44, 160, 44)' if y_cusum[i+1] <= y_cusum[i] else 'rgb(214, 39, 40)'
                fig.add_trace(go.Scatter(x=[fechas.iloc[i], fechas.iloc[i+1]], y=[y_cusum[i], y_cusum[i+1]], mode='lines+markers', line=dict(color=color, width=4), showlegend=False))

            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            fig.update_layout(title="CUSUM Acumulado (kWh)", xaxis_title="Fecha", yaxis_title="kWh Acumulado", template="plotly_white")
            path = os.path.join(os.getcwd(), "temp_graph_cusum.html")
            fig.write_html(path)
            webbrowser.open(f"file://{path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el interactivo: {e}")

    def _guardar_excel(self):
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
