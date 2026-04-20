"""
ui/pages/m3_resultados.py
=========================
Dashboard de resultados del Modelo M3: Regresión Lineal Multivariable.
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
from core.io_excel import escribir_resultados_m3
from core.models.m3_regresion import formatear_ecuacion

# Helper Colors
YEAR_COLORS = ["#2196F3", "#FF9800", "#4CAF50", "#E91E63", "#9C27B0"]
MES_NUM_ES = {1:"Ene", 2:"Feb", 3:"Mar", 4:"Abr", 5:"May", 6:"Jun", 7:"Jul", 8:"Ago", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dic"}

def safe_to_datetime(val):
    MESES_ES_EN = {'Ene':'Jan', 'Feb':'Feb', 'Mar':'Mar', 'Abr':'Apr', 'May':'May', 'Jun':'Jun', 'Jul':'Jul', 'Ago':'Aug', 'Sep':'Sep', 'Oct':'Oct', 'Nov':'Nov', 'Dic':'Dec'}
    if isinstance(val, str):
        for es, en in MESES_ES_EN.items():
            if es in val: val = val.replace(es, en)
    return pd.to_datetime(val, errors='coerce')

def fmt_fecha_es(dt_val):
    try: return f"{MES_NUM_ES[dt_val.month]}-{dt_val.year}"
    except: return str(dt_val)

class M3ResultadosPage(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS.bg_main, **kwargs)
        self.app = parent
        self.res = self.app.session.get("results_m3")
        self.config = self.app.session.get("m3_config")
        self.current_tab = "identificacion"
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._build_header()
        self._build_kpi_cards()
        self._build_tabs_area()

    def _build_header(self):
        topbar = ctk.CTkFrame(self, fg_color=COLORS.bg_card, height=DIMS.topbar_height, corner_radius=0)
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)
        ctk.CTkFrame(topbar, fg_color=COLORS.accent, height=2).place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        ctk.CTkButton(topbar, text="← Volver a Carga", font=(FONTS.family, FONTS.size_sm), fg_color="transparent",
                     text_color=COLORS.primary, command=lambda: self.app.navegar("m3_carga")).grid(row=0, column=0, padx=16)

        ctk.CTkLabel(topbar, text=f"M3: {self.config.get('nombre')}", font=(FONTS.family, FONTS.size_md, "bold"),
                     text_color=COLORS.primary).grid(row=0, column=1, sticky="w")

        self.btn_upd = ctk.CTkButton(topbar, text="💾 Actualizar archivo (Excel)", font=(FONTS.family, FONTS.size_sm, "bold"),
                                    fg_color=COLORS.primary, text_color="white", height=32, command=self._actualizar_excel)
        self.btn_upd.grid(row=0, column=2, padx=16, pady=8, sticky="e")

    def _build_kpi_cards(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(12, 0))
        frame.grid_columnconfigure((0, 1, 2), weight=1)
        p = self.res['potenciales']
        self._kpi_card(frame, 0, "Consumo Promedio Anual", f"{p['prom_real']*12:,.0f}", "kWh")
        self._kpi_card(frame, 1, "Ahorro Potencial Anual", f"{p['ahorro_kwh']*12:,.0f}", "kWh")
        self._kpi_card(frame, 2, "Ahorro Potencial (%)", f"{p['ahorro_pct']:.1f}%", "Estimado")

    def _kpi_card(self, parent, col, title, value, unit, color=None):
        c = ctk.CTkFrame(parent, fg_color=COLORS.bg_card, corner_radius=16,
                        border_width=2, border_color=COLORS.border)
        c.grid(row=0, column=col, padx=8, pady=6, sticky="ew", ipady=4)
        c.grid_columnconfigure(0, weight=1)
        c.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(c, text=title, font=(FONTS.family, FONTS.size_lg),
                     text_color=COLORS.text_secondary, anchor="center").grid(row=0, column=0, padx=14, pady=(8, 0), sticky="ew")
        ctk.CTkFrame(c, height=1, fg_color=COLORS.border).grid(row=1, column=0, padx=20, pady=(6, 0), sticky="ew")
        ctk.CTkLabel(c, text=value, font=(FONTS.family, 26, "bold"),
                     text_color=color if color else COLORS.text_primary, anchor="center").grid(row=2, column=0, padx=14, pady=(4, 0), sticky="ew")
        ctk.CTkLabel(c, text=unit, font=(FONTS.family, FONTS.size_sm),
                     text_color=COLORS.text_secondary, anchor="center").grid(row=3, column=0, padx=14, pady=(2, 0), sticky="ew")
        ctk.CTkFrame(c, height=4, width=20,
                     fg_color=color if color else COLORS.border, corner_radius=4).grid(row=4, column=0, pady=(6, 10))

    def _build_tabs_area(self):
        tabs_container = ctk.CTkFrame(self, fg_color="transparent")
        tabs_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        tabs_container.grid_columnconfigure(0, weight=1)
        tabs_container.grid_rowconfigure(1, weight=1)

        nav = ctk.CTkFrame(tabs_container, fg_color="transparent")
        nav.grid(row=0, column=0, pady=(0, 10))
        self.nav_buttons = {}
        tabs = [
            ("identificacion", "📝 Identificación"),
            ("diag",           "📊 Línea Base"),
            ("potenciales",    "📉 Potenciales"),
            ("monitoreo",      "👁️ Monitoreo"),
        ]
        for i, (tid, lbl) in enumerate(tabs):
            btn = ctk.CTkButton(nav, text=lbl, font=(FONTS.family, FONTS.size_sm),
                                fg_color=COLORS.border, text_color=COLORS.text_primary,
                                width=150, height=36, command=lambda t=tid: self._change_tab(t))
            btn.grid(row=0, column=i, padx=5)
            self.nav_buttons[tid] = btn

        self.content_view = ctk.CTkFrame(tabs_container, fg_color="transparent")
        self.content_view.grid(row=1, column=0, sticky="nsew")
        self.content_view.grid_columnconfigure(0, weight=1)
        self.content_view.grid_rowconfigure(0, weight=1)
        self._change_tab("identificacion")

    def _change_tab(self, tid):
        self.current_tab = tid
        for k, b in self.nav_buttons.items():
            b.configure(fg_color=COLORS.primary if k == tid else COLORS.border,
                        text_color=COLORS.text_white if k == tid else COLORS.text_primary)
        for w in self.content_view.winfo_children():
            w.destroy()
        plt.close("all")
        if tid == "identificacion": self._render_identificacion()
        elif tid == "diag":         self._render_diag()
        elif tid == "potenciales":  self._render_potenciales()
        else:                       self._render_monitoreo()

    # ──────────────────────────────────────────────────────────────────────────
    # TAB: IDENTIFICACIÓN
    # ──────────────────────────────────────────────────────────────────────────
    def _render_identificacion(self):
        scroll = ctk.CTkScrollableFrame(self.content_view, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        scroll.grid_columnconfigure(0, weight=1)

        cols = ctk.CTkFrame(scroll, fg_color="transparent")
        cols.pack(fill="both", expand=True)
        cols.grid_columnconfigure(0, weight=1)
        cols.grid_columnconfigure(1, weight=1)

        left = ctk.CTkFrame(cols, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        m = self.res['metrics']
        p = self.res['potenciales']
        ct = self.res['coef_table']

        # Alerta VIF
        vifs_altos = [ct['vars'][i] for i, v in enumerate(ct['vif']) if not np.isnan(v) and v > 5]
        if vifs_altos:
            f_col = ctk.CTkFrame(scroll, fg_color=COLORS.bg_main, corner_radius=12,
                                 border_width=2, border_color=COLORS.warning)
            f_col.pack(fill="x", pady=(10, 20), padx=5)
            ctk.CTkLabel(f_col, text="⚠️ ALERTA DE COLINEALIDAD DETECTADA",
                         font=(FONTS.family, 13, "bold"), text_color=COLORS.warning).pack(pady=(10, 5))
            msg = (f"Las variables {', '.join(vifs_altos)} tienen un VIF superior a 5.0.\n"
                   "Esto indica redundancia técnica que puede afectar la precisión del modelo.\n"
                   "Se recomienda revisar la fase exploratoria y reducir predictores.")
            ctk.CTkLabel(f_col, text=msg, font=(FONTS.family, 11),
                         text_color=COLORS.text_primary, justify="center").pack(pady=(0, 15), padx=20)

        id_rows = [
            ("Entidad",      self.config['nombre']),
            ("Fuente",       self.config['fuente']),
            ("Unidad",       self.config['unidad']),
            ("Zona",         self.config['zona']),
            ("Área útil (m²)", self.config['area']),
        ]
        for i, v in enumerate(self.config['vars_ind']):
            id_rows.append((f"Variable {i+1}", v))

        self._tabla_simple(left, "Identificación del Proyecto", id_rows)

        right = ctk.CTkFrame(cols, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self._tabla_simple(right, "Métricas del Modelo", [
            ("Tipo de Modelo",        "M3 (Regresión Multivariable)"),
            ("R² Ajustado",           f"{m['r2_adj']*100:.2f}%"),
            ("RMSE (Error)",          f"{m['rmse']:,.2f}"),
            ("N registros totales",   f"{len(self.res['df_base']) + len(self.res['df_excluidos'])}"),
            ("N filtrados",           f"{len(self.res['df_excluidos'])}"),
            ("Periodo Base",          f"{self.app.session['pb_ini']}",
             "Periodo Fin",           f"{self.app.session['pb_fin']}"),
            ("Meta 15% (kWh/año)",    f"{p['prom_real']*12*0.15:,.2f}"),
        ])

    # ──────────────────────────────────────────────────────────────────────────
    # TAB: LÍNEA BASE  –  layout 2×2
    # ──────────────────────────────────────────────────────────────────────────
    def _render_diag(self):
            scroll = ctk.CTkScrollableFrame(self.content_view, fg_color="transparent")
            scroll.grid(row=0, column=0, sticky="nsew")
            scroll.grid_columnconfigure(0, weight=1)

            m  = self.res['metrics']
            ct = self.res['coef_table']

            # ── SECCIÓN DE ECUACIONES (APILADAS Y CENTRADAS) ────────────────────
            eq_container = ctk.CTkFrame(scroll, fg_color="transparent")
            eq_container.pack(fill="x", pady=(5, 15))
            
            txt_lben = f"LBEn: {formatear_ecuacion(self.res['model_lben'], self.config['vars_ind'])}"
            txt_lmen = f"LMEn: {formatear_ecuacion(self.res['model_lmen'], self.config['vars_ind'])}"

            eq_badge = ctk.CTkFrame(eq_container, fg_color=COLORS.bg_card, corner_radius=15, 
                                    border_width=1, border_color=COLORS.border)
            eq_badge.pack(anchor="center", padx=20)

            ctk.CTkLabel(
                eq_badge, text=txt_lben, 
                font=(FONTS.family, FONTS.size_sm),
                text_color=COLORS.primary,
                wraplength=800
            ).pack(fill="x", padx=20, pady=(10, 2))
            
            # Línea divisoria horizontal sutil
            ctk.CTkFrame(eq_badge, fg_color=COLORS.border, height=1).pack(fill="x", padx=40, pady=(0, 2))
            
            ctk.CTkLabel(
                eq_badge, text=txt_lmen, 
                font=(FONTS.family, FONTS.size_sm),
                text_color=COLORS.primary,
                wraplength=800
            ).pack(fill="x", padx=20, pady=(2, 10))

            # ── FILA SUPERIOR: Tabla 1 | Tabla 2 ────────────────────────────────
            row_top = ctk.CTkFrame(scroll, fg_color="transparent")
            row_top.pack(fill="x", pady=(0, 12))
            row_top.grid_columnconfigure((0, 1), weight=1, uniform="top")

            self._tabla_simple(row_top, "1. Resumen Estadístico Global", [
                ("Coef. Determinación (R²)", f"{m['r2']:.4f}"),
                ("R² Ajustado",              f"{m['r2_adj']:.4f}"),
                ("RMSE (Error Estándar)",    f"{m['rmse']:,.2f}"),
                ("CV(RMSE) %",               f"{m['cv_rmse']:.2f}%"),
                ("Estadístico F (p-valor)",  f"{m['f_pval']:.4f}"),
            ], grid_pos=(0, 0), grid_padx=(0, 6))

            # ── TABLA 2: COEFICIENTES ───────────────────────────────────────────
            t2 = ctk.CTkFrame(row_top, fg_color="transparent")
            t2.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
            self._titulo_seccion(t2, "2. Tabla de coeficientes")

            ct_card = ctk.CTkFrame(t2, fg_color=COLORS.bg_card, corner_radius=12, 
                                border_width=1, border_color=COLORS.border)
            ct_card.pack(fill="both", expand=True, padx=10, pady=(5, 5))

            h_f = ctk.CTkFrame(ct_card, fg_color=COLORS.primary, corner_radius=0, height=35)
            h_f.pack(fill="x", padx=1, pady=(1, 0)) 
            h_f.pack_propagate(False)

            headers_ct = ["Variable", "Coeficiente", "Err. Est.", "p-valor", "VIF"]
            rel_widths_ct = [0.30, 0.175, 0.175, 0.175, 0.175]

            for i, h in enumerate(headers_ct):
                ctk.CTkLabel(h_f, text=h, text_color="white", font=(FONTS.family, FONTS.size_lg, "bold"),
                            anchor="center").place(relx=sum(rel_widths_ct[:i]), rely=0.5, relwidth=rel_widths_ct[i], anchor="w")

            rows_ct_cont = ctk.CTkFrame(ct_card, fg_color="transparent")
            rows_ct_cont.pack(fill="both", expand=True, padx=5, pady=5)

            for i in range(len(ct['vars'])):
                row_f = ctk.CTkFrame(rows_ct_cont, fg_color="transparent", height=32)
                row_f.pack(fill="x")
                row_f.pack_propagate(False)
                
                vals = [ct['vars'][i], f"{ct['betas'][i]:,.4f}", f"{ct['std_err'][i]:,.4f}", 
                        f"{ct['p_vals'][i]:,.4f}", "---" if np.isnan(ct['vif'][i]) else f"{ct['vif'][i]:.2f}"]

                for j, val in enumerate(vals):
                    ctk.CTkLabel(row_f, text=val, font=(FONTS.family, FONTS.size_lg), text_color=COLORS.text_primary,
                                anchor="center").place(relx=sum(rel_widths_ct[:j]), rely=0.5, relwidth=rel_widths_ct[j], anchor="w")

                if i < len(ct['vars']) - 1:
                    ctk.CTkFrame(rows_ct_cont, fg_color=COLORS.border, height=1).pack(fill="x", padx=10)

            # ── FILA INFERIOR: Tabla 3 | Tabla 4 ────────────────────────────────
            row_bot = ctk.CTkFrame(scroll, fg_color="transparent")
            row_bot.pack(fill="x", pady=(0, 12))
            row_bot.grid_columnconfigure((0, 1), weight=1, uniform="bot")

            # ── TABLA 3: CORRELACIONES ──────────────────────────────────────────
            t3 = ctk.CTkFrame(row_bot, fg_color="transparent")
            t3.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
            self._titulo_seccion(t3, "3. Correlaciones de Pearson")

            cp_card = ctk.CTkFrame(t3, fg_color=COLORS.bg_card, corner_radius=12, 
                                border_width=1, border_color=COLORS.border)
            cp_card.pack(fill="both", expand=True, padx=10, pady=(5, 5))

            cp_h_f = ctk.CTkFrame(cp_card, fg_color=COLORS.primary, corner_radius=0, height=35)
            cp_h_f.pack(fill="x", padx=1, pady=(1, 0))
            cp_h_f.pack_propagate(False)

            headers_cp = ["Variable", "r (Pearson)", "p-valor", "Grado Influencia"]
            rel_widths_cp = [0.35, 0.20, 0.20, 0.25]

            for i, h in enumerate(headers_cp):
                ctk.CTkLabel(cp_h_f, text=h, text_color="white", font=(FONTS.family, FONTS.size_lg, "bold"),
                            anchor="center").place(relx=sum(rel_widths_cp[:i]), rely=0.5, relwidth=rel_widths_cp[i], anchor="w")

            correls = self.res.get('correls', [])
            cp_rows_cont = ctk.CTkFrame(cp_card, fg_color="transparent")
            cp_rows_cont.pack(fill="both", expand=True, padx=5, pady=5)

            for j, c in enumerate(correls):
                r_abs = abs(c['r'])
                grado = "Fuerte" if r_abs >= 0.70 else "Moderada" if r_abs >= 0.50 else "Débil"
                color_grado = COLORS.primary if r_abs >= 0.50 else COLORS.text_secondary

                row_f = ctk.CTkFrame(cp_rows_cont, fg_color="transparent", height=32)
                row_f.pack(fill="x")
                row_f.pack_propagate(False)

                vals_cp = [c['var'], f"{c['r']:.4f}", f"{c['p']:.4f}", grado]
                for k, val in enumerate(vals_cp):
                    ctk.CTkLabel(row_f, text=val, font=(FONTS.family, FONTS.size_lg), text_color=color_grado if k==3 else COLORS.text_primary,
                                anchor="center").place(relx=sum(rel_widths_cp[:k]), rely=0.5, relwidth=rel_widths_cp[k], anchor="w")

                if j < len(correls) - 1:
                    ctk.CTkFrame(cp_rows_cont, fg_color=COLORS.border, height=1).pack(fill="x", padx=10)

            self._tabla_simple(row_bot, "4. DIAGNÓSTICO DE SUPUESTOS", [
                ("Homocedasticidad (Breusch-Pagan p-val)", f"{m['bp_pval']:.4f}"),
                ("Interpretación", "Varianza constante" if m['bp_pval'] > 0.05 else "Heterocedasticidad Detectada"),
            ], grid_pos=(0, 1), grid_padx=(6, 0))

    # ──────────────────────────────────────────────────────────────────────────
    # TAB: POTENCIALES
    # ──────────────────────────────────────────────────────────────────────────
    def _render_potenciales(self):
        scroll = ctk.CTkScrollableFrame(self.content_view, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        p = self.res['potenciales']

        # ── 1. BLOQUE DE ECUACIONES ──────────────────────────────────────────
        eq_card = ctk.CTkFrame(scroll, fg_color=COLORS.bg_card, corner_radius=15,
                               border_width=1, border_color=COLORS.border)
        eq_card.pack(anchor="center", padx=80, pady=(12, 12), ipadx=10, ipady=5)

        self._titulo_seccion(eq_card, "Fórmulas del Modelo Energético")

        eq_inner = ctk.CTkFrame(eq_card, fg_color="transparent")
        eq_inner.pack(padx=30, pady=(0, 8))

        def add_eq_label(master, title, formula, color):
            ctk.CTkLabel(
                master, text=title,
                # ← TÍTULOS MÁS GRANDES: subimos de size_lg a 15px bold
                font=(FONTS.family, 15, "bold"),
                text_color=color
            ).pack(anchor="center", pady=(8, 0))

            ctk.CTkLabel(
                master, text=formula,
                font=(FONTS.family, FONTS.size_xl, "italic"),
                text_color=COLORS.text_primary,
                wraplength=700,
                justify="center"
            ).pack(anchor="center", pady=(2, 8))

        # Ecuación 1
        add_eq_label(
            eq_inner, "Línea Base (LBEn):",
            formatear_ecuacion(self.res['model_lben'], self.config['vars_ind']),
            COLORS.primary
        )

        # ── SEPARADOR: usamos un frame con height=1 y ancho explícito ────────
        # pack con fill="x" + padx es la forma más confiable en CTk
        ctk.CTkFrame(eq_inner, fg_color=COLORS.border, height=1, corner_radius=0).pack(
            fill="x", padx=50, pady=(0, 0)
        )

        # Ecuación 2
        add_eq_label(
            eq_inner, "Línea Meta (LMEn):",
            formatear_ecuacion(self.res['model_lmen'], self.config['vars_ind']),
            COLORS.accent
        )

        # ── 2. GRID DE RESULTADOS ────────────────────────────────────────────
        results_cont = ctk.CTkFrame(scroll, fg_color="transparent")
        results_cont.pack(fill="x", padx=10)
        results_cont.grid_columnconfigure((0, 1, 2), weight=1, uniform="res")

        self._card_metrica(results_cont, 0, "Promedio Histórico (Real)",
                           f"{p['prom_real']:,.1f}", "kWh/mes", COLORS.text_secondary)
        self._card_metrica(results_cont, 1, "Promedio Proyectado (LBEn)",
                           f"{p['prom_lben']:,.1f}", "kWh/mes", COLORS.primary)
        self._card_metrica(results_cont, 2, "Promedio Eficiente (LMEn)",
                           f"{p['prom_lmen']:,.1f}", "kWh/mes", COLORS.accent)

        # ── 3. RESUMEN DE AHORRO ─────────────────────────────────────────────
        ahorro_frame = ctk.CTkFrame(scroll, fg_color=COLORS.primary, corner_radius=15)
        ahorro_frame.pack(fill="x", padx=20, pady=30)
        ahorro_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(ahorro_frame,
                     text=f"Potencial de Ahorro: {p['ahorro_kwh']:,.2f} kWh/mes",
                     text_color="white",
                     font=(FONTS.family, 18, "bold")).grid(row=0, column=0, pady=25)

        ctk.CTkLabel(ahorro_frame,
                     text=f"Potencial de Ahorro (%): {p['ahorro_pct']:.1f}%",
                     text_color="white",
                     font=(FONTS.family, 14, "italic")).grid(row=0, column=1, pady=25)

    # ──────────────────────────────────────────────────────────────────────────
    # TARJETA MÉTRICA
    # ──────────────────────────────────────────────────────────────────────────
    def _card_metrica(self, master, col, titulo, valor, unidad, color_borde):
        card = ctk.CTkFrame(master, fg_color=COLORS.bg_card, corner_radius=12,
                            border_width=2, border_color=color_borde)
        card.grid(row=0, column=col, padx=10, sticky="nsew")

        # ← TÍTULO MÁS GRANDE: subimos de 10 a 13px
        ctk.CTkLabel(card, text=titulo,
                     font=(FONTS.family, 13, "bold")).pack(pady=(15, 0))
        ctk.CTkLabel(card, text=valor,
                     font=(FONTS.family, 24, "bold"),
                     text_color=COLORS.text_primary).pack(pady=5)
        # ← UNIDAD TAMBIÉN MÁS GRANDE: de 9 a 11px
        ctk.CTkLabel(card, text=unidad,
                     font=(FONTS.family, 11),
                     text_color=COLORS.text_secondary).pack(pady=(0, 15))

    # ──────────────────────────────────────────────────────────────────────────
    # TAB: MONITOREO
    # ──────────────────────────────────────────────────────────────────────────
    def _render_monitoreo(self):
        scroll = ctk.CTkScrollableFrame(self.content_view, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        dfm = self.res['df_mon'].copy()
        if dfm.empty:
            ctk.CTkLabel(scroll, text="No hay datos de monitoreo.", font=(FONTS.family, 14)).pack(pady=50)
            return

        col_consumo = None
        excluir_cols = {"Fecha", "lben_mes", "FechaStr", "Fecha_DT", "Afectacion", "Tarifa", "Factor Emisión"}

        if "Consumo" in dfm.columns:       col_consumo = "Consumo"
        elif "Consumo_kWh" in dfm.columns: col_consumo = "Consumo_kWh"

        if not col_consumo:
            for c in dfm.columns:
                c_low = c.lower()
                if ("consum" in c_low or "kwh" in c_low) and c not in excluir_cols:
                    col_consumo = c; break

        if not col_consumo:
            for c in dfm.columns:
                if c not in excluir_cols:
                    try: pd.to_numeric(dfm[c], errors='raise'); col_consumo = c; break
                    except: continue

        if col_consumo is None:
            ctk.CTkLabel(scroll, text="No se pudo identificar la columna de consumo en monitoreo.",
                         font=(FONTS.family, 12), text_color=COLORS.danger).pack(pady=30)
            return

        def _clean_val(v):
            if v is None: return 0.0
            if isinstance(v, (int, float)): return float(v)
            try: return float(str(v).replace(",", "").strip())
            except: return 0.0

        dfm["_consumo_num"] = dfm[col_consumo].apply(_clean_val)
        col_afec = "Afectacion" if "Afectacion" in dfm.columns else None
        dfm["Ajustado"] = dfm["_consumo_num"] + dfm[col_afec].apply(_clean_val) if col_afec else dfm["_consumo_num"]
        dfm["Fecha_DT"] = dfm["Fecha"].apply(safe_to_datetime)
        dfm["FechaStr"] = dfm["Fecha_DT"].apply(fmt_fecha_es)
        dfm = dfm[dfm["Fecha_DT"].notna()].reset_index(drop=True)
        dfm["lben_mes"] = dfm["lben_mes"].apply(_clean_val)
        dfm["Desemp"] = dfm["Ajustado"] - dfm["lben_mes"]
        dfm["CUSUM"]  = dfm.groupby(dfm["Fecha_DT"].dt.year)["Desemp"].cumsum()

        if dfm.empty:
            ctk.CTkLabel(scroll, text="No hay datos válidos de monitoreo.", font=(FONTS.family, 14)).pack(pady=50)
            return

        col_tarifa = col_factor = None
        for c in dfm.columns:
            cl = c.lower()
            if "tarifa" in cl: col_tarifa = c
            if "factor" in cl and "emisi" in cl: col_factor = c

        dfm["Eco_Mes"]  = dfm["Desemp"] * (dfm[col_tarifa].apply(_clean_val) if col_tarifa else 0)
        dfm["Amb_Mes"]  = dfm["Desemp"] * (dfm[col_factor].apply(_clean_val) if col_factor else 0)
        dfm["Eco_Acum"] = dfm["Eco_Mes"].cumsum()
        dfm["Amb_Acum"] = dfm["Amb_Mes"].cumsum()

        # ── Tabla ──
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

        h_scroll = ctk.CTkScrollableFrame(scroll, fg_color=COLORS.bg_card, height=350,
                                          orientation="horizontal", border_width=1, border_color=COLORS.border)
        h_scroll.pack(fill="x")
        inner = ctk.CTkFrame(h_scroll, fg_color="transparent")
        inner.pack(fill="both")

        headers = ["Fecha", "Ajustado", "LBEn", "D. Mensual", "CUSUM",
                   "Avance Pot (%)", "Eco ($)", "Eco Acum ($)", "Amb (CO2)", "Amb Acum (CO2)"]
        col_w = 110
        h_f = ctk.CTkFrame(inner, fg_color=COLORS.primary, height=35)
        h_f.pack(fill="x")
        for i, h in enumerate(headers):
            ctk.CTkLabel(h_f, text=h, text_color="white",
                         font=(FONTS.family, FONTS.size_lg, "bold"), width=col_w).grid(row=0, column=i, padx=5)

        v_scroll = ctk.CTkScrollableFrame(inner, fg_color="transparent", height=300)
        v_scroll.pack(fill="both")

        pot_anual = self.res['potenciales']['ahorro_kwh'] * 12

        for _, row in dfm.iterrows():
            rf = ctk.CTkFrame(v_scroll, fg_color="transparent")
            rf.pack(fill="x")
            av_pot = f"{(row['CUSUM']/pot_anual)*100*-1:.1f}%" if pot_anual != 0 else "---"
            vals = [
                row['FechaStr'],
                f"{row['Ajustado']:,.0f}",
                f"{row['lben_mes']:,.0f}",
                f"{row['Desemp']:,.0f}",
                f"{row['CUSUM']:,.0f}",
                av_pot,
                f"{-row['Eco_Mes']:,.0f}", f"{-row['Eco_Acum']:,.0f}",
                f"{-row['Amb_Mes']:,.1f}",  f"{-row['Amb_Acum']:,.1f}",
            ]
            for i, v in enumerate(vals):
                color = (COLORS.success if i == 3 and row['Desemp'] <= 0
                         else COLORS.danger if i == 3 else COLORS.text_primary)
                ctk.CTkLabel(rf, text=v, width=col_w, text_color=color, font=(FONTS.family, FONTS.size_lg)).grid(row=0, column=i, padx=5)
            ctk.CTkFrame(v_scroll, fg_color=COLORS.border, height=1).pack(fill="x")

        self._chart_real_vs_base(scroll, dfm)
        self._chart_cusum(scroll, dfm)

    # ──────────────────────────────────────────────────────────────────────────
    # GRÁFICOS
    # ──────────────────────────────────────────────────────────────────────────
    def _chart_container(self, parent, title_text, tipo, dfm):
        wrapper = ctk.CTkFrame(parent, fg_color="transparent")
        wrapper.pack(fill="x", padx=20, pady=10)

        header = ctk.CTkFrame(wrapper, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        t_badge = ctk.CTkFrame(header, fg_color=COLORS.primary, height=38, corner_radius=8)
        t_badge.pack(side="left")
        ctk.CTkFrame(t_badge, fg_color=COLORS.accent, width=4, height=20, corner_radius=2)\
            .place(x=10, rely=0.5, anchor="w")
        ctk.CTkLabel(t_badge, text=title_text,
                    font=(FONTS.family, 13, "bold"),
                    text_color="white").pack(side="left", padx=(22, 15))

        ctk.CTkButton(header, text="🌐 Ver interactivo",
                    font=(FONTS.family, 10, "bold"),
                    fg_color="transparent", border_width=1,
                    border_color=COLORS.primary, text_color=COLORS.primary,
                    width=110, height=30,
                    command=lambda: self._abrir_grafica_interactiva(dfm, tipo)).pack(side="right")

        chart_card = ctk.CTkFrame(wrapper, fg_color=COLORS.bg_card, corner_radius=12,
                                border_width=1, border_color=COLORS.border)
        chart_card.pack(fill="x")
        return chart_card

    def _chart_real_vs_base(self, parent, dfm):
        card = self._chart_container(parent, "Seguimiento Energético: Real vs Meta", "monto", dfm)

        fig, ax = plt.subplots(figsize=(10, 3.5), facecolor=COLORS.bg_card)
        ax.set_facecolor("#F8FAF9")

        fechas = dfm["FechaStr"].tolist()
        real   = dfm["Ajustado"].tolist()
        base   = dfm["lben_mes"].tolist()
        rmse   = self.res['metrics']['rmse']

        ax.plot(fechas, base, color=COLORS.primary, linestyle="--", label="Línea Base", linewidth=2)
        ax.plot(fechas, real, color=COLORS.azul, marker="o", label="Consumo Real", linewidth=1.5)

        base_arr = np.array(base)
        ax.fill_between(fechas, base_arr - 2*rmse, base_arr + 2*rmse,
                        color=COLORS.primary, alpha=0.1, label="Banda Control")

        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize=8)
        plt.xticks(rotation=30, ha="right", fontsize=8)
        plt.tight_layout()

        FigureCanvasTkAgg(fig, master=card).get_tk_widget().pack(fill="both", padx=10, pady=10)

    def _chart_cusum(self, parent, dfm):
        card = self._chart_container(parent, "Desempeño energético Acumulado", "cusum", dfm)

        fig, ax = plt.subplots(figsize=(10, 3.5), facecolor=COLORS.bg_card)
        ax.set_facecolor("#F8FAF9")

        fechas  = dfm["FechaStr"].tolist()
        y_cusum = dfm["CUSUM"].values

        for i in range(len(y_cusum) - 1):
            c = COLORS.success if y_cusum[i+1] <= y_cusum[i] else COLORS.danger
            ax.plot(fechas[i:i+2], y_cusum[i:i+2], color=c, linewidth=2.5, marker="o", markersize=4)

        ax.axhline(0, color=COLORS.primary, linestyle='--', alpha=0.3)
        plt.xticks(rotation=30, ha="right", fontsize=8)
        plt.tight_layout()

        FigureCanvasTkAgg(fig, master=card).get_tk_widget().pack(fill="both", padx=10, pady=10)

    def _abrir_grafica_interactiva(self, dfm, tipo):
        try:
            fig    = go.Figure()
            fechas = dfm["FechaStr"].tolist()
            if tipo == "monto":
                fig.add_trace(go.Scatter(x=fechas, y=dfm["lben_mes"], name="Línea Base",
                                         line=dict(dash='dash', color='#2E7D32')))
                fig.add_trace(go.Scatter(x=fechas, y=dfm["Ajustado"], name="Consumo Ajustado",
                                         mode='lines+markers', line=dict(color="#2F7BD3")))
                fig.update_layout(title="Comparativa Consumo vs Línea Base",
                                  xaxis_title="Mes", yaxis_title="kWh")
            else:
                y_vals    = dfm["CUSUM"].values
                años_list = dfm["Fecha_DT"].dt.year.tolist()
                for i in range(len(y_vals)-1):
                    if años_list[i] == años_list[i+1]:
                        color = 'rgb(44,160,44)' if y_vals[i+1] <= y_vals[i] else 'rgb(214,39,40)'
                        fig.add_trace(go.Scatter(x=[fechas[i], fechas[i+1]], y=[y_vals[i], y_vals[i+1]],
                                                 mode='lines+markers', line=dict(color=color, width=4),
                                                 showlegend=False))
                    else:
                        fig.add_trace(go.Scatter(x=[fechas[i]], y=[y_vals[i]], mode='markers',
                                                 marker=dict(color='gray', size=8), showlegend=False))
                fig.add_hline(y=0, line_dash="dash", line_color="gray")
                fig.update_layout(title="Desempeño Energético Acumulado (CUSUM)",
                                  xaxis_title="Mes", yaxis_title="kWh Acumulado")
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
            fig.write_html(tmp.name)
            webbrowser.open(f"file://{tmp.name}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la gráfica: {e}")

    # ──────────────────────────────────────────────────────────────────────────
    # HELPERS DE UI
    # ──────────────────────────────────────────────────────────────────────────
    def _titulo_seccion(self, parent, title):
        title_row = ctk.CTkFrame(parent, fg_color=COLORS.primary, height=38, corner_radius=8)
        title_row.pack(fill="x")
        title_row.pack_propagate(False)
        ctk.CTkFrame(title_row, fg_color=COLORS.accent, width=4, height=20,
                     corner_radius=2).place(x=12, y=9)
        ctk.CTkLabel(title_row, text=title, font=(FONTS.family, FONTS.size_xl, "bold"),
                     text_color="white", anchor="w").place(x=20, y=19, anchor="w")

    def _tabla_simple(self, parent, title, rows, pady=0, grid_pos=None, grid_padx=(0, 0)):
        frame = ctk.CTkFrame(parent, fg_color="transparent")

        if grid_pos is not None:
            row_idx, col_idx = grid_pos
            frame.grid(row=row_idx, column=col_idx, sticky="nsew", padx=grid_padx)
        else:
            frame.pack(fill="x", pady=pady)

        title_row = ctk.CTkFrame(frame, fg_color=COLORS.primary, height=38, corner_radius=8)
        title_row.pack(fill="x")
        title_row.pack_propagate(False)
        ctk.CTkFrame(title_row, fg_color=COLORS.accent, width=4, height=20,
                     corner_radius=2).place(x=12, y=9)
        ctk.CTkLabel(title_row, text=title, font=(FONTS.family, FONTS.size_xl, "bold"),
                     text_color="white", anchor="w").place(x=20, y=19, anchor="w")

        content = ctk.CTkFrame(frame, fg_color=COLORS.bg_card, corner_radius=20,
                               border_width=1, border_color=COLORS.border)
        content.pack(fill="x", padx=10, pady=0)

        for i, row in enumerate(rows):
            if len(row) == 4:
                label1, value1, label2, value2 = row
                row_f = ctk.CTkFrame(content, fg_color="transparent", height=35)
                row_f.pack(fill="x", padx=15, pady=2)
                row_f.pack_propagate(False)

                left_half = ctk.CTkFrame(row_f, fg_color="transparent")
                left_half.place(relx=0, rely=0, relwidth=0.48, relheight=1.0)
                ctk.CTkLabel(left_half, text=label1, font=(FONTS.family, FONTS.size_md),
                             text_color="#7A8C85", anchor="w").place(relx=0, rely=0.5, anchor="w")
                ctk.CTkLabel(left_half, text=str(value1), font=(FONTS.family, FONTS.size_lg, "bold"),
                             text_color=COLORS.primary, anchor="e").place(relx=1.0, rely=0.5, anchor="e")

                ctk.CTkFrame(row_f, fg_color=COLORS.border, width=1,
                             corner_radius=0).place(relx=0.5, rely=0.1, relheight=0.8)

                right_half = ctk.CTkFrame(row_f, fg_color="transparent")
                right_half.place(relx=0.52, rely=0, relwidth=0.48, relheight=1.0)
                ctk.CTkLabel(right_half, text=label2, font=(FONTS.family, FONTS.size_md),
                             text_color="#7A8C85", anchor="w").place(relx=0, rely=0.5, anchor="w")
                ctk.CTkLabel(right_half, text=str(value2), font=(FONTS.family, FONTS.size_lg, "bold"),
                             text_color=COLORS.primary, anchor="e").place(relx=1.0, rely=0.5, anchor="e")
            else:
                label, value = row
                row_f = ctk.CTkFrame(content, fg_color="transparent", height=35)
                row_f.pack(fill="x", padx=15, pady=2)
                row_f.pack_propagate(False)
                ctk.CTkLabel(row_f, text=label, font=(FONTS.family, FONTS.size_md),
                             text_color="#7A8C85", anchor="w").place(relx=0, rely=0.5, anchor="w")
                ctk.CTkLabel(row_f, text=str(value), font=(FONTS.family, FONTS.size_lg, "bold"),
                             text_color=COLORS.primary, anchor="e").place(relx=1.0, rely=0.5, anchor="e")

            if i < len(rows) - 1:
                ctk.CTkFrame(content, fg_color=COLORS.border, height=1,
                             corner_radius=0).pack(fill="x", padx=10)

    def _actualizar_excel(self):
        path = self.app.session.get("excel_path")
        if not path: return
        self.btn_upd.configure(state="disabled", text="⌛ ESCRIBIENDO...")
        def run():
            try:
                if escribir_resultados_m3(path, self.res, self.config):
                    messagebox.showinfo("Éxito", "Reporte M3 actualizado.")
                else:
                    messagebox.showerror("Error", "No se pudo escribir.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                self.after(0, lambda: self.btn_upd.configure(state="normal", text="💾 Actualizar archivo (Excel)"))
        threading.Thread(target=run, daemon=True).start()