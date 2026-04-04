"""
ui/pages/home.py
================
Pantalla de bienvenida — Hub principal de navegación.
"""

import customtkinter as ctk
from ui.theme import COLORS, FONTS, DIMS


class HomePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=0)  # sidebar
        self.grid_columnconfigure(1, weight=1)  # contenido
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_contenido()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(
            self,
            fg_color=COLORS.bg_sidebar,
            width=DIMS.sidebar_width,
            corner_radius=0
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(6, weight=1)

        # Línea acento superior
        acento = ctk.CTkFrame(
            sidebar, fg_color=COLORS.accent,
            height=3, corner_radius=0
        )
        acento.pack(fill="x")

        # Logo / ícono
        ctk.CTkLabel(
            sidebar,
            text="⚡",
            font=(FONTS.family, 42),
            text_color=COLORS.accent
        ).pack(pady=(32, 8))

        # Nombre app
        ctk.CTkLabel(
            sidebar,
            text="Línea Base\nEnergética",
            font=(FONTS.family, FONTS.size_lg, "bold"),
            text_color=COLORS.text_white,
            justify="center"
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            sidebar,
            text="Resolución UPME\n016 de 2024",
            font=(FONTS.family, FONTS.size_xs),
            text_color="#7A9B8E",
            justify="center"
        ).pack(pady=(0, 24))

        # Separador
        ctk.CTkFrame(
            sidebar, fg_color="#2D4F45",
            height=1, corner_radius=0
        ).pack(fill="x", padx=20, pady=8)

        # Subtítulo
        ctk.CTkLabel(
            sidebar,
            text="Modelos de referencia para\neficiencia energética",
            font=(FONTS.family, FONTS.size_xs),
            text_color="#7A9B8E",
            justify="center",
            wraplength=180
        ).pack(pady=(16, 0), padx=16)

        # Versión al fondo
        ctk.CTkLabel(
            sidebar,
            text="v1.0.0",
            font=(FONTS.family, FONTS.size_xs),
            text_color="#4A6B5E"
        ).pack(side="bottom", pady=16)

    # ── Contenido principal ───────────────────────────────────────────────────
    def _build_contenido(self):
        contenido = ctk.CTkFrame(
            self, fg_color=COLORS.bg_main, corner_radius=0
        )
        contenido.grid(row=0, column=1, sticky="nsew")
        contenido.grid_columnconfigure(0, weight=1)
        contenido.grid_rowconfigure(3, weight=1)

        # ── Header ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(
            contenido, fg_color=COLORS.bg_main, corner_radius=0
        )
        header.grid(row=0, column=0, sticky="ew", padx=48, pady=(40, 0))

        ctk.CTkLabel(
            header,
            text="Bienvenido",
            font=(FONTS.family, FONTS.size_title, "bold"),
            text_color=COLORS.primary
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Esta herramienta te permite establecer la línea base de consumo\n"
                 "energético usando modelos estadísticos validados.",
            font=(FONTS.family, FONTS.size_md),
            text_color=COLORS.text_secondary,
            justify="left"
        ).pack(anchor="w", pady=(6, 0))

        # ── Cards de features ─────────────────────────────────────────────────
        features = ctk.CTkFrame(
            contenido, fg_color=COLORS.bg_main, corner_radius=0
        )
        features.grid(row=1, column=0, sticky="ew", padx=48, pady=(28, 0))

        self._feature_card(features, "📊", "3 Modelos",
                           "Promedio · Cociente · Regresión", 0)
        self._feature_card(features, "📥", "Plantilla Excel",
                           "Descarga y llena tus datos", 1)
        self._feature_card(features, "📈", "Gráficos",
                           "Línea base · Dispersión", 2)

        # ── Rutas principales ─────────────────────────────────────────────────
        rutas = ctk.CTkFrame(
            contenido, fg_color=COLORS.bg_main, corner_radius=0
        )
        rutas.grid(row=2, column=0, sticky="ew", padx=48, pady=(28, 0))
        rutas.grid_columnconfigure((0, 1), weight=1)

        # Card Análisis Exploratorio
        self._ruta_card(
            rutas,
            icono="🔍",
            titulo="Análisis Exploratorio",
            descripcion="No sé qué modelo usar.\nIdentificar variables y recibir\nrecomendación del sistema.",
            boton_texto="Empezar",
            boton_cmd=lambda: self.app.navegar("exploratorio_config"),
            destacado=True,
            col=0
        )

        # Card Modelado Directo
        self._ruta_card(
            rutas,
            icono="📋",
            titulo="Modelado Directo",
            descripcion="Ya sé qué modelo usar.\nIr directo a la configuración\nde un modelo específico.",
            boton_texto="Empezar",
            boton_cmd=lambda: self.app.navegar("seleccion_modelo"),
            destacado=False,
            col=1
        )

        # ── Botón abrir proyecto ──────────────────────────────────────────────
        footer = ctk.CTkFrame(
            contenido, fg_color=COLORS.bg_main, corner_radius=0
        )
        footer.grid(row=3, column=0, sticky="sew", padx=48, pady=(20, 32))
        footer.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            footer,
            text="📂  Abrir Proyecto o Seguimiento Existente",
            font=(FONTS.family, FONTS.size_md),
            fg_color=COLORS.bg_card,
            text_color=COLORS.primary,
            hover_color=COLORS.border,
            border_width=1,
            border_color=COLORS.border,
            corner_radius=DIMS.button_radius,
            height=44,
            command=lambda: self.app.navegar("exploratorio_carga")
        ).grid(row=0, column=0, sticky="ew")

        # Copyright
        ctk.CTkLabel(
            footer,
            text="© 2026 — Herramienta de análisis energético  |  UPME 016/2024",
            font=(FONTS.family, FONTS.size_xs),
            text_color=COLORS.text_secondary
        ).grid(row=1, column=0, pady=(8, 0))

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _feature_card(self, parent, icono, titulo, subtitulo, col):
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS.bg_card,
            corner_radius=DIMS.card_radius,
            border_width=1,
            border_color=COLORS.border
        )
        card.grid(row=0, column=col, padx=(0, 12) if col < 2 else 0,
                  sticky="ew")
        parent.grid_columnconfigure(col, weight=1)

        ctk.CTkLabel(
            card, text=icono,
            font=(FONTS.family, 24)
        ).pack(pady=(16, 4))

        ctk.CTkLabel(
            card, text=titulo,
            font=(FONTS.family, FONTS.size_sm, "bold"),
            text_color=COLORS.primary
        ).pack()

        ctk.CTkLabel(
            card, text=subtitulo,
            font=(FONTS.family, FONTS.size_xs),
            text_color=COLORS.text_secondary
        ).pack(pady=(2, 16))

    def _ruta_card(self, parent, icono, titulo, descripcion,
                   boton_texto, boton_cmd, destacado, col):
        fg = COLORS.primary if destacado else COLORS.bg_card
        txt = COLORS.text_white if destacado else COLORS.primary
        txt2 = "#A8C4BC" if destacado else COLORS.text_secondary
        btn_fg = COLORS.accent if destacado else COLORS.primary
        btn_txt = COLORS.primary if destacado else COLORS.text_white

        card = ctk.CTkFrame(
            parent,
            fg_color=fg,
            corner_radius=DIMS.card_radius,
            border_width=1,
            border_color=COLORS.border
        )
        card.grid(row=0, column=col,
                  padx=(0, 12) if col == 0 else 0,
                  sticky="nsew", pady=4)

        ctk.CTkLabel(
            card, text=icono,
            font=(FONTS.family, 28),
        ).pack(pady=(20, 6))

        ctk.CTkLabel(
            card, text=titulo,
            font=(FONTS.family, FONTS.size_lg, "bold"),
            text_color=txt
        ).pack()

        ctk.CTkLabel(
            card, text=descripcion,
            font=(FONTS.family, FONTS.size_sm),
            text_color=txt2,
            justify="center"
        ).pack(pady=(8, 16), padx=16)

        ctk.CTkButton(
            card,
            text=boton_texto,
            font=(FONTS.family, FONTS.size_sm, "bold"),
            fg_color=btn_fg,
            text_color=btn_txt,
            hover_color=COLORS.accent if not destacado else "#D4E800",
            corner_radius=DIMS.button_radius,
            height=38,
            command=boton_cmd
        ).pack(pady=(0, 20), padx=24, fill="x")