"""
ui/pages/m1_resultados.py
=========================
Visualización de resultados del Modelo M1: Consumo Absoluto.
Incluye Ficha Técnica, LBEn Mensual, Desempeño y Seguimiento.
Sistema de tabs idéntico al M2 (botones manuales con CTkFrame).
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
import tempfile
import threading
import plotly.graph_objects as go
import numpy as np

# Paleta de colores para años (igual que M2)
YEAR_COLORS = ["#2196F3", "#FF9800", "#4CAF50", "#E91E63", "#9C27B0"]
MESES_NOMBRES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                 "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
MESES_ES_EN = {
    'Ene': 'Jan', 'Feb': 'Feb', 'Mar': 'Mar', 'Abr': 'Apr',
    'May': 'May', 'Jun': 'Jun', 'Jul': 'Jul', 'Ago': 'Aug',
    'Sep': 'Sep', 'Oct': 'Oct', 'Nov': 'Nov', 'Dic': 'Dec'
}


def safe_to_datetime(val):
    """Convierte un valor a datetime tolerando formatos en español."""
    if isinstance(val, str):
        for es, en in MESES_ES_EN.items():
            if es in val:
                val = val.replace(es, en)
    return pd.to_datetime(val, errors='coerce')


class M1ResultadosPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master

        # Recuperar datos de sesión
        self.df_lben   = self.app.session.get("df_lben")
        self.df_mon    = self.app.session.get("df_monitoreo")
        self.df_base   = self.app.session.get("df_base_raw")
        self.df_base_f = self.app.session.get("df_base_final")
        self.df_excl   = self.app.session.get("df_excluidos")
        self.metricas  = self.app.session.get("metricas_m1")
        self.config    = {
            "nombre": self.app.session.get("nombre", "Proyecto sin nombre"),
            "fuente": self.app.session.get("fuente", "N/A"),
            "unidad": self.app.session.get("unidad", "kWh"),
            "zona":   self.app.session.get("zona", "N/A"),
            "area":   self.app.session.get("area", "No disponible"),
            "pb_ini": self.app.session.get("pb_ini"),
            "pb_fin": self.app.session.get("pb_fin"),
        }

        self.current_tab = "identificacion"
        self._build()

    # ─────────────────────────────────────────────────────────────────
    # ESTRUCTURA PRINCIPAL  (idéntica al M2: header / stats / tabs)
    # ─────────────────────────────────────────────────────────────────

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)   # row 2 = content, se expande

        self._build_header()      # row 0
        self._build_kpi_cards()   # row 1
        self._build_tabs_area()   # row 2

    def _build_header(self):
        topbar = ctk.CTkFrame(self, fg_color=COLORS.bg_card,
                              height=DIMS.topbar_height, corner_radius=0)
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)
        ctk.CTkFrame(topbar, fg_color=COLORS.accent, height=2).place(
            relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        ctk.CTkButton(topbar, text="← Volver a Carga",
                      font=(FONTS.family, FONTS.size_sm),
                      fg_color="transparent", text_color=COLORS.primary,
                      hover_color=COLORS.bg_main,
                      command=lambda: self.app.navegar("m1_carga")
                      ).grid(row=0, column=0, padx=16, pady=8, sticky="w")

        ctk.CTkLabel(topbar,
                     text=f"M1: {self.config['nombre']}",
                     font=(FONTS.family, FONTS.size_md, "bold"),
                     text_color=COLORS.primary
                     ).grid(row=0, column=1, sticky="w", padx=8)

        self.btn_upd = ctk.CTkButton(
            topbar, text="💾 Actualizar archivo (Excel)",
            font=(FONTS.family, FONTS.size_sm, "bold"),
            fg_color=COLORS.primary, text_color="white", height=32,
            command=self._guardar_excel)
        self.btn_upd.grid(row=0, column=2, padx=16, pady=8, sticky="e")

    def _build_kpi_cards(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(12, 0))
        frame.grid_columnconfigure((0, 1, 2), weight=1)
        m = self.metricas
        self._kpi_card(frame, 0, "Consumo Promedio Anual",
                       f"{m['consumo_promedio_anual']:,.0f}", self.config['unidad'])
        self._kpi_card(frame, 1, "Ahorro Potencial Anual",
                       f"{m['potencial_ahorro_kwh']:,.0f}", self.config['unidad'])
        self._kpi_card(frame, 2, "Ahorro Potencial (%)",
                       f"{m['potencial_ahorro_pct']:.1f}%", "Estimado")

    def _kpi_card(self, parent, col, title, value, unit, color=None):
        c = ctk.CTkFrame(parent, fg_color=COLORS.bg_card, corner_radius=16,
                        border_width=2, border_color=COLORS.border)
        c.grid(row=0, column=col, padx=8, pady=6, sticky="ew", ipady=4)
        c.grid_columnconfigure(0, weight=1)
        c.grid_rowconfigure(0, weight=1)

        # Título
        ctk.CTkLabel(
            c, text=title,
            font=(FONTS.family, FONTS.size_lg),
            text_color=COLORS.text_secondary,
            anchor="center"
        ).grid(row=0, column=0, padx=14, pady=(8, 0), sticky="ew")

        # Separador
        ctk.CTkFrame(
            c, height=1, fg_color=COLORS.border
        ).grid(row=1, column=0, padx=20, pady=(6, 0), sticky="ew")

        # Valor
        ctk.CTkLabel(
            c, text=value,
            font=(FONTS.family, 26, "bold"),
            text_color=color if color else COLORS.text_primary,
            anchor="center"
        ).grid(row=2, column=0, padx=14, pady=(4, 0), sticky="ew")

        # Unidad
        ctk.CTkLabel(
            c, text=unit,
            font=(FONTS.family, FONTS.size_sm),
            text_color=COLORS.text_secondary,
            anchor="center"
        ).grid(row=3, column=0, padx=14, pady=(2, 0), sticky="ew")

        # Pill centrada
        ctk.CTkFrame(
            c, height=4, width=20,
            fg_color=color if color else COLORS.border,
            corner_radius=4
        ).grid(row=4, column=0, pady=(6, 10))

    def _build_tabs_area(self):
        """Área de navegación + contenido (ocupa todo el espacio restante)."""
        tabs_container = ctk.CTkFrame(self, fg_color="transparent")
        tabs_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        tabs_container.grid_columnconfigure(0, weight=1)
        tabs_container.grid_rowconfigure(1, weight=1)  # row 1 = content, expande

        # Fila 0: botones de navegación
        nav = ctk.CTkFrame(tabs_container, fg_color="transparent")
        nav.grid(row=0, column=0, pady=(0, 10))
        self.nav_buttons = {}
        tabs = [
            ("identificacion", "📝 Identificación"),
            ("lben",           "📈 Línea Base (LBEn)"),
            ("potenciales",    "📊 Potenciales"),
            ("monitoreo",      "📋 Monitoreo"),
        ]
        for i, (tab_id, label) in enumerate(tabs):
            btn = ctk.CTkButton(nav, text=label,
                                font=(FONTS.family, FONTS.size_sm),
                                fg_color=COLORS.border,
                                text_color=COLORS.text_primary,
                                width=150, height=36, corner_radius=8,
                                command=lambda t=tab_id: self._change_tab(t))
            btn.grid(row=0, column=i, padx=5)
            self.nav_buttons[tab_id] = btn

        # Fila 1: contenido dinámico (expande)
        self.content_view = ctk.CTkFrame(tabs_container, fg_color="transparent")
        self.content_view.grid(row=1, column=0, sticky="nsew")
        self.content_view.grid_columnconfigure(0, weight=1)
        self.content_view.grid_rowconfigure(0, weight=1)

        self._change_tab("identificacion")

    def _change_tab(self, tab_id):
        self.current_tab = tab_id
        for tid, btn in self.nav_buttons.items():
            btn.configure(fg_color=COLORS.primary if tid == tab_id else COLORS.border,
                          text_color=COLORS.text_white if tid == tab_id else COLORS.text_primary)
        for w in self.content_view.winfo_children():
            w.destroy()
        plt.close("all")
        {
            "identificacion": self._render_identificacion,
            "lben":           self._render_lben,
            "potenciales":    self._render_potenciales,
            "monitoreo":      self._render_monitoreo,
        }[tab_id]()

    # ─────────────────────────────────────────────────────────────────
    # TAB 1: IDENTIFICACIÓN
    # ─────────────────────────────────────────────────────────────────

    def _render_identificacion(self):
        scroll = ctk.CTkScrollableFrame(self.content_view, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        scroll.grid_columnconfigure(0, weight=1)

        # Contenedor de dos columnas
        cols = ctk.CTkFrame(scroll, fg_color="transparent")
        cols.pack(fill="both", expand=True)
        cols.grid_columnconfigure(0, weight=1)
        cols.grid_columnconfigure(1, weight=1)

        # ── Columna izquierda: Identificación del proyecto ──
        left = ctk.CTkFrame(cols, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self._tabla_simple(left, "IDENTIFICACIÓN DEL PROYECTO", [
            ("Nombre Edificio / Entidad",  self.config['nombre']),
            ("Fuente de Energía",          self.config['fuente'],
             "Unidad de Energía",          self.config['unidad']),
            ("Zona Climática",             self.config['zona']),
            ("Área útil (m²)",             self.config['area']),
            ("Periodo base — inicio",      self.config['pb_ini'],
             "Periodo base — fin",         self.config['pb_fin']),
        ])

        # ── Columna derecha: Métricas del modelo ──
        right = ctk.CTkFrame(cols, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        m = self.metricas
        self._tabla_simple(right, "MÉTRICAS DEL MODELO", [
            ("Tipo de Modelo",               self.app.session.get("tipo_modelo", "M1 — Consumo Absoluto")),
            ("N Datos iniciales",            f"{m['n_inicial']}"),
            ("N Datos filtrado estadístico", f"{m['n_filt_est']}"),
            ("Filtrado manual",              f"{m['n_filt_man']}"),
            ("N Datos usados en modelo",     f"{m['n_final']}"),
            ("Fiabilidad",                   f"{m['fiabilidad']:.1f}%"),
            ("Meta 15% Anual Base",          f"{m['meta_15']:,.0f} {self.config['unidad']}"),
        ])

    def _tabla_simple(self, parent, title, rows, pady=0):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=pady)

        title_row = ctk.CTkFrame(frame, fg_color=COLORS.primary, height=38, corner_radius=8)
        title_row.pack(fill="x")
        title_row.pack_propagate(False)

        ctk.CTkFrame(title_row, fg_color=COLORS.accent, width=4, height=20,
                     corner_radius=2).place(x=12, y=9)
        ctk.CTkLabel(title_row, text=title,
                     font=(FONTS.family, FONTS.size_xl, "bold"),
                     text_color="white", anchor="w").place(x=20, y=19, anchor="w")

        content = ctk.CTkFrame(frame, fg_color=COLORS.bg_card, corner_radius=20,
                               border_width=1, border_color=COLORS.border)
        content.pack(fill="x", padx=10, pady=0)

        for i, row in enumerate(rows):
            # Fila doble: tupla de 4 elementos
            if len(row) == 4:
                label1, value1, label2, value2 = row
                row_f = ctk.CTkFrame(content, fg_color="transparent", height=35)
                row_f.pack(fill="x", padx=15, pady=2)
                row_f.pack_propagate(False)

                left_half = ctk.CTkFrame(row_f, fg_color="transparent")
                left_half.place(relx=0, rely=0, relwidth=0.48, relheight=1.0)
                ctk.CTkLabel(left_half, text=label1,
                             font=(FONTS.family, FONTS.size_md),
                             text_color="#7A8C85", anchor="w").place(relx=0, rely=0.5, anchor="w")
                ctk.CTkLabel(left_half, text=str(value1),
                             font=(FONTS.family, FONTS.size_lg, "bold"),
                             text_color=COLORS.primary, anchor="e").place(relx=1.0, rely=0.5, anchor="e")

                ctk.CTkFrame(row_f, fg_color=COLORS.border, width=1,
                             corner_radius=0).place(relx=0.5, rely=0.1, relheight=0.8)

                right_half = ctk.CTkFrame(row_f, fg_color="transparent")
                right_half.place(relx=0.52, rely=0, relwidth=0.48, relheight=1.0)
                ctk.CTkLabel(right_half, text=label2,
                             font=(FONTS.family, FONTS.size_md),
                             text_color="#7A8C85", anchor="w").place(relx=0, rely=0.5, anchor="w")
                ctk.CTkLabel(right_half, text=str(value2),
                             font=(FONTS.family, FONTS.size_lg, "bold"),
                             text_color=COLORS.primary, anchor="e").place(relx=1.0, rely=0.5, anchor="e")

            # Fila simple: tupla de 2 elementos
            else:
                label, value = row
                row_f = ctk.CTkFrame(content, fg_color="transparent", height=35)
                row_f.pack(fill="x", padx=15, pady=2)
                ctk.CTkLabel(row_f, text=label,
                             font=(FONTS.family, FONTS.size_md),
                             text_color="#7A8C85", anchor="w").place(relx=0, rely=0.5, anchor="w")
                ctk.CTkLabel(row_f, text=str(value),
                             font=(FONTS.family, FONTS.size_lg, "bold"),
                             text_color=COLORS.primary, anchor="e").place(relx=1.0, rely=0.5, anchor="e")

            if i < len(rows) - 1:
                ctk.CTkFrame(content, fg_color=COLORS.border, height=1,
                             corner_radius=0).pack(fill="x", padx=10)

    # ─────────────────────────────────────────────────────────────────
    # TAB 2: LÍNEA BASE
    # ─────────────────────────────────────────────────────────────────

    def _render_lben(self):
        scroll = ctk.CTkScrollableFrame(self.content_view, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))

        title = ctk.CTkFrame(header, fg_color=COLORS.primary, height=38, corner_radius=8)
        title.pack(side="left", padx=(0, 10))
        title.pack_propagate(True)

        ctk.CTkFrame(title, fg_color=COLORS.accent, width=4, height=20,
                     corner_radius=2).place(x=12, y=5)
        ctk.CTkLabel(title, text="Comportamiento de la Línea Base",
                     font=(FONTS.family, FONTS.size_lg, "bold"),
                     text_color=COLORS.text_white).pack(side="left", padx=(20, 14))

        ctk.CTkButton(header, text="🌐 Ver interactivo en navegador",
                      font=(FONTS.family, FONTS.size_sm, "bold"),
                      fg_color="transparent", border_width=1,
                      border_color=COLORS.primary,
                      text_color=COLORS.primary, height=28,
                      command=self._abrir_plotly_lben).pack(side="right")

        # Gráfico
        fig_frame = ctk.CTkFrame(scroll, fg_color=COLORS.bg_card, corner_radius=12,
                                 border_width=1, border_color=COLORS.border)
        fig_frame.pack(fill="x", pady=10)

        fig, ax = plt.subplots(figsize=(10, 5), facecolor=COLORS.bg_card)
        ax.set_facecolor("#F8FAF9")
        x_ticks = range(1, 13)

        # A. Puntos históricos por año
        if self.df_base_f is not None:
            df_pts = self.df_base_f.copy()
            df_pts['Fecha_DT'] = df_pts['Fecha'].apply(safe_to_datetime)
            df_pts['mes_n'] = df_pts['Fecha_DT'].dt.month
            df_pts['año']   = df_pts['Fecha_DT'].dt.year
            for i, yr in enumerate(sorted(df_pts['año'].dropna().unique())):
                dy = df_pts[df_pts['año'] == yr]
                ax.scatter(dy['mes_n'], dy['Ajustado'],
                           color=YEAR_COLORS[i % len(YEAR_COLORS)],
                           alpha=0.7, label=f"Año {int(yr)}",
                           edgecolors='white', s=40)

        # B. LBEn promedio
        ax.plot(x_ticks, self.df_lben['lben'], color=COLORS.primary,
                linewidth=2.5, label="Promedio (LBEn)", marker='o', markersize=6)

        # C. Mínimo histórico (meta)
        ax.plot(x_ticks, self.df_lben['min_hist'], color=COLORS.success,
                linewidth=2, linestyle='--', label="Línea Meta")

        # D. Banda de confianza
        ax.fill_between(x_ticks, self.df_lben['lim_inf'], self.df_lben['lim_sup'],
                        color=COLORS.primary, alpha=0.1, label="Confianza (±10%)")

        ax.set_xticks(x_ticks)
        ax.set_xticklabels(MESES_NOMBRES)
        ax.set_ylabel(self.config['unidad'])
        ax.set_xlabel("Período")
        ax.grid(True, linestyle=':', alpha=0.4)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=4, fontsize=8)
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=fig_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Tabla LBEn Mensual
        self._tabla_lben_datos(scroll)

    def _tabla_lben_datos(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=20)

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        title = ctk.CTkFrame(header, fg_color=COLORS.primary, height=30, corner_radius=8)
        title.pack(side="left", padx=(0, 10))
        title.pack_propagate(True)

        ctk.CTkFrame(title, fg_color=COLORS.accent, width=4, height=16,
                     corner_radius=2).place(x=12, y=5)
        ctk.CTkLabel(title, text="TABLA LBEn MENSUAL",
                     font=(FONTS.family, FONTS.size_lg, "bold"),
                     text_color=COLORS.text_white).pack(side="left", padx=(20, 14))

        tbl = ctk.CTkScrollableFrame(frame, fg_color=COLORS.bg_card,
                                     height=420, orientation="horizontal",
                                     border_width=1, border_color=COLORS.border,
                                     width=870)
        tbl.pack(pady=0)
        tbl.pack_configure(anchor="center")

        COL_W = 160
        headers = ["Mes", "LBEn (kWh/mes)", "N Datos",
                   "Límite Inf. (kWh)", "Límite Sup. (kWh)"]
        h_frame = ctk.CTkFrame(tbl, fg_color=COLORS.primary, height=35)
        h_frame.pack(fill="x")
        for i, h in enumerate(headers):
            ctk.CTkLabel(h_frame, text=h, text_color="white",
                         font=(FONTS.family, 11, "bold"), width=COL_W).grid(row=0, column=i, padx=5)

        for _, row in self.df_lben.iterrows():
            r = ctk.CTkFrame(tbl, fg_color="transparent")
            r.pack(fill="x", pady=1)
            ctk.CTkLabel(r, text=str(row['mes']),          width=COL_W, font=(FONTS.family, 11)).grid(row=0, column=0, padx=5)
            ctk.CTkLabel(r, text=f"{row['lben']:,.2f}",    width=COL_W, font=(FONTS.family, 11, "bold")).grid(row=0, column=1, padx=5)
            ctk.CTkLabel(r, text=f"{int(row['n_usados'])}", width=COL_W, font=(FONTS.family, 11)).grid(row=0, column=2, padx=5)
            ctk.CTkLabel(r, text=f"{row['lim_inf']:,.2f}", width=COL_W, font=(FONTS.family, 11), text_color=COLORS.text_secondary).grid(row=0, column=3, padx=5)
            ctk.CTkLabel(r, text=f"{row['lim_sup']:,.2f}", width=COL_W, font=(FONTS.family, 11), text_color=COLORS.text_secondary).grid(row=0, column=4, padx=5)
            ctk.CTkFrame(tbl, fg_color=COLORS.border, height=1).pack(fill="x")

    def _abrir_plotly_lben(self):
        try:
            x_ticks = list(range(1, 13))
            fig = go.Figure()

            if self.df_base_f is not None:
                df_pts = self.df_base_f.copy()
                df_pts['Fecha_DT'] = df_pts['Fecha'].apply(safe_to_datetime)
                df_pts['mes_n'] = df_pts['Fecha_DT'].dt.month
                df_pts['año']   = df_pts['Fecha_DT'].dt.year
                for i, yr in enumerate(sorted(df_pts['año'].dropna().unique())):
                    dy = df_pts[df_pts['año'] == yr]
                    fig.add_trace(go.Scatter(
                        x=dy['mes_n'], y=dy['Ajustado'], mode='markers',
                        name=f"Año {int(yr)}",
                        marker=dict(color=YEAR_COLORS[i % len(YEAR_COLORS)], size=8)))

            # Banda confianza
            lim_sup = list(self.df_lben['lim_sup'])
            lim_inf = list(self.df_lben['lim_inf'])
            fig.add_trace(go.Scatter(
                x=x_ticks + x_ticks[::-1], y=lim_sup + lim_inf[::-1],
                fill='toself', fillcolor='rgba(30,100,60,0.1)',
                line=dict(color='rgba(0,0,0,0)'), name='Confianza (±10%)',
                hoverinfo='skip'))

            fig.add_trace(go.Scatter(
                x=x_ticks, y=self.df_lben['lben'], mode='lines+markers',
                name='Promedio (LBEn)',
                line=dict(color=COLORS.primary, width=3),
                marker=dict(size=8)))

            fig.add_trace(go.Scatter(
                x=x_ticks, y=self.df_lben['min_hist'], mode='lines',
                name='Línea Meta',
                line=dict(color=COLORS.success, dash='dash', width=2)))

            fig.update_xaxes(tickvals=x_ticks, ticktext=MESES_NOMBRES)
            fig.update_layout(
                title=f"Línea Base Energética M1 — {self.config['nombre']}",
                template="plotly_white",
                xaxis_title="Mes", yaxis_title=self.config['unidad'],
                hovermode="x unified")

            tmp = os.path.join(tempfile.gettempdir(), "lben_m1.html")
            fig.write_html(tmp)
            webbrowser.open(f"file:///{tmp}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el gráfico:\n{e}")

    # ─────────────────────────────────────────────────────────────────
    # TAB 3: POTENCIALES
    # ─────────────────────────────────────────────────────────────────

    def _render_potenciales(self):
        scroll = ctk.CTkScrollableFrame(self.content_view, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))

        title = ctk.CTkFrame(header, fg_color=COLORS.primary, height=38, corner_radius=8)
        title.pack(side="left", padx=(0, 10))
        title.pack_propagate(True)

        ctk.CTkFrame(title, fg_color=COLORS.accent, width=4, height=20,
                     corner_radius=2).place(x=12, y=5)
        ctk.CTkLabel(title, text="TABLA DE AHORRO POTENCIAL",
                     font=(FONTS.family, FONTS.size_lg, "bold"),
                     text_color=COLORS.text_white).pack(side="left", padx=(20, 14))

        tbl = ctk.CTkScrollableFrame(scroll, fg_color=COLORS.bg_card,
                                     height=470, orientation="horizontal",
                                     border_width=1, border_color=COLORS.border)
        tbl.configure(width=840)
        tbl.pack()
        tbl.pack_configure(anchor="center")

        COL_W = 160
        headers = ["Mes", "LBEn (kWh/mes)", "Mínimo Histórico (kWh)",
                   "Ahorro Potencial (kWh)", "Ahorro Potencial (%)"]
        h_frame = ctk.CTkFrame(tbl, fg_color=COLORS.primary, height=35)
        h_frame.pack(fill="x")
        for i, h in enumerate(headers):
            ctk.CTkLabel(h_frame, text=h, text_color="white",
                         font=(FONTS.family, 11, "bold"),
                         width=COL_W, wraplength=150).grid(row=0, column=i, padx=5, pady=5)

        for _, row in self.df_lben.iterrows():
            ahorro_kwh = row['lben'] - row['min_hist']
            ahorro_pct = (ahorro_kwh / row['lben'] * 100) if row['lben'] > 0 else 0

            r = ctk.CTkFrame(tbl, fg_color="transparent")
            r.pack(fill="x", pady=1)
            ctk.CTkLabel(r, text=str(row['mes']),            width=COL_W, font=(FONTS.family, 11)).grid(row=0, column=0, padx=5)
            ctk.CTkLabel(r, text=f"{row['lben']:,.2f}",      width=COL_W, font=(FONTS.family, 11)).grid(row=0, column=1, padx=5)
            ctk.CTkLabel(r, text=f"{row['min_hist']:,.2f}",  width=COL_W, font=(FONTS.family, 11), text_color=COLORS.text_secondary).grid(row=0, column=2, padx=5)
            ctk.CTkLabel(r, text=f"{ahorro_kwh:,.2f}",       width=COL_W, font=(FONTS.family, 11, "bold"), text_color=COLORS.success).grid(row=0, column=3, padx=5)
            ctk.CTkLabel(r, text=f"{ahorro_pct:.1f}%",       width=COL_W, font=(FONTS.family, 11, "bold"), text_color=COLORS.success).grid(row=0, column=4, padx=5)
            ctk.CTkFrame(tbl, fg_color=COLORS.border, height=1).pack(fill="x")

        # Fila totales
        m = self.metricas
        sum_min = self.df_lben['min_hist'].sum()
        t = ctk.CTkFrame(tbl, fg_color="#F0F4F2", height=40)
        t.pack(fill="x", pady=(5, 0))
        ctk.CTkLabel(t, text="PROMEDIO ANUAL",                     width=COL_W, font=(FONTS.family, 11, "bold"), text_color=COLORS.primary).grid(row=0, column=0, padx=5)
        ctk.CTkLabel(t, text=f"{m['consumo_promedio_anual']:,.2f}", width=COL_W, font=(FONTS.family, 11, "bold"), text_color=COLORS.primary).grid(row=0, column=1, padx=5)
        ctk.CTkLabel(t, text=f"{sum_min:,.2f}",                    width=COL_W, font=(FONTS.family, 11, "bold"), text_color=COLORS.text_secondary).grid(row=0, column=2, padx=5)
        ctk.CTkLabel(t, text=f"{m['potencial_ahorro_kwh']:,.2f}",  width=COL_W, font=(FONTS.family, 11, "bold"), text_color=COLORS.success).grid(row=0, column=3, padx=5)
        ctk.CTkLabel(t, text=f"{m['potencial_ahorro_pct']:.1f}%",  width=COL_W, font=(FONTS.family, 11, "bold"), text_color=COLORS.success).grid(row=0, column=4, padx=5)

    # ─────────────────────────────────────────────────────────────────
    # TAB 4: MONITOREO
    # ─────────────────────────────────────────────────────────────────

    def _render_monitoreo(self):
        scroll = ctk.CTkScrollableFrame(self.content_view, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        if self.df_mon is None or self.df_mon.empty:
            ctk.CTkLabel(scroll, text="No hay datos de monitoreo cargados.",
                         font=(FONTS.family, 14)).pack(pady=50)
            return
        # Header
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))

        title = ctk.CTkFrame(header, fg_color=COLORS.primary, height=38, corner_radius=8)
        title.pack(side="left", padx=(0, 10))
        title.pack_propagate(True)

        ctk.CTkFrame(title, fg_color=COLORS.accent, width=4, height=20,
                     corner_radius=2).place(x=12, y=5)
        ctk.CTkLabel(title, text="DATOS DE MONITOREO",
                     font=(FONTS.family, FONTS.size_lg, "bold"),
                     text_color=COLORS.text_white).pack(side="left", padx=(20, 14))


        h_scroll = ctk.CTkScrollableFrame(scroll, fg_color=COLORS.bg_card,
                                          height=380, orientation="horizontal",
                                          border_width=1, border_color=COLORS.border)
        h_scroll.configure(width=1200)
        h_scroll.pack(pady=(0, 20))

        inner_tbl = ctk.CTkFrame(h_scroll, fg_color="transparent")
        inner_tbl.pack(fill="both", expand=True)

        COL_W = 220
        headers = [
            "Fecha", 
            "Consumo Normalizado\n(kWh/30d)", 
            "Consumo Normalizado y Ajustado\n(kWh)", 
            "LBEn mes\n(kWh)",
            "Desempeño Energético\n(kWh)", 
            "Desempeño Energético\n(%)", 
            "Desempeño Energético Acumulado\n(kWh)",
            "Avance Respecto a Potencial Anual\n(%)", 
            "Avance Respecto a Meta 15%\nAnual Base (%)",
            "Desempeño Económico\n(COP)", 
            "Desempeño Económico Acumulado\n(COP)",
            "Desempeño Ambiental\n(kgCO2e)", 
            "Desempeño Ambiental Acumulado\n(kgCO2e)"
        ]
        h_frame = ctk.CTkFrame(inner_tbl, fg_color=COLORS.primary, height=55) # Altura suficiente para wrapping
        h_frame.pack(fill="x")
        for i, h in enumerate(headers):
            ctk.CTkLabel(h_frame, text=h, text_color="white",
                         font=(FONTS.family, 11, "bold"), 
                         width=COL_W, justify="center", wraplength=200).grid(row=0, column=i, padx=5, sticky="nsew")
        
        # Compensador de Scrollbar (Derecha)
        ctk.CTkLabel(h_frame, text="", width=20).grid(row=0, column=len(headers), padx=0)

        v_scroll = ctk.CTkScrollableFrame(inner_tbl, fg_color="transparent",
                                          height=320, orientation="vertical")
        v_scroll.pack(fill="both", expand=True)

        for _, row in self.df_mon.iterrows():
            r = ctk.CTkFrame(v_scroll, fg_color="transparent")
            r.pack(fill="x", pady=1)

            color_des = COLORS.success if row['Desemp_kWh'] <= 0 else COLORS.danger

            vals = [
                row['Fecha'],
                f"{row['Normalizado']:,.1f}",
                f"{row['Ajustado']:,.1f}",
                f"{row['LBEn_Mes']:,.1f}",
                f"{row['Desemp_kWh']:,.1f}",
                f"{row['Desemp_Pct']:.1f}",     # Sin %
                f"{row['CUSUM_kWh']:,.1f}",
                f"{row['Avance_Pot']:.1f}",      # Sin %
                f"{row['Avance_15']:.1f}",       # Sin %
                f"{row['Desemp_COP']:,.0f}",
                f"{row['CUSUM_COP']:,.0f}",
                f"{row['Desemp_CO2']:,.1f}",
                f"{row['CUSUM_CO2']:,.1f}",
            ]
            for i, v in enumerate(vals):
                txt_c = color_des if i in [4, 5, 6, 9, 10, 11, 12] else COLORS.text_primary
                ctk.CTkLabel(r, text=v, width=COL_W,
                             font=(FONTS.family, FONTS.size_lg),
                             text_color=txt_c, justify="center").grid(row=0, column=i, padx=5, sticky="nsew")
            ctk.CTkFrame(v_scroll, fg_color=COLORS.border, height=1).pack(fill="x")
        
        # Compensador inferior (opcional, para cuadrar con el header)
        # ctk.CTkLabel(r, text="", width=20).grid(row=0, column=len(vals), padx=0)

        # ── Gráfico 1: Real vs Meta ──
        self._chart_seguimiento(scroll)
        # ── Gráfico 2: CUSUM ──
        self._chart_cusum(scroll)

    def _chart_seguimiento(self, parent):
        # Gráfico 1: Seguimiento Real vs Meta
        h1 = ctk.CTkFrame(parent, fg_color="transparent")
        h1.pack(fill="both", expand=True, padx=20, pady=10)

        # 1. Header con Botón Interactivo
        header = ctk.CTkFrame(h1, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))

        title = ctk.CTkFrame(header, fg_color=COLORS.primary, height=38, corner_radius=8)
        title.pack(side="left", padx=(0, 10))
        title.pack_propagate(True)

        ctk.CTkFrame(title, fg_color=COLORS.accent, width=4, height=20, corner_radius=2)\
            .place(x=12, y=5)

        ctk.CTkLabel(title, text="Seguimiento Energético: Real vs Base",
                    font=(FONTS.family, FONTS.size_lg, "bold"),
                    text_color=COLORS.text_white).pack(side="left", padx=(20, 14))

        ctk.CTkButton(header, text="🌐 Ver interactivo",
                    font=(FONTS.family, 10, "bold"),
                    fg_color="transparent", border_width=1,
                    border_color=COLORS.primary, text_color=COLORS.primary, height=28,
                    command=self._abrir_plotly_seguimiento).pack(side="right")

        frame = ctk.CTkFrame(parent, fg_color=COLORS.bg_card, corner_radius=12,
                            border_width=1, border_color=COLORS.border)
        frame.pack(fill="x", pady=5)

        fig, ax = plt.subplots(figsize=(10, 3.5), facecolor=COLORS.bg_card)
        ax.set_facecolor("#F8FAF9")

        fechas = self.df_mon['Fecha']
        lben   = self.df_mon['LBEn_Mes']
        real   = self.df_mon['Ajustado']

        ax.plot(fechas, lben, color=COLORS.primary, linestyle='--', linewidth=2,
                label="Línea Base")
        ax.plot(fechas, real, color=COLORS.azul, marker='o', markersize=5,
                linewidth=1.5, label="Consumo Real")

        lben_arr = np.array(lben, dtype=float)
        ax.fill_between(fechas, lben_arr * 0.9, lben_arr * 1.1,
                        color=COLORS.primary, alpha=0.07, label="Intervalo de Confianza")

        ax.set_ylabel(self.config['unidad'])
        ax.grid(True, linestyle=':', alpha=0.4)

        ax.legend(
            loc='upper center',
            bbox_to_anchor=(0.5, -0.28),
            ncol=3,
            fontsize=8,
            frameon=False
        )

        plt.xticks(rotation=45, ha='right', fontsize=8)
        fig.subplots_adjust(bottom=0.32, left=0.07, right=0.98, top=0.95)

        FigureCanvasTkAgg(fig, master=frame).get_tk_widget().pack(
            fill="both", expand=True, padx=10, pady=10)

    def _chart_cusum(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(20, 5))
        
        title_cusum = ctk.CTkFrame(header, fg_color=COLORS.primary, height=38, corner_radius=8)
        title_cusum.pack(side="left", padx=(0, 10))
        title_cusum.pack_propagate(True)

        ctk.CTkFrame(title_cusum, fg_color=COLORS.accent, width=4, height=20, corner_radius=2)\
            .place(x=12, y=5)
        
        ctk.CTkLabel(title_cusum, text="Desempeño energético Acumulado",
                    font=(FONTS.family, FONTS.size_lg, "bold"),
                    text_color=COLORS.text_white).pack(side="left", padx=(20, 14))
        ctk.CTkButton(header, text="🌐 Ver interactivo",
                    font=(FONTS.family, 10, "bold"),
                    fg_color="transparent", border_width=1,
                    border_color=COLORS.primary, text_color=COLORS.primary, height=28,
                    command=self._abrir_plotly_cusum).pack(side="right")

        frame = ctk.CTkFrame(parent, fg_color=COLORS.bg_card, corner_radius=12,
                            border_width=1, border_color=COLORS.border)
        frame.pack(fill="x", pady=5)

        fig, ax = plt.subplots(figsize=(10, 3.5), facecolor=COLORS.bg_card)
        ax.set_facecolor("#F8FAF9")
        fechas   = self.df_mon['Fecha'].tolist()
        y_cusum  = self.df_mon['CUSUM_kWh'].values

        def get_yr(f):
            try: return int(str(f).split("-")[-1])
            except: return 0

        for i in range(len(y_cusum) - 1):
            if get_yr(fechas[i]) == get_yr(fechas[i + 1]):
                c = COLORS.success if y_cusum[i + 1] <= y_cusum[i] else COLORS.danger
                ax.plot(fechas[i:i + 2], y_cusum[i:i + 2],
                        color=c, linewidth=2, marker='o', markersize=4)
            else:
                ax.plot([fechas[i + 1]], [y_cusum[i + 1]],
                        color=COLORS.primary, marker='o', markersize=4)

        ax.axhline(0, color=COLORS.primary, linestyle='--', alpha=0.5)
        ax.set_ylabel(f"Acumulado ({self.config['unidad']})")
        ax.grid(True, linestyle=':', alpha=0.4)

        # ── Leyenda manual con líneas de color ──────────────────────────────
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color=COLORS.success, linewidth=2, marker='o',
                markersize=4, label="Ahorro"),
            Line2D([0], [0], color=COLORS.danger,  linewidth=2, marker='o',
                markersize=4, label="Sobreconsumo"),
        ]
        ax.legend(
            handles=legend_elements,
            loc='upper center',
            bbox_to_anchor=(0.5, -0.28),
            ncol=2,
            fontsize=8,
            frameon=False
        )

        plt.xticks(rotation=45, ha='right', fontsize=8)
        fig.subplots_adjust(bottom=0.32, left=0.08, right=0.98, top=0.95)

        FigureCanvasTkAgg(fig, master=frame).get_tk_widget().pack(
            fill="both", expand=True, padx=10, pady=10)

    def _abrir_plotly_seguimiento(self):
        try:
            fechas = self.df_mon['Fecha']
            lben   = self.df_mon['LBEn_Mes']
            real   = self.df_mon['Ajustado']
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(fechas) + list(fechas)[::-1],
                y=list(lben * 1.1) + list(lben * 0.9)[::-1],
                fill='toself', fillcolor='rgba(0,100,80,0.08)',
                line=dict(color='rgba(0,0,0,0)'),
                name='Intervalo de Confianza', hoverinfo='skip'))
            fig.add_trace(go.Scatter(
                x=fechas, y=lben, mode='lines',
                name='Línea Base',
                line=dict(color=COLORS.primary, dash='dash', width=2)))
            fig.add_trace(go.Scatter(
                x=fechas, y=real, mode='lines+markers',
                name='Consumo Real',
                line=dict(color=COLORS.azul, width=2),
                marker=dict(size=6)))
            fig.update_layout(
                title="Seguimiento Energético: Real vs Base ",
                xaxis_title="Fecha", yaxis_title=self.config['unidad'],
                template="plotly_white",
                legend=dict(orientation="h", yanchor="bottom", y=-0.3))
            tmp = os.path.join(tempfile.gettempdir(), "seguimiento_m1.html")
            fig.write_html(tmp)
            webbrowser.open(f"file:///{tmp}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el gráfico:\n{e}")

    def _abrir_plotly_cusum(self):
        try:
            fechas  = self.df_mon['Fecha'].tolist()
            y_cusum = self.df_mon['CUSUM_kWh'].values

            def get_yr(f):
                try: return int(str(f).split("-")[-1])
                except: return 0

            fig = go.Figure()

            # Trazos del gráfico (sin leyenda individual)
            for i in range(len(y_cusum) - 1):
                if get_yr(fechas[i]) == get_yr(fechas[i + 1]):
                    c = 'rgb(44,160,44)' if y_cusum[i + 1] <= y_cusum[i] else 'rgb(214,39,40)'
                    fig.add_trace(go.Scatter(
                        x=[fechas[i], fechas[i + 1]],
                        y=[y_cusum[i], y_cusum[i + 1]],
                        mode='lines+markers',
                        line=dict(color=c, width=4),
                        showlegend=False))
                else:
                    fig.add_trace(go.Scatter(
                        x=[fechas[i + 1]], y=[y_cusum[i + 1]],
                        mode='markers',
                        marker=dict(color='gray', size=8),
                        showlegend=False))

            # ── Trazos dummy solo para la leyenda ───────────────────────────
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode='lines+markers',
                line=dict(color='rgb(44,160,44)', width=4),
                marker=dict(color='rgb(44,160,44)', size=8),
                name='Ahorro'
            ))
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode='lines+markers',
                line=dict(color='rgb(214,39,40)', width=4),
                marker=dict(color='rgb(214,39,40)', size=8),
                name='Sobreconsumo'
            ))

            fig.add_hline(y=0, line_dash='dash', line_color=COLORS.primary, opacity=0.5)

            fig.update_layout(
                title="Desempeño Energético Acumulado",
                xaxis_title="Fecha",
                yaxis_title=f"Acumulado ({self.config['unidad']})",
                template="plotly_white",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.25,
                    xanchor="center",
                    x=0.5
                )
            )

            tmp = os.path.join(tempfile.gettempdir(), "cusum_m1.html")
            fig.write_html(tmp)
            webbrowser.open(f"file:///{tmp}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el gráfico:\n{e}")

    # ─────────────────────────────────────────────────────────────────
    # ACCIONES
    # ─────────────────────────────────────────────────────────────────

    def _guardar_excel(self):
        path = self.app.session.get("excel_path")
        if not path:
            messagebox.showwarning("Aviso", "No se encontró la ruta del archivo Excel.")
            return
        self.btn_upd.configure(state="disabled", text="⌛ ESCRIBIENDO...")

        def run():
            try:
                ok = escribir_resultados_m1(
                    path=path,
                    df_lben=self.df_lben,
                    df_mon=self.df_mon,
                    df_base_f=self.df_base_f,
                    df_excluidos=self.df_excl,
                    meta=self.metricas,
                    config=self.config)
                if ok:
                    messagebox.showinfo("Éxito", f"Archivo Excel actualizado:\n{path}")
                else:
                    messagebox.showerror("Error", "No se pudo escribir el archivo Excel.")
            except Exception as e:
                messagebox.showerror("Error", f"Fallo al escribir Excel:\n{e}")
            finally:
                self.after(0, lambda: self.btn_upd.configure(
                    state="normal", text="💾 Actualizar archivo (Excel)"))

        threading.Thread(target=run, daemon=True).start()