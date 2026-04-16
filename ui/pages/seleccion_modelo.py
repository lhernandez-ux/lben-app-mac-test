"""
ui/pages/seleccion_modelo.py
=============================
Pantalla de selección de modelo.
Muestra los 3 modelos disponibles con la recomendación destacada.
"""

import customtkinter as ctk
from ui.theme import COLORS, FONTS, DIMS
from ui.utils import resource_path


class SeleccionModeloPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        self._recomendacion = self._obtener_recomendacion()
        self._build()

    def _obtener_recomendacion(self) -> str:
        """Obtiene el código del modelo recomendado desde la sesión."""
        res = self.app.session.get("resultados_exploratorio")
        if res and "recomendacion" in res:
            return res["recomendacion"].get("codigo", "")
        return ""

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

        ctk.CTkButton(
            topbar,
            text="← Exploración",
            font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent",
            text_color=COLORS.primary,
            hover_color=COLORS.bg_main,
            width=110, height=32,
            corner_radius=DIMS.button_radius,
            command=lambda: self.app.navegar("exploratorio_resultados")
        ).grid(row=0, column=0, padx=16, pady=8, sticky="w")

        ctk.CTkLabel(
            topbar,
            text="Selecciona el modelo de LBEn",
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

    # ── Cuerpo ────────────────────────────────────────────────────────────────
    def _build_cuerpo(self):
        cuerpo = ctk.CTkFrame(
            self, fg_color=COLORS.bg_main, corner_radius=0
        )
        cuerpo.grid(row=1, column=0, sticky="nsew")
        cuerpo.grid_columnconfigure(0, weight=1)
        cuerpo.grid_rowconfigure(1, weight=1)

        # Subtítulo
        ctk.CTkLabel(
            cuerpo,
            text="Elige el modelo que mejor se adapte a tus datos y objetivos."
                 " Aparecerá resaltado el modelo recomendado en el ultimo análisis exploratorio",
            font=(FONTS.family, FONTS.size_sm),
            text_color=COLORS.text_secondary,
            justify="left"
        ).grid(row=0, column=0, sticky="w", padx=48, pady=(24, 16))

        # Grid de 3 cards
        cards_frame = ctk.CTkFrame(cuerpo, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="nsew", padx=48, pady=(0, 32))
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
        cards_frame.grid_rowconfigure(0, weight=1)

        modelos = [
            {
                "codigo":    "M1",
                "titulo":    "Consumo Absoluto",
                "subtitulo": "Promedios Mensuales",
                "descripcion": (
                    "Estima la línea base como el promedio del "
                    "consumo histórico mensual.\n\n"
                    "Ideal cuando el consumo es relativamente "
                    "constante y no depende o no se dispone de variables externas."
                ),
                "variables": "Solo consumo energético",
                "recomendado_para": "Edificios con consumo estable",
                "destino": "m1_config"
            },
            {
                "codigo":    "M2",
                "titulo":    "Modelo de Cociente",
                "subtitulo": "Consumo Normalizado",
                "descripcion": (
                    "Calcula un índice de consumo energético "
                    "normalizado por una variable (Ej: kWh/visitantes).\n\n"
                    "Útil cuando el consumo escala proporcionalmente con una sola "
                    "variable como usuarios o área."
                ),
                "variables": "Consumo + 1 variable",
                "recomendado_para": "Edificios con ocupación variable",
                "destino": "m2_config"
            },
            {
                "codigo":    "M3",
                "titulo":    "Modelos Estadísticos",
                "subtitulo": "Regresión Lineal",
                "descripcion": (
                    "Calcula el consumo en función de una o más "
                    "variables independientes estadísticamente "
                    "significativas.\n\n"
                    "Puede detectar relaciones complejas entre variables"
                ),
                "variables": "Consumo + 1 o más variables significativas",
                "recomendado_para": "Edificios con múltiples variables disponibles",
                "destino": "m3_config"
            }
        ]

        for col, modelo in enumerate(modelos):
            es_rec = modelo["codigo"] == self._recomendacion
            self._build_card_modelo(cards_frame, modelo, col, es_rec)

    # ── Card modelo ───────────────────────────────────────────────────────────
    def _build_card_modelo(self, parent, modelo, col, es_recomendado):
        # Estilo según si es recomendado
        if es_recomendado:
            fg_card    = COLORS.primary
            fg_icono   = COLORS.accent
            fg_titulo  = COLORS.text_white
            fg_sub     = COLORS.accent
            fg_desc    = "#A8C4BC"
            fg_label   = "#7A9B8E"
            fg_val     = "#C8DDD8"
            btn_fg     = COLORS.accent
            btn_txt    = COLORS.primary
            btn_hover  = "#D4E800"
            border_c   = COLORS.accent
        else:
            fg_card    = COLORS.bg_card
            fg_icono   = COLORS.primary
            fg_titulo  = COLORS.primary
            fg_sub     = COLORS.text_secondary
            fg_desc    = COLORS.text_secondary
            fg_label   = COLORS.text_secondary
            fg_val     = COLORS.text_primary
            btn_fg     = COLORS.primary
            btn_txt    = COLORS.text_white
            btn_hover  = COLORS.primary_dark
            border_c   = COLORS.border

        card = ctk.CTkFrame(
            parent,
            fg_color=fg_card,
            corner_radius=DIMS.card_radius,
            border_width=2 if es_recomendado else 1,
            border_color=border_c
        )
        card.grid(
            row=0, column=col,
            padx=(0, 12) if col < 2 else 0,
            sticky="nsew", pady=4
        )
        card.grid_columnconfigure(0, weight=1)

        # Badge recomendado
        if es_recomendado:
            badge = ctk.CTkFrame(card, fg_color=COLORS.success, corner_radius=10, height=24)
            badge.place(relx=1.0, x=-10, y=10, anchor="ne")
            ctk.CTkLabel(
                badge, text="RECOMENDADO", 
                font=(FONTS.family, 10, "bold"),
                text_color="white", padx=10
            ).pack()
        else:
            ctk.CTkFrame(
                card, fg_color="transparent", height=24
            ).grid(row=0, column=0, padx=16, pady=(16, 0), sticky="w")

        # Ícono / Ilustración
        from PIL import Image
        import os
        
        modelo_id = modelo["codigo"]
        icon_map = {"M1": "m1_icon.png", "M2": "m2_icon.png", "M3": "m3_icon.png"}
        icon_path = resource_path(os.path.join("assets", icon_map.get(modelo_id, "m1_icon.png")))
        
        try:
            pil_img = Image.open(icon_path)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(48, 48))
            icon_label = ctk.CTkLabel(card, text="", image=ctk_img)
            icon_label.grid(row=1, column=0, padx=16, pady=(8, 0), sticky="w")
        except:
            ctk.CTkLabel(
                card, text="📊", font=(FONTS.family, 32),
                text_color=fg_icono
            ).grid(row=1, column=0, padx=16, pady=(8, 0), sticky="w")

        # Título
        ctk.CTkLabel(
            card,
            text=modelo["titulo"],
            font=(FONTS.family, FONTS.size_md, "bold"),
            text_color=fg_titulo
        ).grid(row=2, column=0, padx=16, pady=(16, 0), sticky="w")

        # Subtítulo
        ctk.CTkLabel(
            card,
            text=modelo["subtitulo"],
            font=(FONTS.family, FONTS.size_xs),
            text_color=fg_sub
        ).grid(row=3, column=0, padx=16, pady=(0, 12), sticky="w")

        # Separador
        ctk.CTkFrame(
            card,
            fg_color=COLORS.accent if es_recomendado else COLORS.border,
            height=1, corner_radius=0
        ).grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 12))

        # Descripción
        ctk.CTkLabel(
            card,
            text=modelo["descripcion"],
            font=(FONTS.family, FONTS.size_xs),
            text_color=fg_desc,
            wraplength=240,
            justify="center"
        ).grid(row=5, column=0, padx=16, pady=(0, 16))

        # --- FILA ELÁSTICA (ESPACIADOR) ---
        # Fila 6 absorbe espacio y empuja lo demás al fondo
        card.grid_rowconfigure(6, weight=1)
        ctk.CTkFrame(card, fg_color="transparent", height=1).grid(row=6, column=0)

        # Variables (Cuadro Gris)
        info_frame = ctk.CTkFrame(
            card,
            fg_color=COLORS.primary_dark if es_recomendado else COLORS.bg_main,
            corner_radius=8
        )
        info_frame.grid(row=7, column=0, sticky="ew",
                        padx=16, pady=(0, 12))

        ctk.CTkLabel(
            info_frame,
            text="Variables:",
            font=(FONTS.family, FONTS.size_xs, "bold"),
            text_color=fg_label, anchor="w"
        ).pack(anchor="w", padx=12, pady=(8, 2))

        ctk.CTkLabel(
            info_frame,
            text=modelo["variables"],
            font=(FONTS.family, FONTS.size_xs),
            text_color=fg_val, anchor="w",
            wraplength=220, justify="left"
        ).pack(anchor="w", padx=12, pady=(0, 4))

        ctk.CTkLabel(
            info_frame,
            text="Recomendado para:",
            font=(FONTS.family, FONTS.size_xs, "bold"),
            text_color=fg_label, anchor="w"
        ).pack(anchor="w", padx=12, pady=(4, 2))

        ctk.CTkLabel(
            info_frame,
            text=modelo["recomendado_para"],
            font=(FONTS.family, FONTS.size_xs),
            text_color=fg_val, anchor="w",
            wraplength=220, justify="left"
        ).pack(anchor="w", padx=12, pady=(0, 8))

        # Botón configurar
        ctk.CTkButton(
            card,
            text="Configurar →",
            font=(FONTS.family, FONTS.size_sm, "bold"),
            fg_color=btn_fg,
            text_color=btn_txt,
            hover_color=btn_hover,
            corner_radius=DIMS.button_radius,
            height=40,
            command=lambda d=modelo["destino"]: self.app.navegar(d)
        ).grid(row=8, column=0, padx=16, pady=(0, 20), sticky="ew")