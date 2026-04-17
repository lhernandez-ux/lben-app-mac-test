"""
ui/theme.py
===========
ADN Visual — LBEn App
Paleta: Proyectos E2
"""

import customtkinter as ctk

# ── Paleta de colores ─────────────────────────────────────────────────────────
class COLORS:
    # Primarios
    bg_main        = "#EAEAEA"       # Fondo base (light grey)
    primary        = "#204339"       # Verde oscuro (primario)
    primary_dark   = "#162E27"       # Verde muy oscuro (sidebar)
    accent         = "#C2D500"       # Lima (acento)

    # Superficies
    bg_card        = "#FFFFFF"       # Fondo de tarjetas
    bg_sidebar     = "#162E27"       # Fondo sidebar
    border         = "#D0D5CC"       # Bordes suaves

    # Texto
    text_primary   = "#1A1A1A"       # Texto principal
    text_secondary = "#5A6B63"       # Texto secundario
    text_white     = "#FFFFFF"       # Texto sobre fondo oscuro
    text_accent    = "#C2D500"       # Texto acento (sobre primario)

    # Semánticos
    success        = "#2D6A4F"       # Verde éxito
    warning        = "#F4A261"       # Naranja advertencia
    danger         = "#E63946"       # Rojo error
    improvement    = "#40916C"       # Verde mejora
    degradation    = "#E63946"       # Rojo degradación

    # Gradiente especial (para cards destacadas)
    gradient_start = "#162E27"
    gradient_mid   = "#204339"
    gradient_end   = "#C2D500"

    azul           ="#4B85F1"


# ── Tipografía ────────────────────────────────────────────────────────────────
class FONTS:
    family      = "Inter"
    family_mono = "Courier New"

    size_xs     = 11
    size_sm     = 12
    size_md     = 13
    size_lg     = 15
    size_xl     = 18
    size_xxl    = 24
    size_title  = 30


# ── Dimensiones ───────────────────────────────────────────────────────────────
class DIMS:
    sidebar_width    = 220
    topbar_height    = 50
    card_radius      = 10
    button_radius    = 20       # Pill buttons
    padding_card     = 20
    padding_section  = 30


# ── Configuración global CustomTkinter ───────────────────────────────────────
def aplicar_tema():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")