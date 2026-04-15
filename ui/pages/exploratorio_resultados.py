"""
ui/pages/exploratorio_resultados.py
=====================================
Pantalla de resultados del análisis exploratorio.
Muestra: recomendación, diagnóstico avanzado, tabla Pearson, scatters, sincronía temporal.
"""

import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os
from PIL import Image
from ui.theme import COLORS, FONTS, DIMS
from ui.utils import resource_path


class ExploratorioResultadosPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        self._resultados    = None
        self._recomendacion = None
        self._diagnostico   = None
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_topbar()
        self._calcular()
        self._build_cuerpo()

    # ── Topbar ────────────────────────────────────────────────────────────────
    def _build_topbar(self):
        topbar = ctk.CTkFrame(
            self, fg_color=COLORS.bg_card,
            corner_radius=0, height=DIMS.topbar_height
        )
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)

        ctk.CTkFrame(
            topbar, fg_color=COLORS.accent,
            height=2, corner_radius=0
        ).place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        ctk.CTkButton(
            topbar,
            text="← Datos",
            font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent",
            text_color=COLORS.primary,
            hover_color=COLORS.bg_main,
            width=80, height=32,
            corner_radius=DIMS.button_radius,
            command=lambda: self.app.navegar("exploratorio_carga")
        ).grid(row=0, column=0, padx=16, pady=8, sticky="w")

        ctk.CTkLabel(
            topbar,
            text="Análisis Exploratorio de Datos",
            font=(FONTS.family, FONTS.size_md, "bold"),
            text_color=COLORS.primary
        ).grid(row=0, column=1, sticky="w", padx=8)

        ctk.CTkButton(
            topbar,
            text="🏠 Inicio",
            font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent",
            text_color=COLORS.primary,
            hover_color=COLORS.bg_main,
            width=80, height=32,
            corner_radius=DIMS.button_radius,
            command=lambda: self.app.navegar("home")
        ).grid(row=0, column=2, padx=16, pady=8, sticky="e")

    # ── Cálculos ──────────────────────────────────────────────────────────────
    def _calcular(self):
        from core.exploratorio import calcular_correlaciones, recomendar_modelo, obtener_diagnostico_avanzado
        sesion   = self.app.session
        df       = sesion.get("df_datos")
        var_dep  = sesion.get("var_dependiente", "")
        vars_ind = sesion.get("vars_independientes", [])

        if df is None or not var_dep:
            return

        self._resultados    = calcular_correlaciones(df, var_dep, vars_ind)
        self._recomendacion = recomendar_modelo(self._resultados)
        self._diagnostico   = obtener_diagnostico_avanzado(df, var_dep, vars_ind)

        # Guardar en sesión
        sesion["resultados_exploratorio"] = {
            "correlaciones":  self._resultados,
            "recomendacion":  self._recomendacion,
            "diagnostico":    self._diagnostico
        }

    # ── Cuerpo scrollable ─────────────────────────────────────────────────────
    def _build_cuerpo(self):
        self.scroll = ctk.CTkScrollableFrame(
            self, fg_color=COLORS.bg_main, corner_radius=0
        )
        self.scroll.grid(row=1, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

        fila = 0

        # 1 — Card recomendación
        self._build_card_recomendacion(self.scroll, fila)
        fila += 1

        # 1.5 — Card Diagnóstico Avanzado
        self._build_card_diagnostico(self.scroll, fila)
        fila += 1

        # 2 — Card tabla Pearson
        self._build_card_tabla(self.scroll, fila)
        fila += 1

        # 3 — Scatters por variable
        self._build_scatters(self.scroll, fila)
        fila += 1

        # 4 — Sincronía temporal
        self._build_sincronia(self.scroll, fila)
        fila += 1

        # 4.5 — Guía de interpretación (Glosario)
        self._build_glosario(self.scroll, fila)
        fila += 1

        # 5 — Botones de acción
        self._build_botones(self.scroll, fila)

    # ── Card recomendación ────────────────────────────────────────────────────
    def _build_card_recomendacion(self, parent, fila):
        if not self._recomendacion:
            return

        rec = self._recomendacion
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS.primary,
            corner_radius=DIMS.card_radius
        )
        card.grid(row=fila, column=0, padx=48, pady=(24, 8), sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        icon_map = {"M1": "m1_icon.png", "M2": "m2_icon.png", "M3": "m3_icon.png"}
        icon_path = resource_path(os.path.join("assets", icon_map.get(rec["codigo"], "m1_icon.png")))
        
        try:
            pil_img = Image.open(icon_path)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(48, 48))
            ctk.CTkLabel(card, text="", image=ctk_img).grid(row=0, column=0, rowspan=2, padx=20, pady=20)
        except:
            ctk.CTkLabel(card, text="📊", font=(FONTS.family, 36), text_color=COLORS.accent).grid(row=0, column=0, rowspan=2, padx=20, pady=20)

        ctk.CTkLabel(
            card,
            text=rec["titulo"],
            font=(FONTS.family, FONTS.size_xl, "bold"),
            text_color=COLORS.text_white,
            anchor="w"
        ).grid(row=0, column=1, sticky="w", padx=(0, 20), pady=(20, 4))

        ctk.CTkLabel(
            card,
            text="Recomendación del Sistema",
            font=(FONTS.family, FONTS.size_xs, "bold"),
            text_color=COLORS.accent,
            anchor="w"
        ).grid(row=0, column=2, sticky="e", padx=20, pady=(20, 4))

        ctk.CTkLabel(
            card,
            text=rec["justificacion"],
            font=(FONTS.family, FONTS.size_sm),
            text_color="#A8C4BC",
            anchor="w",
            wraplength=700,
            justify="left"
        ).grid(row=1, column=1, columnspan=2,
               sticky="w", padx=(0, 20), pady=(0, 20))

    # ── Card Diagnóstico ──────────────────────────────────────────────────────
    def _build_card_diagnostico(self, parent, fila):
        if not self._diagnostico:
            return
        
        diag = self._diagnostico
        card = self._card(parent, fila, "🔍  Calidad y Diagnóstico de los Datos")
        
        container = ctk.CTkFrame(card, fg_color="transparent")
        container.pack(fill="x", padx=16, pady=(0, 16))
        container.grid_columnconfigure((0, 1, 2), weight=1)

        # --- A. OUTLIERS ---
        out = diag["outliers"]
        color_out = COLORS.danger if out["conteo"] > 0 else COLORS.success
        f_out = ctk.CTkFrame(container, fg_color=COLORS.bg_main, corner_radius=8, border_width=1, border_color=color_out)
        f_out.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        
        ctk.CTkLabel(f_out, text="Calidad de Datos", font=(FONTS.family, FONTS.size_xs, "bold"), text_color=COLORS.primary).pack(pady=(8, 2))
        if out["conteo"] > 0:
            msg = f"Se detectaron {out['conteo']} anomalías.\nEl consumo presenta picos fuera de lo común."
            ctk.CTkLabel(f_out, text="ALERTA", font=(FONTS.family, 10, "bold"), text_color=COLORS.danger).pack()
            ctk.CTkLabel(f_out, text=msg, font=(FONTS.family, 11), text_color=COLORS.text_primary, wraplength=200).pack(padx=10, pady=(4, 8))
        else:
            ctk.CTkLabel(f_out, text="Datos Limpios", font=(FONTS.family, 10, "bold"), text_color=COLORS.success).pack()
            ctk.CTkLabel(f_out, text="No se detectaron valores inusuales en el periodo.", font=(FONTS.family, 11), text_color=COLORS.text_secondary, wraplength=200).pack(padx=10, pady=(4, 8))

        # --- B. COLINEALIDAD ---
        colin = diag["colinealidad"]
        color_col = COLORS.warning if colin else COLORS.success
        f_col = ctk.CTkFrame(container, fg_color=COLORS.bg_main, corner_radius=8, border_width=1, border_color=color_col)
        f_col.grid(row=0, column=1, padx=4, sticky="nsew")

        ctk.CTkLabel(f_col, text="Colinealidad", font=(FONTS.family, FONTS.size_xs, "bold"), text_color=COLORS.primary).pack(pady=(8, 2))
        if colin:
            v1, v2 = colin[0]["variables"]
            msg_col = (f"'{v1}' y '{v2}' están altamente correlacionadas entre sí.\n"
                       f"Al ser colineales, se sugiere conservar solo la de mayor impacto y excluir la otra\n"
                       f"en la hoja 'Periodo_Análisis' antes de re-procesar.")
            ctk.CTkLabel(f_col, text="COLINEALIDAD", font=(FONTS.family, 10, "bold"), text_color=COLORS.warning).pack()
            ctk.CTkLabel(f_col, text=msg_col, font=(FONTS.family, 11), text_color=COLORS.text_primary, wraplength=200, justify="left").pack(padx=10, pady=(4, 8))
        else:
            ctk.CTkLabel(f_col, text="Óptima", font=(FONTS.family, 10, "bold"), text_color=COLORS.success).pack()
            ctk.CTkLabel(f_col, text="Las variables aportan información única y valiosa.", font=(FONTS.family, 11), text_color=COLORS.text_secondary, wraplength=200).pack(padx=10, pady=(4, 8))

        # --- C. COMPORTAMIENTO ESTACIONAL DEL CONSUMO ---
        est = diag["estacionalidad"]
        f_est = ctk.CTkFrame(container, fg_color=COLORS.bg_main, corner_radius=8, border_width=1, border_color=COLORS.primary)
        f_est.grid(row=0, column=2, padx=(8, 0), sticky="nsew")

        ctk.CTkLabel(f_est, text="Patrón del Consumo", font=(FONTS.family, FONTS.size_xs, "bold"), text_color=COLORS.primary).pack(pady=(8, 2))
        if est and est["tipo"] != "N/D":
            ctk.CTkLabel(f_est, text=est["tipo"].upper(), font=(FONTS.family, 10, "bold"), text_color=COLORS.primary).pack()
            
            tendencia = est.get("tendencia", {}).get("clase", "Estable")
            msg = f"Tendencia a largo plazo: {tendencia}\nPeriodo Pico: {est['pico']}\nPeriodo Valle: {est['valle']}"
            ctk.CTkLabel(f_est, text=msg, font=(FONTS.family, 11), text_color=COLORS.text_primary, wraplength=200, justify="left").pack(padx=10, pady=(4, 8))
        else:
            ctk.CTkLabel(f_est, text="No detectado", font=(FONTS.family, 10, "bold"), text_color=COLORS.text_secondary).pack()
            ctk.CTkLabel(f_est, text="Datos insuficientes para análisis estacional.", font=(FONTS.family, 11), text_color=COLORS.text_secondary, wraplength=200).pack(padx=10, pady=(4, 8))

    def _build_glosario(self, parent, fila):
        card = ctk.CTkFrame(parent, fg_color="transparent")
        card.grid(row=fila, column=0, padx=48, pady=(8, 24), sticky="ew")
        
        lbl = ctk.CTkLabel(
            card, text="📖  Guía de Interpretación de Resultados",
            font=(FONTS.family, FONTS.size_sm, "bold"),
            text_color=COLORS.text_secondary
        )
        lbl.pack(anchor="w", pady=(0, 8))

        texto_ayuda = (
            "• Estacionalidad Estable: El consumo es constante; ningún mes varía más del 15% del promedio anual.\n"
            "• Ciclos (Uni/Bimodal): Indican 1 o 2 periodos de alta demanda al año (estacionalidad clara).\n"
            "• Tendencia a largo plazo: Indica si el edificio está aumentando o disminuyendo su carga base con el tiempo.\n"
            "• Sincronía: Cuantifica qué tan parecidas son las formas de las curvas. Si es Alta Inversa, cuando una sube la otra siempre baja."
        )

        ctk.CTkLabel(
            card, text=texto_ayuda,
            font=(FONTS.family, 11),
            text_color=COLORS.text_secondary,
            justify="left", anchor="w"
        ).pack(anchor="w", padx=10)

    # ── Card tabla Pearson ────────────────────────────────────────────────────
    def _build_card_tabla(self, parent, fila):
        if not self._resultados:
            return

        card = self._card(parent, fila, "🔗  Influencia de las Variables (Pearson)")

        # Encabezados (nueva columna: Sugerencia)
        cols   = ["Variable Independiente", "r (Pearson)", "p-valor", "¿Significativa?", "Grado", "Interpretación", "Sugerencia"]
        anchos = [170, 90, 90, 100, 110, 0, 100]

        enc = ctk.CTkFrame(card, fg_color=COLORS.primary, corner_radius=6)
        enc.pack(fill="x", padx=16, pady=(0, 4))

        for ci, (col, ancho) in enumerate(zip(cols, anchos)):
            enc.grid_columnconfigure(ci, weight=1, minsize=ancho)
            ctk.CTkLabel(
                enc, text=col,
                font=(FONTS.family, FONTS.size_xs, "bold"),
                text_color="white", anchor="center"
            ).grid(row=0, column=ci, sticky="ew", padx=6, pady=10)

        # Filas
        for ri, res in enumerate(self._resultados):
            bg = COLORS.bg_main if ri % 2 == 0 else COLORS.bg_card
            fila_frame = ctk.CTkFrame(card, fg_color=bg, corner_radius=0)
            fila_frame.pack(fill="x", padx=16, pady=1)

            for ci, ancho in enumerate(anchos):
                fila_frame.grid_columnconfigure(ci, weight=1, minsize=ancho)

            # Col 0: Variable
            ctk.CTkLabel(fila_frame, text=res["variable"], font=(FONTS.family, FONTS.size_xs, "bold"), text_color=COLORS.primary, anchor="center").grid(row=0, column=0, sticky="ew", padx=6, pady=8)

            # Col 1: r de Pearson
            r_val = res["r_pearson"]
            r_txt = f"{r_val:+.4f}" if r_val is not None else "—"
            ctk.CTkLabel(fila_frame, text=r_txt, font=(FONTS.family_mono, FONTS.size_xs, "bold"), text_color=self._color_r(r_val), anchor="center").grid(row=0, column=1, sticky="ew", padx=6, pady=8)

            # Col 2: p-valor
            p_val = res["p_valor"]
            p_txt = f"{p_val:.4f}" if p_val is not None else "—"
            p_color = COLORS.success if res["significativa"] else COLORS.danger
            ctk.CTkLabel(fila_frame, text=p_txt, font=(FONTS.family_mono, FONTS.size_xs), text_color=p_color, anchor="center").grid(row=0, column=2, sticky="ew", padx=6, pady=8)

            # Col 3: Significativa
            sig_txt   = "✅ Sí" if res["significativa"] else "❌ No"
            sig_color = COLORS.success if res["significativa"] else COLORS.danger
            ctk.CTkLabel(fila_frame, text=sig_txt, font=(FONTS.family, FONTS.size_xs, "bold"), text_color=sig_color, anchor="center").grid(row=0, column=3, sticky="ew", padx=6, pady=8)

            # Col 4: Grado
            ctk.CTkLabel(fila_frame, text=res["grado"], font=(FONTS.family, FONTS.size_xs), text_color=COLORS.text_secondary, anchor="center").grid(row=0, column=4, sticky="ew", padx=6, pady=8)

            # Col 5: Interpretación
            ctk.CTkLabel(fila_frame, text=res.get("interpretacion", ""), font=(FONTS.family, 11), text_color=COLORS.text_primary, anchor="w", wraplength=280, justify="left").grid(row=0, column=5, sticky="ew", padx=10, pady=8)

            # Col 6: Sugerencia (icono + color)
            sug = res.get("sugerencia", "Incluir")
            if sug == "Incluir":
                sug_txt, sug_color = "✔ Incluir", COLORS.success
            else:
                sug_txt, sug_color = "✗ Excluir", COLORS.danger
            ctk.CTkLabel(fila_frame, text=sug_txt, font=(FONTS.family, FONTS.size_xs, "bold"), text_color=sug_color, anchor="center").grid(row=0, column=6, sticky="ew", padx=6, pady=8)

        ctk.CTkFrame(card, fg_color="transparent", height=12).pack()

    # ── Scatters ──────────────────────────────────────────────────────────────
    def _build_scatters(self, parent, fila):
        sesion   = self.app.session
        df       = sesion.get("df_datos")
        var_dep  = sesion.get("var_dependiente", "")
        vars_ind = sesion.get("vars_independientes", [])

        if df is None or not vars_ind:
            return

        from core.exploratorio import preparar_datos_scatter

        card = self._card(parent, fila, "📊  Análisis de Dispersión y Proporcionalidad")

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=16, pady=(0, 16))
        grid.grid_columnconfigure((0, 1), weight=1)

        for idx, var in enumerate(vars_ind):
            datos = preparar_datos_scatter(df, var_dep, var)
            col   = idx % 2
            row   = idx // 2

            fig = self._crear_scatter(datos, var_dep, var)
            canvas_frame = ctk.CTkFrame(grid, fg_color=COLORS.bg_card, corner_radius=8, border_width=1, border_color=COLORS.border)
            canvas_frame.grid(row=row, column=col, padx=(0, 8) if col == 0 else 0, pady=8, sticky="nsew")
            canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
            plt.close(fig)

    def _crear_scatter(self, datos, var_dep, var_ind):
        fig, ax = plt.subplots(figsize=(5, 3.5))
        fig.patch.set_facecolor(COLORS.bg_card)
        ax.set_facecolor("#F8FAF9")
        ax.scatter(datos["x"], datos["y"], color=COLORS.primary, alpha=0.7, s=50, zorder=3, edgecolors="white", linewidths=0.5)
        if len(datos["x_trend"]) > 0:
            ax.plot(datos["x_trend"], datos["y_trend"], color=COLORS.accent, linewidth=2, linestyle="--", zorder=2)
        ax.set_xlabel(var_ind, fontsize=9, color=COLORS.text_secondary)
        ax.set_ylabel(var_dep, fontsize=9, color=COLORS.text_secondary)
        titulo = f"Dispersión: {var_dep} vs {var_ind}"
        if datos["r"] is not None:
            sig = "✓ sig." if (datos["p_valor"] < 0.05) else "✗ no sig."
            titulo += f"\nr = {datos['r']:+.3f}  |  p = {datos['p_valor']:.4f}  |  {sig}"
        ax.set_title(titulo, fontsize=8.5, color=COLORS.primary, fontweight="bold", pad=10)
        ax.tick_params(colors=COLORS.text_secondary, labelsize=8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_color(COLORS.border)
        ax.grid(True, alpha=0.3, color=COLORS.border)
        fig.tight_layout()
        return fig

    # ── Sincronía temporal ────────────────────────────────────────────────────
    def _build_sincronia(self, parent, fila):
        sesion   = self.app.session
        df       = sesion.get("df_datos")
        var_dep  = sesion.get("var_dependiente", "")
        vars_ind = sesion.get("vars_independientes", [])

        if df is None: return

        from core.exploratorio import preparar_datos_sincronia, calcular_puntajes_sincronia
        datos = preparar_datos_sincronia(df, var_dep, vars_ind)
        # Diagnóstico de sincronía basado en Pearson
        diagnosticos = calcular_puntajes_sincronia(self._resultados if self._resultados else [])

        card = self._card(parent, fila, "📈  Sincronía Temporal (Consumo vs Variables)")

        fig = self._crear_sincronia(datos, var_dep)
        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=(0, 4))
        plt.close(fig)

        # NOTA EXPLICATIVA + PUNTAJES
        insight_frame = ctk.CTkFrame(card, fg_color=COLORS.bg_main, corner_radius=8)
        insight_frame.pack(fill="x", padx=16, pady=(0, 16))
        
        ctk.CTkLabel(
            insight_frame,
            text="💡 Guía Visual: Observa si el consumo y las variables suben y bajan al mismo tiempo (Directa) o en sentido contrario (Inversa).",
            font=(FONTS.family, FONTS.size_xs, "bold"),
            text_color=COLORS.primary, anchor="w", wraplength=700, justify="left"
        ).pack(padx=12, pady=(8, 4), anchor="w")

        resumen_sync = []
        for var, d in diagnosticos.items():
            if var == var_dep: continue
            resumen_sync.append(f"• {var}: {d['porcentaje']}% de sincronía — {d['mensaje']}")
        
        txt_sync = "\n".join(resumen_sync) if resumen_sync else "No hay variables para comparar."
        
        ctk.CTkLabel(
            insight_frame, text=txt_sync, font=(FONTS.family, FONTS.size_xs),
            text_color=COLORS.text_primary, justify="left", anchor="w"
        ).pack(padx=12, pady=(0, 12), anchor="w")

    def _crear_sincronia(self, datos, var_dep):
        fechas = datos["fechas"]
        series = datos["series"]
        n      = len(fechas)
        fig, ax = plt.subplots(figsize=(11, 3.5))
        fig.patch.set_facecolor(COLORS.bg_card)
        ax.set_facecolor("#F8FAF9")
        colores = [COLORS.primary, COLORS.accent, "#E63946", "#F4A261", "#2D6A4F", "#457B9D"]
        for idx, (nombre, valores) in enumerate(series.items()):
            color  = colores[idx % len(colores)]
            estilo = "-" if nombre == var_dep else "--"
            grosor = 2.5 if nombre == var_dep else 1.5
            ax.plot(range(n), valores, color=color, linewidth=grosor, linestyle=estilo, label=nombre, zorder=3)
        paso = max(1, n // 12)
        ax.set_xticks(range(0, n, paso))
        ax.set_xticklabels([fechas[i] for i in range(0, n, paso)], rotation=45, ha="right", fontsize=7, color=COLORS.text_secondary)
        ax.set_ylabel("Valor normalizado (0–1)", fontsize=9, color=COLORS.text_secondary)
        ax.set_title("Comparativa de Comportamientos Temporales (Normalizados)", fontsize=9, color=COLORS.primary, fontweight="bold")
        ax.legend(fontsize=8, loc="upper right", framealpha=0.9, edgecolor=COLORS.border)
        ax.tick_params(colors=COLORS.text_secondary, labelsize=8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_color(COLORS.border)
        ax.grid(True, alpha=0.3, color=COLORS.border)
        fig.tight_layout()
        return fig

    # ── Botones ───────────────────────────────────────────────────────────────
    def _build_botones(self, parent, fila):
        frame = ctk.CTkFrame(parent, fg_color=COLORS.bg_card, corner_radius=0, height=70)
        frame.grid(row=fila, column=0, sticky="ew", padx=0, pady=(8, 0))
        frame.grid_propagate(False)
        frame.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(frame, text="📊  Actualizar informe en Excel", font=(FONTS.family, FONTS.size_sm, "bold"), fg_color=COLORS.accent, text_color=COLORS.primary, hover_color="#D4E800", corner_radius=DIMS.button_radius, height=40, command=self._actualizar_excel).grid(row=0, column=0, padx=24, pady=15, sticky="w")
        ctk.CTkButton(frame, text="Continuar a selección de modelo →", font=(FONTS.family, FONTS.size_sm, "bold"), fg_color=COLORS.primary, text_color=COLORS.text_white, hover_color=COLORS.primary_dark, corner_radius=DIMS.button_radius, height=40, command=lambda: self.app.navegar("seleccion_modelo")).grid(row=0, column=2, padx=24, pady=15, sticky="e")

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _actualizar_excel(self):
        from core.io_excel import escribir_resultados_exploratorios
        sesion = self.app.session
        if self._resultados is None: return
        path = sesion.get("excel_path")
        if not path:
            from tkinter import filedialog
            path = filedialog.askopenfilename(title="Seleccionar Excel", filetypes=[("Excel", "*.xlsx")])
        if not path: return
        conf = {
            "var_dep": sesion.get("var_dependiente"),
            "vars_ind": sesion.get("vars_independientes"),
            "f_ini": sesion.get("fecha_inicio"),
            "f_fin": sesion.get("fecha_fin")
        }
        ok = escribir_resultados_exploratorios(path, self._recomendacion["titulo"], self._recomendacion["justificacion"], self._resultados, conf)
        if ok: messagebox.showinfo("Éxito", f"Excel actualizado en:\n{path}")

    def _card(self, parent, fila, titulo):
        card = ctk.CTkFrame(parent, fg_color=COLORS.bg_card, corner_radius=DIMS.card_radius, border_width=1, border_color=COLORS.border)
        card.grid(row=fila, column=0, padx=48, pady=8, sticky="ew")
        card.grid_columnconfigure(0, weight=1)
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(14, 10))
        ctk.CTkFrame(header, fg_color=COLORS.accent, width=4, corner_radius=2).pack(side="left", fill="y", padx=(0, 10))
        ctk.CTkLabel(header, text=titulo, font=(FONTS.family, FONTS.size_sm, "bold"), text_color=COLORS.primary, anchor="w").pack(side="left")
        return card

    def _color_r(self, r):
        if r is None: return COLORS.text_secondary
        r_abs = abs(r)
        if r_abs >= 0.70: return COLORS.success
        elif r_abs >= 0.50: return COLORS.warning
        return COLORS.danger