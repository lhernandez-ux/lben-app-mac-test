"""
ui/pages/guia_usuario.py
========================
Página de guía de usuario (En construcción).
"""

import customtkinter as ctk
from ui.theme import COLORS, FONTS

class GuiaUsuarioPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        self._build()

    def _build(self):
        # Contenedor central
        cnt = ctk.CTkFrame(self, fg_color="transparent")
        cnt.place(relx=0.5, rely=0.5, anchor="center")

        # Iconos de construcción
        ctk.CTkLabel(
            cnt, text="🚧",
            font=(FONTS.family, 64)
        ).pack(pady=10)

        # Título
        ctk.CTkLabel(
            cnt, text="Módulo en Construcción",
            font=(FONTS.family, FONTS.size_title, "bold"),
            text_color=COLORS.primary
        ).pack()

        # Descripción
        ctk.CTkLabel(
            cnt, 
            text="Estamos preparando la Guía de Usuario para que puedas aprovechar\nal máximo todas las capacidades de la Herramienta LBEn.\n\nPróximamente disponible.",
            font=(FONTS.family, FONTS.size_md),
            text_color=COLORS.text_secondary,
            justify="center"
        ).pack(pady=20)

        # Botón Volver
        ctk.CTkButton(
            cnt,
            text="Regresar al Inicio",
            font=(FONTS.family, FONTS.size_sm, "bold"),
            fg_color=COLORS.primary,
            text_color="white",
            command=lambda: self.app.navegar("home")
        ).pack(pady=10)
