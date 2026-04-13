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
    MESES_ES_EN = {'Ene':'Jan', 'Feb':'Feb', 'Mar':'Mar', 'Abr':'Apr', 'May':'May', 'Jun':'Jun', 'Jul':'Jul', 'Ago':'Aug', 'Sep':'Sep', 'Oct':'Oct', 'Nov':'Nov', 'Dic':'Dic'}
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

        ctk.CTkLabel(topbar, text=f"M3: {self.config.get('nombre')}", font=(FONTS.family, FONTS.size_md, "bold"), text_color=COLORS.primary).grid(row=0, column=1, sticky="w")

        self.btn_upd = ctk.CTkButton(topbar, text="💾 Actualizar archivo (Excel)", font=(FONTS.family, FONTS.size_sm, "bold"),
                                    fg_color=COLORS.primary, text_color="white", height=32, command=self._actualizar_excel)
        self.btn_upd.grid(row=0, column=2, padx=16, pady=8, sticky="e")

    def _build_kpi_cards(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="ew", padx=20, pady=20)
        frame.grid_columnconfigure((0, 1, 2), weight=1)
        p = self.res['potenciales']
        self._kpi_card(frame, 0, "Consumo Promedio Anual", f"{p['prom_real']*12:,.0f}", "kWh")
        self._kpi_card(frame, 1, "Ahorro Potencial Anual", f"{p['ahorro_kwh']*12:,.0f}", "kWh", color=COLORS.success)
        self._kpi_card(frame, 2, "Ahorro Potencial (%)", f"{p['ahorro_pct']:.1f}%", "Estimado")

    def _kpi_card(self, parent, col, title, value, unit, color=None):
        c = ctk.CTkFrame(parent, fg_color=COLORS.bg_card, corner_radius=12, border_width=1, border_color=COLORS.border)
        c.grid(row=0, column=col, padx=10, sticky="nsew")
        ctk.CTkLabel(c, text=title, font=(FONTS.family, 12), text_color=COLORS.text_secondary).pack(pady=(15,0))
        ctk.CTkLabel(c, text=value, font=(FONTS.family, 28, "bold"), text_color=color if color else COLORS.primary).pack(pady=(5,0))
        ctk.CTkLabel(c, text=unit, font=(FONTS.family, 10, "bold"), text_color=COLORS.text_secondary).pack(pady=(0,15))

    def _build_tabs_area(self):
        tabs_container = ctk.CTkFrame(self, fg_color="transparent")
        tabs_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0,10))
        tabs_container.grid_columnconfigure(0, weight=1)
        tabs_container.grid_rowconfigure(1, weight=1)

        nav = ctk.CTkFrame(tabs_container, fg_color="transparent")
        nav.grid(row=0, column=0, pady=(0,10))
        self.nav_buttons = {}
        tabs = [("identificacion", "📝 Identificación"), ("diag", "📊 Línea Base"), ("potenciales", "📉 Potenciales"), ("monitoreo", "👁️ Monitoreo")]
        for i, (tid, lbl) in enumerate(tabs):
            btn = ctk.CTkButton(nav, text=lbl, font=(FONTS.family, FONTS.size_sm), fg_color=COLORS.border, text_color=COLORS.text_primary, width=150, height=36, command=lambda t=tid: self._change_tab(t))
            btn.grid(row=0, column=i, padx=5)
            self.nav_buttons[tid] = btn

        self.content_view = ctk.CTkFrame(tabs_container, fg_color="transparent")
        self.content_view.grid(row=1, column=0, sticky="nsew")
        self.content_view.grid_columnconfigure(0, weight=1); self.content_view.grid_rowconfigure(0, weight=1)
        self._change_tab("identificacion")

    def _change_tab(self, tid):
        self.current_tab = tid
        for k, b in self.nav_buttons.items():
            b.configure(fg_color=COLORS.primary if k==tid else COLORS.border, text_color=COLORS.text_white if k==tid else COLORS.text_primary)
        for w in self.content_view.winfo_children(): w.destroy()
        plt.close("all")
        if tid == "identificacion": self._render_identificacion()
        elif tid == "diag": self._render_diag()
        elif tid == "potenciales": self._render_potenciales()
        else: self._render_monitoreo()

    def _render_identificacion(self):
        scroll = ctk.CTkScrollableFrame(self.content_view, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)
        
        m = self.res['metrics']
        p = self.res['potenciales']
        id_rows = [("Entidad", self.config['nombre']), ("Fuente", self.config['fuente']), ("Unidad", self.config['unidad']), ("Zona", self.config['zona']), ("Área útil (m²)", self.config['area'])]
        for i, v in enumerate(self.config['vars_ind']): id_rows.append((f"Variable {i+1}", v))
        
        self._tabla_simple(scroll, "IDENTIFICACIÓN DEL PROYECTO", id_rows)
        self._tabla_simple(scroll, "MÉTRICAS DEL MODELO", [
            ("Tipo de Modelo", "M3 (Regresión Multivariable)"),
            ("Fiabilidad (R2)", f"{m['fiabilidad']:.2f}%"),
            ("RMSE (Error)", f"{m['rmse']:,.2f}"),
            ("N registros totales", f"{len(self.res['df_base']) + len(self.res['df_excluidos'])}"),
            ("N filtrados", f"{len(self.res['df_excluidos'])}"),
            ("Periodo Base", f"{self.app.session['pb_ini']} - {self.app.session['pb_fin']}"),
            ("Meta 15% (kWh/año)", f"{p['prom_real']*12*0.15:,.2f}")
        ], pady=20)

    def _render_diag(self):
        scroll = ctk.CTkScrollableFrame(self.content_view, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)
        
        m = self.res['metrics']
        self._tabla_simple(scroll, "1. RESUMEN ESTADÍSTICO GLOBAL", [
            ("Coef. Determinación (R2)", f"{m['r2']:.4f}"),
            ("R2 Ajustado", f"{m['r2_adj']:.4f}"),
            ("RMSE (Error Estándar)", f"{m['rmse']:,.2f}"),
            ("CV(RMSE) %", f"{m['cv_rmse']:.2f}%"),
            ("Estadístico F (Significancia)", f"{m['f_pval']:.4f}")
        ])

        # Tabla Coeficientes
        ct_lbl = ctk.CTkLabel(scroll, text="2. TABLA DE COEFICIENTES", font=(FONTS.family, 13, "bold"), text_color=COLORS.primary, anchor="w")
        ct_lbl.pack(fill="x", pady=(20,10))
        ct_card = ctk.CTkFrame(scroll, fg_color=COLORS.bg_card, border_width=1, border_color=COLORS.border)
        ct_card.pack(fill="x")
        
        ct = self.res['coef_table']
        headers = ["Variable", "Coeficiente", "Err. Est.", "p-valor", "VIF"]
        h_f = ctk.CTkFrame(ct_card, fg_color=COLORS.primary, height=30)
        h_f.pack(fill="x")
        for i, h in enumerate(headers): ctk.CTkLabel(h_f, text=h, text_color="white", font=(FONTS.family, 10, "bold"), width=120).grid(row=0, column=i, padx=5)
        
        for i in range(len(ct['vars'])):
            row_f = ctk.CTkFrame(ct_card, fg_color="transparent")
            row_f.pack(fill="x")
            ctk.CTkLabel(row_f, text=ct['vars'][i], width=120).grid(row=0, column=0, padx=5)
            ctk.CTkLabel(row_f, text=f"{ct['betas'][i]:,.4f}", width=120).grid(row=0, column=1, padx=5)
            ctk.CTkLabel(row_f, text=f"{ct['std_err'][i]:,.4f}", width=120).grid(row=0, column=2, padx=5)
            ctk.CTkLabel(row_f, text=f"{ct['p_vals'][i]:,.4f}", width=120).grid(row=0, column=3, padx=5)
            ctk.CTkLabel(row_f, text="---" if np.isnan(ct['vif'][i]) else f"{ct['vif'][i]:.2f}", width=120).grid(row=0, column=4, padx=5)

        self._tabla_simple(scroll, "3. SUPUESTOS DEL MODELO", [
            ("Homocedasticidad (Breusch-Pagan p-val)", f"{m['bp_pval']:.4f}"),
            ("Interpretación", "Varianza constante" if m['bp_pval'] > 0.05 else "Heterocedasticidad Detectada")
        ], pady=20)

    def _render_potenciales(self):
        scroll = ctk.CTkScrollableFrame(self.content_view, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)
        
        p = self.res['potenciales']
        self._tabla_simple(scroll, "ECUACIONES DEL MODELO", [
            ("Línea Base (LBEn)", formatear_ecuacion(self.res['model_lben'], self.config['vars_ind'])),
            ("Línea Meta (LMEn)", formatear_ecuacion(self.res['model_lmen'], self.config['vars_ind']))
        ])
        
        self._tabla_simple(scroll, "TABLA DE AHORRO POTENCIAL", [
            ("Promedio histórico (Real)", f"{p['prom_real']:,.2f} kWh/mes"),
            ("Promedio Proyectado (LBEn)", f"{p['prom_lben']:,.2f} kWh/mes"),
            ("Promedio Eficiente (LMEn)", f"{p['prom_lmen']:,.2f} kWh/mes"),
            ("Potencial de Ahorro", f"{p['ahorro_kwh']:,.2f} kWh/mes"),
            ("Potencial de Ahorro (%)", f"{p['ahorro_pct']:.2f}%")
        ], pady=20)

    def _render_monitoreo(self):
        scroll = ctk.CTkScrollableFrame(self.content_view, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        dfm = self.res['df_mon'].copy()
        if dfm.empty:
            ctk.CTkLabel(scroll, text="No hay datos de monitoreo.", font=(FONTS.family, 14)).pack(pady=50)
            return

        # ── Detectar columna de consumo real por posición/nombre robusto ──
        col_consumo = None
        excluir_cols = {"Fecha", "lben_mes", "FechaStr", "Fecha_DT", "Afectacion", "Tarifa", "Factor Emisión"}
        
        # 1. Prioridad: nombres exactos
        if "Consumo" in dfm.columns: col_consumo = "Consumo"
        elif "Consumo_kWh" in dfm.columns: col_consumo = "Consumo_kWh"
        
        # 2. Búsqueda por subcadena
        if not col_consumo:
            for c in dfm.columns:
                c_low = c.lower()
                if ("consum" in c_low or "kwh" in c_low) and c not in excluir_cols:
                    col_consumo = c
                    break
        
        # 3. Fallback: primera numérica no excluida
        if not col_consumo:
            for c in dfm.columns:
                if c not in excluir_cols:
                    try:
                        pd.to_numeric(dfm[c], errors='raise')
                        col_consumo = c
                        break
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
        # Columna Afectacion si existe
        col_afec = "Afectacion" if "Afectacion" in dfm.columns else None
        dfm["Ajustado"] = dfm["_consumo_num"] + dfm[col_afec].apply(_clean_val) if col_afec else dfm["_consumo_num"]
        dfm["lben_mes"] = dfm["lben_mes"].apply(_clean_val)

        # FILTRAR: solo filas con consumo real (evitar fechas vacías hasta 2050)
        dfm = dfm[dfm["_consumo_num"] > 0].reset_index(drop=True)

        dfm["Desemp"] = dfm["Ajustado"] - dfm["lben_mes"]
        dfm["CUSUM"] = dfm["Desemp"].cumsum()

        dfm["Fecha_DT"] = dfm["Fecha"].apply(safe_to_datetime)
        dfm["FechaStr"] = dfm["Fecha_DT"].apply(fmt_fecha_es)
        # Filtrar solo filas con fecha válida
        dfm = dfm[dfm["Fecha_DT"].notna()].reset_index(drop=True)

        if dfm.empty:
            ctk.CTkLabel(scroll, text="No hay datos válidos de monitoreo.", font=(FONTS.family, 14)).pack(pady=50)
            return

        # ── Tabla con Doble Scroll ──
        ctk.CTkLabel(scroll, text="DATOS DE MONITOREO", font=(FONTS.family, 14, "bold"),
                     text_color=COLORS.primary, anchor="w").pack(fill="x", pady=(0,10))

        h_scroll = ctk.CTkScrollableFrame(scroll, fg_color=COLORS.bg_card, height=350,
                                          orientation="horizontal", border_width=1, border_color=COLORS.border)
        h_scroll.pack(fill="x")
        inner = ctk.CTkFrame(h_scroll, fg_color="transparent")
        inner.pack(fill="both")

        headers = ["Fecha", "Real (kWh)", "Ajustado", "LBEn (kWh)", "Desempeño", "CUSUM (kWh)", "Avance %"]
        col_w = 130
        h_f = ctk.CTkFrame(inner, fg_color=COLORS.primary, height=35)
        h_f.pack(fill="x")
        for i, h in enumerate(headers):
            ctk.CTkLabel(h_f, text=h, text_color="white", font=(FONTS.family, 10, "bold"), width=col_w).grid(row=0, column=i, padx=5)

        v_scroll = ctk.CTkScrollableFrame(inner, fg_color="transparent", height=300)
        v_scroll.pack(fill="both")

        pot_anual = self.res['potenciales']['ahorro_kwh'] * 12

        for _, row in dfm.iterrows():
            rf = ctk.CTkFrame(v_scroll, fg_color="transparent")
            rf.pack(fill="x")
            avance = f"{(row['CUSUM']/pot_anual)*100:.1f}%" if pot_anual > 0 else "0%"
            vals = [row['FechaStr'], f"{row['_consumo_num']:,.1f}", f"{row['Ajustado']:,.1f}",
                    f"{row['lben_mes']:,.1f}", f"{row['Desemp']:,.1f}", f"{row['CUSUM']:,.1f}", avance]
            for i, v in enumerate(vals):
                color = COLORS.success if i==4 and row['Desemp']<=0 else COLORS.danger if i==4 else COLORS.text_primary
                ctk.CTkLabel(rf, text=v, width=col_w, text_color=color).grid(row=0, column=i, padx=5)
            ctk.CTkFrame(v_scroll, fg_color=COLORS.border, height=1).pack(fill="x")

        # ── Gráficos ──
        self._chart_real_vs_base(scroll, dfm)
        self._chart_cusum(scroll, dfm)

    def _chart_real_vs_base(self, parent, dfm):
        f = ctk.CTkFrame(parent, fg_color=COLORS.bg_card, corner_radius=12, border_width=1, border_color=COLORS.border)
        f.pack(fill="x", pady=20)
        fig, ax = plt.subplots(figsize=(10, 4), facecolor=COLORS.bg_card)
        ax.set_facecolor("#F8FAF9")
        
        fechas = dfm["FechaStr"].tolist()
        real = dfm["Ajustado"].tolist()
        base = dfm["lben_mes"].tolist()
        rmse = self.res['metrics']['rmse']
        
        ax.plot(fechas, base, color=COLORS.primary, linestyle="--", label="Línea Base", linewidth=2)
        ax.plot(fechas, real, color=COLORS.danger, marker="o", label="Consumo Real", linewidth=1.5)
        
        base_arr = np.array(base)
        ax.fill_between(fechas, base_arr - 3*rmse, base_arr + 3*rmse, color=COLORS.primary, alpha=0.1, label="Banda Control (±3σ)")
        
        ax.legend(fontsize=8, loc="upper right")
        plt.xticks(rotation=30, ha="right", fontsize=8); plt.tight_layout()
        FigureCanvasTkAgg(fig, master=f).get_tk_widget().pack(fill="both", padx=10, pady=10)

    def _chart_cusum(self, parent, dfm):
        f = ctk.CTkFrame(parent, fg_color=COLORS.bg_card, corner_radius=12, border_width=1, border_color=COLORS.border)
        f.pack(fill="x", pady=(0, 20))
        fig, ax = plt.subplots(figsize=(10, 4), facecolor=COLORS.bg_card)
        ax.set_facecolor("#F8FAF9")
        
        fechas = dfm["FechaStr"].tolist()
        cusum = dfm["CUSUM"].tolist()
        
        for i in range(1, len(cusum)):
            c = COLORS.success if cusum[i] <= cusum[i-1] else COLORS.danger
            ax.plot(fechas[i-1:i+1], cusum[i-1:i+1], color=c, linewidth=2.5)
            
        ax.axhline(0, color=COLORS.primary, alpha=0.3, linestyle=":")
        ax.set_title("CUSUM — Desempeño Energético Acumulado", fontdict={"size":10, "weight":"bold"})
        plt.xticks(rotation=30, ha="right", fontsize=8); plt.tight_layout()
        FigureCanvasTkAgg(fig, master=f).get_tk_widget().pack(fill="both", padx=10, pady=10)

    def _tabla_simple(self, parent, title, rows, pady=0):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=pady)
        ctk.CTkLabel(frame, text=title, font=(FONTS.family, 14, "bold"), text_color=COLORS.primary, anchor="w").pack(fill="x", pady=(0, 10))
        content = ctk.CTkFrame(frame, fg_color=COLORS.bg_card, corner_radius=8, border_width=1, border_color=COLORS.border)
        content.pack(fill="x")
        for i, (l, v) in enumerate(rows):
            if i > 0: ctk.CTkFrame(content, fg_color=COLORS.border, height=1).pack(fill="x", padx=10)
            row_f = ctk.CTkFrame(content, fg_color="transparent", height=35)
            row_f.pack(fill="x", padx=15, pady=2)
            ctk.CTkLabel(row_f, text=l, font=(FONTS.family, 11), text_color=COLORS.text_secondary, anchor="w").place(relx=0, rely=0.5, anchor="w")
            ctk.CTkLabel(row_f, text=str(v), font=(FONTS.family, 11, "bold"), text_color=COLORS.text_primary, anchor="e").place(relx=1.0, rely=0.5, anchor="e")

    def _actualizar_excel(self):
        path = self.app.session.get("excel_path")
        if not path: return
        self.btn_upd.configure(state="disabled", text="⌛ ESCRIBIENDO...")
        def run():
            try:
                if escribir_resultados_m3(path, self.res, self.config):
                    messagebox.showinfo("Éxito", "Reporte M3 actualizado.")
                else: messagebox.showerror("Error", "No se pudo escribir.")
            except Exception as e: messagebox.showerror("Error", str(e))
            finally: self.after(0, lambda: self.btn_upd.configure(state="normal", text="💾 Actualizar archivo (Excel)"))
        threading.Thread(target=run, daemon=True).start()
