"""
ui/pages/m2_resultados.py
=========================
Dashboard de resultados del Modelo M2: Cociente de Valores Medidos.
ADN Visual idéntico al M1. Versión corregida y completa.
"""

import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
import webbrowser
import os
import tempfile
import threading
import plotly.graph_objects as go

from ui.theme import COLORS, FONTS, DIMS
from core.io_excel import escribir_resultados_m2

# Paleta de colores para años (igual que M1)
YEAR_COLORS = ["#2196F3", "#FF9800", "#4CAF50", "#E91E63", "#9C27B0"]
MESES_NOMBRES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                 "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
MESES_ES_EN = {
    'Ene': 'Jan', 'Feb': 'Feb', 'Mar': 'Mar', 'Abr': 'Apr',
    'May': 'May', 'Jun': 'Jun', 'Jul': 'Jul', 'Ago': 'Aug',
    'Sep': 'Sep', 'Oct': 'Oct', 'Nov': 'Nov', 'Dic': 'Dec'
}
# Mapa inverso: inglés -> español (para formatear fechas)
MES_NUM_ES = {1:"Ene", 2:"Feb", 3:"Mar", 4:"Abr", 5:"May", 6:"Jun",
              7:"Jul", 8:"Ago", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dic"}


def safe_to_datetime(val):
    """Convierte un valor a datetime tolerando formatos en español."""
    if isinstance(val, str):
        for es, en in MESES_ES_EN.items():
            if es in val:
                val = val.replace(es, en)
    return pd.to_datetime(val, errors='coerce')


def fmt_fecha_es(dt_val):
    """Formatea un datetime a 'Ene-2024' (español)."""
    try:
        return f"{MES_NUM_ES[dt_val.month]}-{dt_val.year}"
    except Exception:
        return str(dt_val)


class M2ResultadosPage(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS.bg_main, **kwargs)
        self.app = parent

        # Recuperar datos de sesión
        self.df_lben     = self.app.session.get("df_lben")
        self.df_mon      = self.app.session.get("df_monitoreo")
        self.df_base_raw = self.app.session.get("df_base_raw")
        self.df_base_f   = self.app.session.get("df_base_final")
        self.df_exc      = self.app.session.get("df_excluidos")
        self.metricas    = self.app.session.get("metricas_m2") or {}
        self.config      = self.app.session

        self.current_tab = "identificacion"
        self._build()

    # ─────────────────────────────────────────────────────────────────
    # ESTRUCTURA PRINCIPAL  (igual que M1: header / stats / tabs)
    # ─────────────────────────────────────────────────────────────────

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)   # row 2 = content, se expande

        self._build_header()          # row 0
        self._build_kpi_cards()       # row 1
        self._build_tabs_area()       # row 2

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
                      command=lambda: self.app.navegar("m2_carga")
                      ).grid(row=0, column=0, padx=16, pady=8, sticky="w")

        ctk.CTkLabel(topbar,
                     text=f"M2: {self.config.get('nombre', 'Proyecto')}",
                     font=(FONTS.family, FONTS.size_md, "bold"),
                     text_color=COLORS.primary
                     ).grid(row=0, column=1, sticky="w", padx=8)

        self.btn_upd = ctk.CTkButton(
            topbar, text="💾 Actualizar archivo (Excel)",
            font=(FONTS.family, FONTS.size_sm, "bold"),
            fg_color=COLORS.primary, text_color="white", height=32,
            command=self._actualizar_excel)
        self.btn_upd.grid(row=0, column=2, padx=16, pady=8, sticky="e")

    def _build_kpi_cards(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(12, 0))
        frame.grid_columnconfigure((0, 1, 2), weight=1)
        m = self.metricas
        self._kpi_card(frame, 0, "Consumo Promedio Anual",
                       f"{m.get('consumo_promedio_anual', 0):,.0f}", "kWh")
        self._kpi_card(frame, 1, "Ahorro Potencial Anual",
                       f"{m.get('potencial_ahorro_kwh', 0):,.0f}", "kWh",
                       color=COLORS.success)
        self._kpi_card(frame, 2, "Ahorro Potencial (%)",
                       f"{m.get('potencial_ahorro_pct', 0):.1f}%", "Estimado")

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
            ("monitoreo",      "👁️ Monitoreo"),
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
        {"identificacion": self._render_identificacion,
         "lben":           self._render_lben,
         "potenciales":    self._render_potenciales,
         "monitoreo":      self._render_monitoreo}[tab_id]()

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
            ("Nombre Edificio / Entidad",        self.config.get("nombre", "---")),
            ("Fuente de Energía",                self.config.get("fuente", "---"),
            "Unidad de Energía",                self.config.get("unidad", "---")),
            ("Zona Climática",                   self.config.get("zona", "---")),
            ("Área útil (m2)",                   self.config.get("area", "---")),
            ("Variable relevante (Denominador)", self.config.get("var_relevante_nom", "---"),
            "Unidad de la variable relevante",  self.config.get("var_relevante_uni", "---")),
            ("Periodo base — inicio",            self.config.get("pb_ini", "---"),
            "Periodo base — fin",               self.config.get("pb_fin", "---")),
        ])

        # ── Columna derecha: Métricas del modelo ──
        right = ctk.CTkFrame(cols, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        m = self.metricas
        self._tabla_simple(right, "MÉTRICAS DEL MODELO", [
            ("Tipo de Modelo",               "M2 (Cociente de Valores Medidos)"),
            ("N Datos iniciales",            f"{m.get('n_inicial', 0)}"),
            ("N Datos filtrado estadístico", f"{m.get('n_filtrado', 0)}"),
            ("N Datos usados en modelo",     f"{m.get('n_final', 0)}"),
            ("Fiabilidad",               f"{m.get('fiabilidad', 0):.1f}%"),
            ("Meta 15% Anual Base (kWh)",    f"{m.get('meta_15', 0):,.2f}"),
        ])

    def _tabla_simple(self, parent, title, rows, pady=0):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=pady)

        title_row = ctk.CTkFrame(frame, fg_color=COLORS.primary, height=38, corner_radius=8)
        title_row.pack(fill="x")
        title_row.pack_propagate(False)

        ctk.CTkFrame(title_row, fg_color=COLORS.accent, width=4, height=20, corner_radius=2).place(x=12, y=9)
        ctk.CTkLabel(title_row, text=title, font=(FONTS.family, FONTS.size_xl, "bold"),text_color="white", anchor="w").place(x=20, y=19, anchor="w")

        content = ctk.CTkFrame(frame, fg_color=COLORS.bg_card, corner_radius=20,border_width=1, border_color=COLORS.border)
        content.pack(fill="x", padx=10, pady=0)

        for i, row in enumerate(rows):
            # Fila doble: tupla de 4 elementos (label1, val1, label2, val2)
            if len(row) == 4:
                label1, value1, label2, value2 = row
                row_f = ctk.CTkFrame(content, fg_color="transparent", height=35)
                row_f.pack(fill="x", padx=15, pady=2)
                row_f.pack_propagate(False)

                # Mitad izquierda
                left_half = ctk.CTkFrame(row_f, fg_color="transparent")
                left_half.place(relx=0, rely=0, relwidth=0.48, relheight=1.0)

                ctk.CTkLabel(left_half, text=label1,font=(FONTS.family, FONTS.size_md),text_color="#7A8C85", anchor="w").place(relx=0, rely=0.5, anchor="w")
                ctk.CTkLabel(left_half, text=str(value1),font=(FONTS.family, FONTS.size_lg, "bold"),text_color=COLORS.primary, anchor="e").place(relx=1.0, rely=0.5, anchor="e")

                # Separador vertical central
                ctk.CTkFrame(row_f, fg_color=COLORS.border, width=1,corner_radius=0).place(relx=0.5, rely=0.1, relheight=0.8)

                # Mitad derecha
                right_half = ctk.CTkFrame(row_f, fg_color="transparent")
                right_half.place(relx=0.52, rely=0, relwidth=0.48, relheight=1.0)

                ctk.CTkLabel(right_half, text=label2,font=(FONTS.family, FONTS.size_md),text_color="#7A8C85", anchor="w").place(relx=0, rely=0.5, anchor="w")
                ctk.CTkLabel(right_half, text=str(value2),font=(FONTS.family, FONTS.size_lg, "bold"),text_color=COLORS.primary, anchor="e").place(relx=1.0, rely=0.5, anchor="e")

            # Fila simple: tupla de 2 elementos (comportamiento original)
            else:
                label, value = row
                row_f = ctk.CTkFrame(content, fg_color="transparent", height=35)
                row_f.pack(fill="x", padx=15, pady=2)

                ctk.CTkLabel(row_f, text=label,font=(FONTS.family, FONTS.size_md),text_color="#7A8C85", anchor="w").place(relx=0, rely=0.5, anchor="w")
                ctk.CTkLabel(row_f, text=str(value),font=(FONTS.family, FONTS.size_lg, "bold"),text_color=COLORS.primary, anchor="e").place(relx=1.0, rely=0.5, anchor="e")

            if i < len(rows) - 1:
                ctk.CTkFrame(content, fg_color=COLORS.border, height=1,corner_radius=0).pack(fill="x", padx=10)

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

        ctk.CTkFrame(title, fg_color=COLORS.accent, width=4, height=20, corner_radius=2)\
            .place(x=12, y=5)
        
        ctk.CTkLabel(title, text="Comportamiento de la Línea Base",
                     font=(FONTS.family, FONTS.size_lg, "bold"),
                     text_color=COLORS.text_white).pack(side="left", padx=(20, 14))
        ctk.CTkButton(header, text="🌐 Ver interactivo en navegador",
                      font=(FONTS.family, FONTS.size_sm, "bold"), fg_color="transparent",
                      border_width=1, border_color=COLORS.primary,
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
            col_fecha = df_pts.columns[0]
            df_pts["Fecha_DT"] = df_pts[col_fecha].apply(safe_to_datetime)
            df_pts["mes_n"] = df_pts["Fecha_DT"].dt.month
            df_pts["año"]   = df_pts["Fecha_DT"].dt.year
            for i, yr in enumerate(sorted(df_pts["año"].dropna().unique())):
                dy = df_pts[df_pts["año"] == yr]
                ax.scatter(dy["mes_n"], dy["Cociente"],
                           color=YEAR_COLORS[i % len(YEAR_COLORS)],
                           alpha=0.7, label=f"Año {int(yr)}",
                           edgecolors="white", s=40)

        # B. LBEn promedio
        ax.plot(x_ticks, self.df_lben["lben"], color=COLORS.primary,
                linewidth=2.5, label="Promedio (LBEn)", marker="o", markersize=6)

        # C. Mínimo histórico (meta)
        if "min_hist" in self.df_lben.columns:
            ax.plot(x_ticks, self.df_lben["min_hist"], color=COLORS.success,
                    linewidth=2, linestyle="--", label="Línea Meta")

        # D. Banda de confianza
        ax.fill_between(x_ticks, self.df_lben["lim_inf"], self.df_lben["lim_sup"],
                        color=COLORS.primary, alpha=0.1, label="Confianza (±)")

        ax.set_xticks(x_ticks)
        ax.set_xticklabels(MESES_NOMBRES)
        ax.set_ylabel("Cociente (E / Var. Relevante)")
        ax.grid(True, linestyle=":", alpha=0.4)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=4, fontsize=8)
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

        ctk.CTkFrame(title, fg_color=COLORS.accent, width=4, height=16, corner_radius=2)\
            .place(x=12, y=5)

        ctk.CTkLabel(title,text="TABLA LBEn MENSUAL",font=(FONTS.family, FONTS.size_lg, "bold"),text_color=COLORS.text_white).pack(side="left", padx=(20, 14))

        tbl = ctk.CTkScrollableFrame(frame, fg_color=COLORS.bg_card,
                                     height=430, orientation="horizontal",
                                     border_width=1, border_color=COLORS.border,width=870)
        tbl.pack(pady=0)
        tbl.pack_configure(anchor="center")

        COL_W = 160
        headers = ["Mes", "LBEn (Cociente)", "N Datos",
                   "Límite Inf. (Cociente)", "Límite Sup. (Cociente)"]
        h_frame = ctk.CTkFrame(tbl, fg_color=COLORS.primary, height=35)
        h_frame.pack(fill="x")
        for i, h in enumerate(headers):
            ctk.CTkLabel(h_frame, text=h, text_color="white",
                         font=(FONTS.family, 11, "bold"), width=COL_W).grid(row=0, column=i, padx=5)

        for _, row in self.df_lben.iterrows():
            r = ctk.CTkFrame(tbl, fg_color="transparent")
            r.pack(fill="x", pady=1)
            ctk.CTkLabel(r, text=str(row["mes"]),          width=COL_W, font=(FONTS.family, 11)).grid(row=0, column=0, padx=5)
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
                col_fecha = df_pts.columns[0]
                df_pts["Fecha_DT"] = df_pts[col_fecha].apply(safe_to_datetime)
                df_pts["mes_n"] = df_pts["Fecha_DT"].dt.month
                df_pts["año"]   = df_pts["Fecha_DT"].dt.year
                for i, yr in enumerate(sorted(df_pts["año"].dropna().unique())):
                    dy = df_pts[df_pts["año"] == yr]
                    fig.add_trace(go.Scatter(
                        x=dy["mes_n"], y=dy["Cociente"], mode="markers",
                        name=f"Año {int(yr)}",
                        marker=dict(color=YEAR_COLORS[i % len(YEAR_COLORS)], size=8)))
            fig.add_trace(go.Scatter(
                x=x_ticks, y=self.df_lben["lben"], mode="lines+markers",
                name="Promedio (LBEn)", line=dict(color=COLORS.primary, width=3)))
            if "min_hist" in self.df_lben.columns:
                fig.add_trace(go.Scatter(
                    x=x_ticks, y=self.df_lben["min_hist"], mode="lines",
                    name="Línea Meta", line=dict(color=COLORS.success, dash="dash")))
            lim_sup = list(self.df_lben["lim_sup"])
            lim_inf = list(self.df_lben["lim_inf"])
            fig.add_trace(go.Scatter(
                x=x_ticks + x_ticks[::-1], y=lim_sup + lim_inf[::-1],
                fill="toself", fillcolor="rgba(30,100,60,0.1)",
                line=dict(color="rgba(0,0,0,0)"), name="Confianza"))
            fig.update_xaxes(tickvals=x_ticks, ticktext=MESES_NOMBRES)
            fig.update_layout(title="Comportamiento Línea Base M2 — Interactivo",
                              template="plotly_white", xaxis_title="Mes",
                              yaxis_title="Cociente (E/Var. Relevante)")
            tmp = os.path.join(tempfile.gettempdir(), "lben_m2.html")
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
        tbl.configure(width=1080)
        tbl.pack()
        tbl.pack_configure(anchor="center")

        COL_W = 175
        headers = ["Mes", "LBEn (Cociente)", "Mín. Histórico",
                   "Ahorro Pot. (Cociente)", "Ahorro (kWh)", "Ahorro (%)"]
        h_frame = ctk.CTkFrame(tbl, fg_color=COLORS.primary, height=45)
        h_frame.pack(fill="x")
        for i, h in enumerate(headers):
            ctk.CTkLabel(h_frame, text=h, text_color="white",
                         font=(FONTS.family, 11, "bold"),
                         width=COL_W, wraplength=160).grid(row=0, column=i, padx=5, pady=5)

        for row_data in self.metricas.get("tabla_potenciales", []):
            is_total = str(row_data[0]).upper() == "PROMEDIO ANUAL"
            r = ctk.CTkFrame(tbl, fg_color="transparent")
            r.pack(fill="x", pady=1)
            fmts = [str, "{:,.2f}".format, "{:,.2f}".format,
                    "{:,.2f}".format, "{:,.0f}".format, "{:.1f}%".format]
            for c_idx, (val, fmt) in enumerate(zip(row_data, fmts)):
                try:
                    txt = fmt(val) if callable(fmt) else fmt.format(val)
                except Exception:
                    txt = str(val)
                ctk.CTkLabel(r, text=txt, width=COL_W,
                             font=(FONTS.family, 11, "bold" if is_total else "normal"),
                             text_color=COLORS.primary if is_total else COLORS.text_primary
                             ).grid(row=0, column=c_idx, padx=5)
            if not is_total:
                ctk.CTkFrame(tbl, fg_color=COLORS.border, height=1).pack(fill="x")

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

        # Preparar fechas en español
        dfm = self.df_mon.copy()
        col_f = dfm.columns[0]
        dfm["Fecha_DT"] = dfm[col_f].apply(safe_to_datetime)
        dfm = dfm.dropna(subset=["Fecha_DT"])
        dfm["FechaStr"] = dfm["Fecha_DT"].apply(fmt_fecha_es)

        # ── Tabla ──
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

        # 1. Contenedor Horizontal Exterior
        h_scroll = ctk.CTkScrollableFrame(scroll, fg_color=COLORS.bg_card,
                                     height=380, orientation="horizontal",
                                     border_width=1, border_color=COLORS.border)
        h_scroll.configure(width=1200)
        h_scroll.pack(pady=(0, 20))
        h_scroll.pack_configure(anchor="center")

        # 2. Frame interno para Header + Body
        inner_tbl = ctk.CTkFrame(h_scroll, fg_color="transparent")
        inner_tbl.pack(fill="both", expand=True)

        COL_W = 140
        headers = [
            "Fecha", "Norm. (kWh)", "Cociente", "LBEn (kWh)", 
            "Desemp. (kWh)", "Desemp. (%)", "CUSUM (kWh)", 
            "Avance Pot. (%)", "Avance 15% (%)", 
            "Econ. ($)", "Eco Acum. ($)", 
            "Amb. (CO2)", "Amb. Acu (CO2)"
        ]
        
        h_frame = ctk.CTkFrame(inner_tbl, fg_color=COLORS.primary, height=35)
        h_frame.pack(fill="x")
        for i, h in enumerate(headers):
            ctk.CTkLabel(h_frame, text=h, text_color="white",
                         font=(FONTS.family, FONTS.size_lg, "bold"), width=COL_W).grid(row=0, column=i, padx=5)

        # 3. Contenedor Vertical para las filas
        v_scroll = ctk.CTkScrollableFrame(inner_tbl, fg_color="transparent", height=320, orientation="vertical")
        v_scroll.pack(fill="both", expand=True)

        col_map = [
            "FechaStr", "Cons_Num", "Cociente_Real", "LBEn_Ratio",
            "Desemp_kWh", "Desemp_Pct", "CUSUM_kWh",
            "Avance_Pot", "Avance_15", 
            "Desemp_COP", "CUSUM_COP", "Desemp_CO2", "CUSUM_CO2"
        ]
        for _, row in dfm.iterrows():
            r = ctk.CTkFrame(v_scroll, fg_color="transparent")
            r.pack(fill="x", pady=1)
            for c_idx, col in enumerate(col_map):
                val = row.get(col, "---")
                color = COLORS.text_primary
                
                # Resaltar en rojo/verde columnas de desempeño
                # Indices: 4(Desemp), 5(%), 6(CUSUM), 9(Econ), 10(Econ Acu), 11(Amb), 12(Amb Acu)
                if c_idx in [4, 5, 6, 9, 10, 11, 12]:
                    try:
                        # Usamos Desemp_kWh (col 4) para decidir el color de todo el bloque de desempeño
                        des_val = float(row.get("Desemp_kWh", 0))
                        color = COLORS.success if des_val <= 0 else COLORS.danger
                    except: pass

                # Formateo según tipo
                if c_idx in [5, 7, 8]: # Porcentajes
                    txt = f"{float(val):.1f}%" if isinstance(val, (int, float)) else str(val)
                elif c_idx in [9, 10]: # COP (Sin decimales)
                    txt = f"{float(val):,.0f}" if isinstance(val, (int, float)) else str(val)
                elif isinstance(val, (int, float)):
                    txt = f"{val:,.1f}"
                else:
                    txt = str(val)

                ctk.CTkLabel(r, text=txt, width=COL_W,
                             font=(FONTS.family, FONTS.size_lg), text_color=color
                             ).grid(row=0, column=c_idx, padx=5)
            ctk.CTkFrame(v_scroll, fg_color=COLORS.border, height=1).pack(fill="x")

        # ── Gráfico 1: Real vs Meta ──
        self._chart_seguimiento(scroll, dfm)
        # ── Gráfico 2: CUSUM ──
        self._chart_cusum(scroll, dfm)

    def _chart_seguimiento(self, parent, dfm):
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

        ctk.CTkLabel(title, text="Seguimiento Energético: Real vs Meta",
                    font=(FONTS.family, FONTS.size_lg, "bold"),
                    text_color=COLORS.text_white).pack(side="left", padx=(20, 14))
        ctk.CTkButton(header, text="🌐 Ver interactivo", font=(FONTS.family, 10, "bold"),
                      fg_color="transparent", border_width=1,
                      border_color=COLORS.primary, text_color=COLORS.primary, height=28,
                      command=lambda: self._plotly_seguimiento(dfm)).pack(side="right")
        frame = ctk.CTkFrame(parent, fg_color=COLORS.bg_card, corner_radius=12,
                             border_width=1, border_color=COLORS.border)
        frame.pack(fill="x", pady=5)

        fig, ax = plt.subplots(figsize=(10, 3.5), facecolor=COLORS.bg_card)
        ax.set_facecolor("#F8FAF9")
        fechas = dfm["FechaStr"].tolist()
        lben   = pd.to_numeric(dfm["LBEn_Ratio"],    errors="coerce").tolist()
        real   = pd.to_numeric(dfm["Cociente_Real"],  errors="coerce").tolist()
        ax.plot(fechas, lben, color=COLORS.primary, linestyle="--", linewidth=2,
                label="Línea Meta")
        ax.plot(fechas, real, color=COLORS.azul, marker="o", markersize=5,
                linewidth=1.5, label="Cociente Real")
        lben_arr = np.array(lben, dtype=float)
        ax.fill_between(fechas, lben_arr * 0.9, lben_arr * 1.1,
                        color=COLORS.primary, alpha=0.07, label="Zona de Control")
        ax.set_ylabel("Cociente (E/Var)")
        ax.grid(True, linestyle=":", alpha=0.4)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3, fontsize=8)
        plt.xticks(rotation=45, ha="right", fontsize=8)
        plt.tight_layout()
        FigureCanvasTkAgg(fig, master=frame).get_tk_widget().pack(
            fill="both", expand=True, padx=10, pady=10)

    def _chart_cusum(self, parent, dfm):
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
        ctk.CTkButton(header, text="🌐 Ver interactivo", font=(FONTS.family, 10, "bold"),
                      fg_color="transparent", border_width=1,
                      border_color=COLORS.primary, text_color=COLORS.primary, height=28,
                      command=lambda: self._plotly_cusum(dfm)).pack(side="right")
        frame = ctk.CTkFrame(parent, fg_color=COLORS.bg_card, corner_radius=12,
                             border_width=1, border_color=COLORS.border)
        frame.pack(fill="x", pady=5)

        fig, ax = plt.subplots(figsize=(10, 3.5), facecolor=COLORS.bg_card)
        ax.set_facecolor("#F8FAF9")
        fechas = dfm["FechaStr"].tolist()
        cusum  = pd.to_numeric(dfm["CUSUM_kWh"], errors="coerce").tolist()
        años   = dfm["Fecha_DT"].dt.year.tolist()
        # Color por tramo según pendiente y EVITAR unión Dic-Ene
        for i in range(1, len(fechas)):
            if años[i] == años[i-1]:
                # Si el valor actual es mayor al anterior, la pendiente sube (mal -> rojo)
                c = COLORS.danger if cusum[i] > cusum[i-1] else COLORS.success
                ax.plot(fechas[i-1:i+1], cusum[i-1:i+1], color=c, linewidth=2, marker="o", markersize=4)
            else:
                # Punto inicial del nuevo ciclo
                ax.plot([fechas[i]], [cusum[i]], color=COLORS.primary, marker="o", markersize=4)
        ax.axhline(0, color=COLORS.primary, linestyle="--", alpha=0.5)
        ax.set_ylabel("CUSUM (kWh)")
        ax.grid(True, linestyle=":", alpha=0.4)
        plt.xticks(rotation=45, ha="right", fontsize=8)
        plt.tight_layout()
        FigureCanvasTkAgg(fig, master=frame).get_tk_widget().pack(
            fill="both", expand=True, padx=10, pady=10)

    def _plotly_seguimiento(self, dfm):
        try:
            fechas = dfm["FechaStr"].tolist()
            fig = go.Figure()
            lben = pd.to_numeric(dfm["LBEn_Ratio"],   errors="coerce")
            real = pd.to_numeric(dfm["Cociente_Real"], errors="coerce")
            fig.add_trace(go.Scatter(x=fechas, y=lben, mode="lines",
                                     name="Línea Meta",
                                     line=dict(color=COLORS.primary, dash="dash", width=2)))
            fig.add_trace(go.Scatter(x=fechas, y=real, mode="lines+markers",
                                     name="Cociente Real",
                                     line=dict(color=COLORS.azul, width=2),
                                     marker=dict(size=6)))
            # Banda de zona de control
            fig.add_trace(go.Scatter(
                x=fechas + fechas[::-1],
                y=list(lben * 1.1) + list(lben * 0.9)[::-1],
                fill="toself", fillcolor="rgba(30,100,60,0.08)",
                line=dict(color="rgba(0,0,0,0)"), name="Zona de Control"))
            fig.update_layout(title="Seguimiento Energético: Real vs Meta — Interactivo",
                              xaxis_title="Período", yaxis_title="Cociente (E/Var)",
                              template="plotly_white",
                              legend=dict(orientation="h", yanchor="bottom", y=-0.3))
            tmp = os.path.join(tempfile.gettempdir(), "seguimiento_m2.html")
            fig.write_html(tmp)
            webbrowser.open(f"file:///{tmp}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el gráfico:\n{e}")

    def _plotly_cusum(self, dfm):
        try:
            fechas = dfm["FechaStr"].tolist()
            cusum  = pd.to_numeric(dfm["CUSUM_kWh"], errors="coerce").tolist()
            años   = dfm["Fecha_DT"].dt.year.tolist()
            fig = go.Figure()
            
            for i in range(len(cusum)-1):
                # Solo dibujar segmento si es el mismo año
                if años[i] == años[i+1]:
                    c = 'rgb(44, 160, 44)' if cusum[i+1] <= cusum[i] else 'rgb(214, 39, 40)'
                    fig.add_trace(go.Scatter(
                        x=[fechas[i], fechas[i+1]], 
                        y=[cusum[i], cusum[i+1]],
                        mode="lines+markers", 
                        line=dict(color=c, width=4), 
                        showlegend=False
                    ))
                else:
                    # Punto final de año
                    fig.add_trace(go.Scatter(x=[fechas[i]], y=[cusum[i]], mode='markers', 
                                             marker=dict(color='gray', size=8), showlegend=False))
            
            fig.add_hline(y=0, line_dash="dash", line_color=COLORS.primary, opacity=0.5)
            fig.update_layout(title="CUSUM — Desempeño Energético Acumulado — Interactivo",
                              xaxis_title="Período", yaxis_title="CUSUM (kWh)",
                              template="plotly_white")
            tmp = os.path.join(tempfile.gettempdir(), "cusum_m2.html")
            fig.write_html(tmp)
            webbrowser.open(f"file:///{tmp}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el gráfico:\n{e}")

    # ─────────────────────────────────────────────────────────────────
    # ACCIONES
    # ─────────────────────────────────────────────────────────────────

    def _actualizar_excel(self):
        dest = self.config.get("excel_path")
        if not dest:
            messagebox.showwarning("Aviso", "No se encontró la ruta del archivo Excel.")
            return
        self.btn_upd.configure(state="disabled", text="⌛ ESCRIBIENDO...")

        def run():
            try:
                ok = escribir_resultados_m2(
                    dest, self.df_lben, self.df_mon,
                    self.df_base_f, self.df_exc,
                    self.metricas, self.config)
                if ok:
                    messagebox.showinfo("Éxito", "Archivo Excel actualizado correctamente.")
                else:
                    messagebox.showerror("Error", "No se pudo escribir el archivo Excel.")
            except Exception as e:
                messagebox.showerror("Error", f"Fallo al escribir Excel:\n{e}")
            finally:
                self.after(0, lambda: self.btn_upd.configure(
                    state="normal", text="💾 Actualizar archivo (Excel)"))

        threading.Thread(target=run, daemon=True).start()
