"""
ui/pages/m3_carga.py
====================
Página de carga de datos para el Modelo M3 (Regresión Multivariable).
ADN Identico a M1.
"""

import customtkinter as ctk
import os
import pandas as pd
from tkinter import filedialog, messagebox
from ui.theme import COLORS, FONTS, DIMS
from core.models.m3_regresion import ejecutar_modelo_m3
from core.io_excel import leer_excel_m1, _leer_hoja_datos_generica
from openpyxl import load_workbook

class M3CargaPage(ctk.CTkFrame):
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
        self._build_topbar()
        self._build_cuerpo()

    def _build_topbar(self):
        topbar = ctk.CTkFrame(self, fg_color=COLORS.bg_card, height=DIMS.topbar_height, corner_radius=0)
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)

        ctk.CTkFrame(topbar, fg_color=COLORS.accent, height=2).place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        ctk.CTkButton(
            topbar, text="← Inicio", font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent", text_color=COLORS.primary, width=90, height=32,
            command=lambda: self.app.navegar("home")
        ).grid(row=0, column=0, padx=16, pady=8, sticky="w")

        ctk.CTkLabel(
            topbar, text="Modelo M3: Regresión Multivariable — Carga de Datos",
            font=(FONTS.family, FONTS.size_md, "bold"), text_color=COLORS.primary
        ).grid(row=0, column=1, sticky="w", padx=8)

    def _build_cuerpo(self):
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS.bg_main, corner_radius=0)
        self.scroll.grid(row=1, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

        # Card de Selección
        self._card_seleccion = ctk.CTkFrame(self.scroll, fg_color=COLORS.bg_card, corner_radius=DIMS.card_radius, border_width=1, border_color=COLORS.border)
        self._card_seleccion.grid(row=0, column=0, padx=40, pady=(20, 20), sticky="ew")
        
        ctk.CTkLabel(self._card_seleccion, text="Selecciona el archivo Excel M3 configurado", 
                     font=(FONTS.family, FONTS.size_sm), text_color=COLORS.text_secondary).pack(pady=(32, 16))
        
        self.btn_sel = ctk.CTkButton(self._card_seleccion, text="📁 Seleccionar Archivo / Plantilla M3", 
                                     font=(FONTS.family, FONTS.size_md, "bold"),
                                     fg_color=COLORS.primary, height=48, command=self._seleccionar_archivo)
        self.btn_sel.pack(pady=(0, 8))
        
        self.lbl_filename = ctk.CTkLabel(self._card_seleccion, text="Ningún archivo seleccionado", 
                                         font=(FONTS.family, FONTS.size_xs), text_color=COLORS.text_secondary)
        self.lbl_filename.pack(pady=(0, 32))

        self.zona_resumen = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.zona_resumen.grid(row=1, column=0, sticky="nsew")
        self.zona_resumen.grid_columnconfigure(0, weight=1)

    def _seleccionar_archivo(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if not path: return
        
        try:
            # 1. Leer estructura básica (Fecha y Metadatos)
            from core.io_excel import leer_excel_m1
            df_b, df_m, meta, errores = leer_excel_m1(path)
            
            # 2. Releer con Pandas para capturar las 5 variables multivariable
            from core.io_excel import _leer_hoja_datos_generica
            
            # Nota: self.df_base se arma a medida para captar las variables multivariable
            # pero self.df_monitoreo puede usar la lógica genérica robusta que acabamos de mejorar
            wb_obj = load_workbook(path, data_only=True)
            self.df_monitoreo = _leer_hoja_datos_generica(wb_obj["Monitoreo"])

            # Proceso para df_base (Multivariable)
            xl = pd.ExcelFile(path)
            df_full = pd.read_excel(xl, sheet_name="Período_Base", skiprows=5)
            df_full.columns = [str(c).strip() for c in df_full.columns]
            
            cols_lista = df_full.columns.tolist()
            vars_cols = []
            for i in range(4, 9):
                if i < len(cols_lista):
                    cname = str(cols_lista[i]).strip()
                    if "Unnamed" not in cname and cname != "—" and not cname.startswith("—."):
                        vars_cols.append(cname)

            col_fecha = cols_lista[1] if len(cols_lista) > 1 else "Fecha"
            col_consumo = cols_lista[2] if len(cols_lista) > 2 else "Consumo"

            self.df_base = df_full[[col_fecha, col_consumo] + vars_cols].dropna(subset=[col_fecha])
            # Filtrar df_base para que solo tenga registros con consumo (como en M1)
            self.df_base = self.df_base[pd.to_numeric(self.df_base[col_consumo], errors='coerce') > 0].head(len(df_b))
            self.df_base.rename(columns={col_fecha: "Fecha", col_consumo: "Consumo"}, inplace=True)

            self.current_path = path
            self.lbl_filename.configure(text=f"✓ {os.path.basename(path)}", text_color=COLORS.success)
            
            # Sincronizar session
            self.app.session.update({
                "m3_config": {
                    "nombre": meta["entidad"], "fuente": meta["fuente"], "unidad": meta["unidad"],
                    "zona": meta.get("zona", "Templada"), "area": meta.get("area", "---"),
                    "vars_ind": vars_cols
                },
                "n_pb": len(self.df_base), "n_pr": len(self.df_monitoreo), "vars_detectadas": vars_cols,
                "pb_ini": str(self.df_base["Fecha"].iloc[0]), "pb_fin": str(self.df_base["Fecha"].iloc[-1])
            })
            self._mostrar_resumen()
            
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al leer archivo: {e}")

    def _mostrar_resumen(self):
        for w in self.zona_resumen.winfo_children():
            w.destroy()

        conf = self.app.session.get("m3_config", {})

        # Ficha de Resumen Premium (idéntica a M2)
        card = ctk.CTkFrame(
            self.zona_resumen,
            fg_color=COLORS.bg_card,
            corner_radius=DIMS.card_radius,
            border_width=1,
            border_color=COLORS.border
        )
        card.grid(row=0, column=0, padx=40, sticky="ew")
        card.grid_columnconfigure((0, 1), weight=1)

        # Encabezado
        ctk.CTkLabel(
            card,
            text="M3 (Regresión Multivariable)",
            font=(FONTS.family, FONTS.size_md, "bold"),
            text_color=COLORS.accent
        ).grid(row=0, column=0, columnspan=2, pady=(20, 15))

        # Columna Izquierda: Identificación
        f_id = ctk.CTkFrame(card, fg_color="transparent")
        f_id.grid(row=1, column=0, sticky="nsew", padx=(40, 20), pady=(0, 25))

        items = [
            f"🏢 Entidad: {conf.get('nombre', '---')}",
            f"⚡ Fuente: {conf.get('fuente', '---')}",
            f"📐 Unidad: {conf.get('unidad', '---')}",
            f"🌍 Zona: {conf.get('zona', '---')}",
            f"📏 Área Útil: {conf.get('area', '---')}",
            f"📅 Periodo Base: {self.app.session.get('pb_ini', '---')} - {self.app.session.get('pb_fin', '---')}"
        ]
        for txt in items:
            ctk.CTkLabel(
                f_id,
                text=txt,
                font=(FONTS.family, FONTS.size_xs),
                text_color=COLORS.text_primary,
                anchor="w"
            ).pack(fill="x", pady=2)

        # Columna Derecha: Estadísticas
        f_st = ctk.CTkFrame(card, fg_color="transparent")
        f_st.grid(row=1, column=1, sticky="nsew", padx=(20, 40), pady=(0, 25))

        vars_txt = ", ".join(conf.get("vars_ind", [])) if conf.get("vars_ind") else "---"

        stats = [
            f"📊 Registros Periodo Base: {self.app.session.get('n_pb', 0)} datos",
            f"📈 Registros Monitoreo: {self.app.session.get('n_pr', 0)} datos",
            f"🔗 Variables encontradas: {vars_txt}"
        ]
        for txt in stats:
            ctk.CTkLabel(
                f_st,
                text=txt,
                font=(FONTS.family, FONTS.size_xs),
                text_color=COLORS.text_secondary,
                anchor="w"
            ).pack(fill="x", pady=2)

        # Botón ejecutar (idéntico estilo M2)
        self.btn_calc = ctk.CTkButton(
            self.zona_resumen,
            text="🚀 Ejecutar Modelo M3 (Regresión)",
            font=(FONTS.family, FONTS.size_md, "bold"),
            fg_color=COLORS.accent,
            text_color=COLORS.primary,
            height=48,
            command=self._procesar
        )
        self.btn_calc.grid(row=2, column=0, pady=30)

    def _procesar(self):
        try:
            config = self.app.session.get("m3_config")
            res = ejecutar_modelo_m3(self.df_base, self.df_monitoreo, "Consumo", config["vars_ind"])
            self.app.session["results_m3"] = res
            self.app.session["excel_path"] = self.current_path
            self.app.navegar("m3_resultados")
        except Exception as e:
            messagebox.showerror("Error", f"Error en el motor M3: {e}")
