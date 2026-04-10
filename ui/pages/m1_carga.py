"""
ui/pages/m1_carga.py
====================
Página de carga de datos para el Modelo M1.
Permite seleccionar el archivo Excel, sincronizar metadatos y previsualizar información real.
"""

import customtkinter as ctk
import os
import pandas as pd
from tkinter import filedialog, messagebox
from ui.theme import COLORS, FONTS, DIMS
from core.models.m1_absoluto import procesar_m1, calcular_resumen_metricas
from core.io_excel import leer_excel_m1

class M1CargaPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        self.df_base = None
        self.df_monitoreo = None
        self.current_path = None
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Topbar
        topbar = ctk.CTkFrame(self, fg_color=COLORS.bg_card, height=DIMS.topbar_height, corner_radius=0)
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)
        
        ctk.CTkButton(topbar, text="← Configuración", font=(FONTS.family, FONTS.size_sm),
                      fg_color="transparent", text_color=COLORS.primary, command=lambda: self.app.navegar("m1_config")).grid(row=0, column=0, padx=16)
        
        ctk.CTkLabel(topbar, text="Modelo M1: Carga de Datos", font=(FONTS.family, FONTS.size_md, "bold"), 
                     text_color=COLORS.primary).grid(row=0, column=1, sticky="w")

        # Cuerpo
        self.cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        self.cuerpo.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        self.cuerpo.grid_columnconfigure(0, weight=1)

        # Card de Selección
        self.card_sel = ctk.CTkFrame(self.cuerpo, fg_color=COLORS.bg_card, corner_radius=DIMS.card_radius, border_width=1, border_color=COLORS.border)
        self.card_sel.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(self.card_sel, text="Selecciona el archivo Excel M1 con tus datos", 
                     font=(FONTS.family, FONTS.size_sm), text_color=COLORS.text_secondary).pack(pady=(30, 15))
        
        self.btn_sel = ctk.CTkButton(self.card_sel, text="📁 Seleccionar Archivo", font=(FONTS.family, FONTS.size_md, "bold"),
                                     fg_color=COLORS.primary, height=44, command=self._seleccionar_archivo)
        self.btn_sel.pack(pady=(0, 10))
        
        self.lbl_path = ctk.CTkLabel(self.card_sel, text="Ningún archivo seleccionado", font=(FONTS.family, FONTS.size_xs), text_color=COLORS.text_secondary)
        self.lbl_path.pack(pady=(0, 30))

        # Zona para la Tarjeta Única de Resumen
        self.zona_resumen = ctk.CTkFrame(self.cuerpo, fg_color="transparent")
        self.zona_resumen.grid(row=1, column=0, sticky="nsew")
        self.zona_resumen.grid_columnconfigure(0, weight=1)

    def _seleccionar_archivo(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if not path: return
        
        self.current_path = path
        self.lbl_path.configure(text=os.path.basename(path))

        # 1. Sincronización de Metadatos (ADN del Proyecto)
        import openpyxl
        try:
            wb = openpyxl.load_workbook(path, data_only=True)
            if "Modelo_LBEn" in wb.sheetnames:
                ws = wb["Modelo_LBEn"]
                self.app.session.update({
                    "tipo_modelo": ws["K5"].value or "M1 — Consumo Absoluto",
                    "nombre": ws["D5"].value or self.app.session.get("nombre", ""),
                    "fuente": ws["D6"].value or self.app.session.get("fuente", ""),
                    "unidad": ws["D7"].value or self.app.session.get("unidad", ""),
                    "pb_ini": ws["M5"].value or self.app.session.get("pb_ini", ""),
                    "pb_fin": ws["M6"].value or self.app.session.get("pb_fin", ""),
                })
        except: pass

        # 2. Lectura y Conteo Real
        df_b, df_m, _, _ = leer_excel_m1(path)
        self.df_base = df_b
        self.df_monitoreo = df_m

        if df_b is not None:
            n_pb = pd.to_numeric(df_b.iloc[:,1], errors='coerce').notna().sum()
            self.app.session["n_pb"] = n_pb
            self.app.session["n_cols"] = len(df_b.columns)
        
        if df_m is not None:
            n_pr = pd.to_numeric(df_m.iloc[:,1], errors='coerce').notna().sum()
            self.app.session["n_pr"] = n_pr

        self._mostrar_resumen()

    def _mostrar_resumen(self):
        for w in self.zona_resumen.winfo_children(): w.destroy()
        
        # Tarjeta Única Centralizada
        card = ctk.CTkFrame(self.zona_resumen, fg_color=COLORS.bg_card, corner_radius=DIMS.card_radius, border_width=1, border_color=COLORS.border)
        card.grid(row=0, column=0, padx=20, sticky="ew")
        card.grid_columnconfigure((0, 1), weight=1)

        # Encabezado: Tipo de Modelo
        tipo = self.app.session.get("tipo_modelo", "M1 — Consumo Absoluto")
        ctk.CTkLabel(card, text=tipo, font=(FONTS.family, FONTS.size_md, "bold"), text_color=COLORS.accent).grid(row=0, column=0, columnspan=2, pady=(20, 15))

        # Columna Izquierda: ID
        f_id = ctk.CTkFrame(card, fg_color="transparent")
        f_id.grid(row=1, column=0, sticky="nsew", padx=(40, 20), pady=(0, 25))
        items = [
            (f"🏢 Entidad: {self.app.session.get('nombre', '---')}",),
            (f"⚡ Fuente: {self.app.session.get('fuente', '---')}",),
            (f"📐 Unidad: {self.app.session.get('unidad', '---')}",),
            (f"📅 Periodo Base: {self.app.session.get('pb_ini', '---')} - {self.app.session.get('pb_fin', '---')}",)
        ]
        for txt, in items:
            ctk.CTkLabel(f_id, text=txt, font=(FONTS.family, FONTS.size_xs), text_color=COLORS.text_primary, anchor="w").pack(fill="x", pady=2)

        # Columna Derecha: Stats
        f_st = ctk.CTkFrame(card, fg_color="transparent")
        f_st.grid(row=1, column=1, sticky="nsew", padx=(20, 40), pady=(0, 25))
        stats = [
            (f"📊 Registros Periodo Base: {self.app.session.get('n_pb', 0)} datos",),
            (f"📈 Registros Monitoreo: {self.app.session.get('n_pr', 0)} datos",),
            (f"✅ Columnas encontradas: {self.app.session.get('n_cols', 0)}",)
        ]
        for txt, in stats:
            ctk.CTkLabel(f_st, text=txt, font=(FONTS.family, FONTS.size_xs), text_color=COLORS.text_secondary, anchor="w").pack(fill="x", pady=2)

        # Botón Calcular (debajo de la tarjeta)
        ctk.CTkButton(self.zona_resumen, text="⚙️ Calcular Línea Base y Desempeño", font=(FONTS.family, FONTS.size_md, "bold"),
                      fg_color=COLORS.accent, text_color=COLORS.primary, height=48, command=self._procesar).grid(row=1, column=0, pady=30)

    def _procesar(self):
        if self.df_base is None: return
        try:
            df_lben, df_mon, df_bf, df_exc = procesar_m1(self.df_base, self.df_monitoreo)
            metricas = calcular_resumen_metricas(df_lben, self.df_base)
            
            self.app.session.update({
                "df_base_raw": self.df_base,
                "df_base_final": df_bf,
                "df_excluidos": df_exc,
                "df_lben": df_lben,
                "df_monitoreo": df_mon,
                "metricas_m1": metricas,
                "meta_m1": self.app.session,
                "excel_path": self.current_path
            })
            self.app.navegar("m1_resultados")
        except Exception as e:
            messagebox.showerror("Error", f"Fallo en el cálculo: {e}")
