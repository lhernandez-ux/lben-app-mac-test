"""
ui/pages/exploratorio_carga.py
================================
Pantalla de carga del Excel exploratorio.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from ui.theme import COLORS, FONTS, DIMS


class ExploratorioCargaPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        self.archivo_path = None
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_topbar()
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

        # Botón regresar a configuración
        ctk.CTkButton(
            topbar,
            text="← Configuración",
            font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent",
            text_color=COLORS.primary,
            hover_color=COLORS.bg_main,
            width=120, height=32,
            corner_radius=DIMS.button_radius,
            command=lambda: self.app.navegar("exploratorio_config")
        ).grid(row=0, column=0, padx=16, pady=8, sticky="w")

        # Título
        ctk.CTkLabel(
            topbar,
            text="Cargar datos",
            font=(FONTS.family, FONTS.size_md, "bold"),
            text_color=COLORS.primary
        ).grid(row=0, column=1, sticky="w", padx=8)

        # Botón inicio
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

    # ── Cuerpo ────────────────────────────────────────────────────────────────
    def _build_cuerpo(self):
        cuerpo = ctk.CTkFrame(
            self, fg_color=COLORS.bg_main, corner_radius=0
        )
        cuerpo.grid(row=1, column=0, sticky="nsew")
        cuerpo.grid_columnconfigure(0, weight=1)
        cuerpo.grid_rowconfigure(1, weight=1)

        # ── Banner de sesión ──────────────────────────────────────────────────
        self._build_banner_sesion(cuerpo)

        # ── Card de carga ─────────────────────────────────────────────────────
        card = ctk.CTkFrame(
            cuerpo,
            fg_color=COLORS.bg_card,
            corner_radius=DIMS.card_radius,
            border_width=1,
            border_color=COLORS.border
        )
        card.grid(row=1, column=0, padx=48, pady=24, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)

        # Zona de drop / selección
        zona = ctk.CTkFrame(
            card, fg_color=COLORS.bg_main,
            corner_radius=8,
            border_width=2,
            border_color=COLORS.border
        )
        zona.grid(row=0, column=0, padx=32, pady=32, sticky="nsew")
        zona.grid_columnconfigure(0, weight=1)
        zona.grid_rowconfigure(0, weight=1)

        inner = ctk.CTkFrame(zona, fg_color="transparent")
        inner.grid(row=0, column=0)

        # Ícono carpeta
        ctk.CTkLabel(
            inner,
            text="📁",
            font=(FONTS.family, 48)
        ).pack(pady=(32, 8))

        ctk.CTkLabel(
            inner,
            text="Selecciona el archivo Excel con tus datos",
            font=(FONTS.family, FONTS.size_md, "bold"),
            text_color=COLORS.primary
        ).pack()

        ctk.CTkLabel(
            inner,
            text="El archivo debe tener la hoja 'Periodo_Analisis' con tus datos.",
            font=(FONTS.family, FONTS.size_sm),
            text_color=COLORS.text_secondary
        ).pack(pady=(4, 20))

        ctk.CTkButton(
            inner,
            text="Seleccionar archivo Excel",
            font=(FONTS.family, FONTS.size_sm, "bold"),
            fg_color=COLORS.primary,
            text_color=COLORS.text_white,
            hover_color=COLORS.primary_dark,
            corner_radius=DIMS.button_radius,
            height=40,
            width=220,
            command=self._seleccionar_archivo
        ).pack(pady=(0, 32))

        # Label de estado del archivo
        self.lbl_archivo = ctk.CTkLabel(
            card,
            text="Ningún archivo cargado",
            font=(FONTS.family, FONTS.size_sm),
            text_color=COLORS.text_secondary
        )
        self.lbl_archivo.grid(row=1, column=0, pady=(0, 8))

        # ── Botón continuar ───────────────────────────────────────────────────
        self.btn_continuar = ctk.CTkButton(
            cuerpo,
            text="Continuar a Análisis Exploratorio →",
            font=(FONTS.family, FONTS.size_md, "bold"),
            fg_color=COLORS.primary,
            text_color=COLORS.text_white,
            hover_color=COLORS.primary_dark,
            corner_radius=DIMS.button_radius,
            height=46,
            state="disabled",
            command=self._continuar
        )
        self.btn_continuar.grid(
            row=2, column=0,
            padx=48, pady=(0, 32),
            sticky="w"
        )

    def _build_banner_sesion(self, parent):
        """Muestra los parámetros de la sesión actual si existen."""
        sesion = self.app.session
        nombre   = sesion.get("proyecto_nombre", "")
        var_dep  = sesion.get("var_dependiente", "")
        f_ini    = sesion.get("fecha_inicio", "")
        f_fin    = sesion.get("fecha_fin", "")

        if not nombre and not var_dep:
            return

        banner = ctk.CTkFrame(
            parent,
            fg_color="#E8F5E9",
            corner_radius=8,
            border_width=1,
            border_color="#A5D6A7"
        )
        banner.grid(row=0, column=0, padx=48, pady=(20, 0), sticky="ew")

        texto = []
        if nombre:
            texto.append(f"Proyecto: {nombre}")
        if var_dep:
            texto.append(f"Consumo: {var_dep}")
        if f_ini and f_fin:
            texto.append(f"Período: {f_ini} — {f_fin}")

        ctk.CTkLabel(
            banner,
            text="  |  ".join(texto),
            font=(FONTS.family, FONTS.size_sm),
            text_color=COLORS.success
        ).pack(padx=16, pady=10)

    # ── Lógica ────────────────────────────────────────────────────────────────
    def _seleccionar_archivo(self):
        path = filedialog.askopenfilename(
            title="Seleccionar archivo Excel exploratorio",
            filetypes=[("Excel", "*.xlsx *.xls")]
        )
        if not path:
            return

        self.archivo_path = path
        nombre_archivo = os.path.basename(path)

        self.lbl_archivo.configure(
            text=f"✅  {nombre_archivo}",
            text_color=COLORS.success
        )
        self.btn_continuar.configure(state="normal")
        self.app.session["excel_path"] = path

    def _continuar(self):
        if not self.archivo_path:
            messagebox.showwarning(
                "Sin archivo",
                "Primero selecciona un archivo Excel."
            )
            return

        # Leer y validar el Excel
        from core.io_excel import leer_excel_exploratorio
        df, meta, errores = leer_excel_exploratorio(self.archivo_path)

        # Errores críticos
        if df is None:
            messagebox.showerror(
                "Error al leer archivo",
                "\n".join(errores)
            )
            return

        # Advertencias no críticas
        if errores:
            continuar = messagebox.askyesno(
                "Advertencias encontradas",
                "Se encontraron los siguientes problemas:\n\n" +
                "\n".join(f"• {e}" for e in errores) +
                "\n\n¿Deseas continuar de todas formas?"
            )
            if not continuar:
                return

        # Guardar en sesión
        self.app.session["df_datos"]        = df
        self.app.session["var_dependiente"] = meta.get("var_dep", "")
        self.app.session["vars_independientes"] = meta.get("vars_ind", [])

        self.app.navegar("exploratorio_resultados")