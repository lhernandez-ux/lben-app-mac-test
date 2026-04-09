"""
ui/pages/m1_resultados.py
=========================
Visualización de resultados del Modelo M1: Consumo Absoluto.
"""

import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ui.theme import COLORS, FONTS, DIMS
from core.io_excel import escribir_resultados_m1

class M1ResultadosPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        
        # Recuperar datos de sesión
        self.df_lben = self.app.session.get("df_lben")
        self.df_mon  = self.app.session.get("df_monitoreo")
        self.meta    = self.app.session.get("meta_m1")

        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_topbar()
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
            topbar, text="M1: Resultados y Seguimiento",
            font=(FONTS.family, FONTS.size_md, "bold"), text_color=COLORS.primary
        ).grid(row=0, column=1, sticky="w", padx=8)

        ctk.CTkButton(
            topbar, text="💾 Actualizar Informe en Excel",
            font=(FONTS.family, FONTS.size_sm, "bold"), fg_color=COLORS.primary,
            text_color="white", height=32, command=self._guardar_excel
        ).grid(row=0, column=2, padx=16, pady=8, sticky="e")

    def _build_tabs(self):
        self.tabs = ctk.CTkTabview(
            self, fg_color=COLORS.bg_main, segmented_button_fg_color=COLORS.bg_card,
            segmented_button_selected_color=COLORS.primary,
            segmented_button_selected_hover_color=COLORS.primary_dark,
            segmented_button_unselected_hover_color=COLORS.border,
            text_color=COLORS.primary
        )
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        self.tabs.add("Línea Base")
        self.tabs.add("Desempeño")
        self.tabs.add("Seguimiento")
        self.tabs.add("Ajuste NR")

        self._render_lben_tab()
        self._render_desempeno_tab()
        self._render_seguimiento_tab()
        self._render_ajuste_tab()

    def _render_lben_tab(self):
        tab = self.tabs.tab("Línea Base")
        
        fig, ax = plt.subplots(figsize=(8, 4), facecolor=COLORS.bg_main)
        ax.set_facecolor(COLORS.bg_main)
        
        meses = self.df_lben['mes']
        valores = self.df_lben['lben']
        
        ax.bar(meses, valores, color=COLORS.primary, alpha=0.7, label="LBEn Mensual")
        ax.plot(meses, valores, marker='o', color=COLORS.accent, linewidth=2)
        
        ax.set_title("Línea Base Energética por Mes", color=COLORS.primary, fontsize=12, fontweight='bold')
        ax.tick_params(axis='x', rotation=45, labelcolor=COLORS.text_secondary)
        ax.tick_params(axis='y', labelcolor=COLORS.text_secondary)
        ax.grid(True, axis='y', linestyle='--', alpha=0.3)
        
        rect = fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def _render_desempeno_tab(self):
        tab = self.tabs.tab("Desempeño")
        if self.df_mon is None or self.df_mon.empty:
            ctk.CTkLabel(tab, text="No hay datos de monitoreo cargados para mostrar desempeño.", text_color=COLORS.text_secondary).pack(pady=40)
            return

        fig, ax = plt.subplots(figsize=(8, 4), facecolor=COLORS.bg_main)
        ax.set_facecolor(COLORS.bg_main)
        
        ax.plot(self.df_mon['Fecha'], self.df_mon['LBEn_Mes'], label="Línea Base (Meta)", color=COLORS.primary, linestyle='--', marker='s')
        ax.plot(self.df_mon['Fecha'], self.df_mon['Normalizado'], label="Consumo Real", color=COLORS.accent, marker='o', linewidth=2)
        
        ax.set_title("Consumo Real vs Línea Base", color=COLORS.primary, fontsize=12, fontweight='bold')
        ax.legend()
        ax.tick_params(axis='x', rotation=45, labelcolor=COLORS.text_secondary)
        ax.tick_params(axis='y', labelcolor=COLORS.text_secondary)
        ax.grid(True, linestyle='--', alpha=0.3)
        
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def _render_seguimiento_tab(self):
        tab = self.tabs.tab("Seguimiento")
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        if self.df_mon is None or self.df_mon.empty:
            ctk.CTkLabel(scroll, text="Cargue datos de monitoreo para ver la tabla de seguimiento.").pack(pady=20)
            return

        # Encabezado simple de tabla
        headers = ["Fecha", "Real (kWh)", "LBEn (kWh)", "Ahorro (kWh)", "Ahorro (%)"]
        h_frame = ctk.CTkFrame(scroll, fg_color=COLORS.primary, height=30)
        h_frame.pack(fill="x", pady=(0, 5))
        for i, h in enumerate(headers):
            ctk.CTkLabel(h_frame, text=h, text_color="white", font=(FONTS.family, 11, "bold"), width=120).grid(row=0, column=i, padx=5)

        # Filas
        for _, row in self.df_mon.iterrows():
            f_frame = ctk.CTkFrame(scroll, fg_color=COLORS.bg_card, height=28)
            f_frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(f_frame, text=row['Fecha'], width=120).grid(row=0, column=0, padx=5)
            ctk.CTkLabel(f_frame, text=f"{row['Normalizado']:,.1f}", width=120).grid(row=0, column=1, padx=5)
            ctk.CTkLabel(f_frame, text=f"{row['LBEn_Mes']:,.1f}", width=120).grid(row=0, column=2, padx=5)
            
            ahorro = row['Ahorro_kWh']
            color = COLORS.primary if ahorro >= 0 else COLORS.danger
            ctk.CTkLabel(f_frame, text=f"{ahorro:,.1f}", text_color=color, width=120, font=(FONTS.family, 11, "bold")).grid(row=0, column=3, padx=5)
            ctk.CTkLabel(f_frame, text=f"{row['Ahorro_Pct']:,.1f}%", text_color=color, width=120, font=(FONTS.family, 11, "bold")).grid(row=0, column=4, padx=5)

    def _render_ajuste_tab(self):
        tab = self.tabs.tab("Ajuste NR")
        ctk.CTkLabel(
            tab, text="Ajustes No Rutinarios Detectados",
            font=(FONTS.family, FONTS.size_lg, "bold"), text_color=COLORS.primary
        ).pack(pady=20)
        
        # Aquí se detectarán filas donde 'Ajuste No Rutinario (NR)' == 'Si'
        ajustes = self.df_base[self.df_base.iloc[:, 5].astype(str).str.lower() == 'si'] if self.df_base is not None else []
        
        if len(ajustes) == 0:
            ctk.CTkLabel(tab, text="No se han reportado eventos no rutinarios en el periodo base.", text_color=COLORS.text_secondary).pack()
        else:
            for _, row in ajustes.iterrows():
                msg = f"• {row['Fecha']}: {row.iloc[6]}"
                ctk.CTkLabel(tab, text=msg, anchor="w", justify="left").pack(fill="x", padx=40)

    def _guardar_excel(self):
        path = self.app.session.get("excel_path")
        if not path: return
        
        if escribir_resultados_m1(path, self.df_lben, self.df_mon, self.meta):
            messagebox.showinfo("Éxito", "El archivo Excel ha sido actualizado con los resultados.")
        else:
            messagebox.showerror("Error", "No se pudo actualizar el archivo.")
