"""
ui/pages/informe_upme.py
========================
Página para generar el Informe Oficial UPME 016 (En construcción).
"""

import customtkinter as ctk
from ui.theme import COLORS, FONTS

class InformeUPMEPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        self._build()

    def _build(self):
        # Contenedor central
        cnt = ctk.CTkFrame(self, fg_color="transparent")
        cnt.place(relx=0.5, rely=0.5, anchor="center")

        # Icono de Reporte
        ctk.CTkLabel(
            cnt, text="📄",
            font=(FONTS.family, 64)
        ).pack(pady=10)

        # Título
        ctk.CTkLabel(
            cnt, text="Informe UPME Resolución 016 de 2024",
            font=(FONTS.family, FONTS.size_title, "bold"),
            text_color=COLORS.primary
        ).pack()

        # Descripción del objetivo
        ctk.CTkLabel(
            cnt, 
            text="Este módulo permitirá cargar un proyecto existente para:\n\n"
                 "1. Visualizar el resumen general de la Línea Base y Desempeño.\n"
                 "2. Consultar oportunidades de mejora, recomendaciones e información de interés.\n"
                 "3. Incluir observaciones manuales y conclusiones.\n"
                 "4. Generar y descargar el Reporte Ejecutivo Oficial en PDF.\n\n"
                 "Módulo en desarrollo.",
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
