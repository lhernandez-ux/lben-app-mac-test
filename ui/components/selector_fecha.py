"""
ui/components/selector_fecha.py
==============================
Componente de selección de Mes/Año.
"""

import customtkinter as ctk
from datetime import datetime
from ui.theme import COLORS, FONTS

class SelectorFecha(ctk.CTkFrame):
    """
    Componente para seleccionar Mes y Año mediante menús desplegables.
    Retorna la fecha en formato MM/AAAA.
    """
    def __init__(self, master, label_text="Fecha", start_year=2015, end_year=2030, command=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.command = command
        self.meses_nombres = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        self.meses_map = {name: str(i+1).zfill(2) for i, name in enumerate(self.meses_nombres)}
        self.anios = [str(y) for y in range(start_year, end_year + 1)]

        # Layout
        self.grid_columnconfigure(0, weight=1)
        
        # Etiqueta opcional
        if label_text:
            self.label = ctk.CTkLabel(
                self, text=label_text,
                font=(FONTS.family, FONTS.size_xs),
                text_color=COLORS.text_secondary,
                anchor="w"
            )
            self.label.pack(side="top", anchor="w", pady=(0, 4))

        # Contenedor de menus
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="x")

        # Menu Mes
        self.combo_mes = ctk.CTkOptionMenu(
            self.container,
            values=self.meses_nombres,
            command=self._on_change,
            font=(FONTS.family, FONTS.size_sm),
            fg_color=COLORS.bg_card,
            button_color=COLORS.primary,
            button_hover_color=COLORS.primary_dark,
            text_color=COLORS.text_primary,
            dropdown_fg_color=COLORS.bg_card,
            dropdown_text_color=COLORS.text_primary,
            dropdown_hover_color=COLORS.bg_main,
            height=38,
            width=120
        )
        self.combo_mes.pack(side="left", padx=(0, 8))
        self.combo_mes.set("Enero")

        # Menu Año
        self.combo_anio = ctk.CTkOptionMenu(
            self.container,
            values=self.anios,
            command=self._on_change,
            font=(FONTS.family, FONTS.size_sm),
            fg_color=COLORS.bg_card,
            button_color=COLORS.primary,
            button_hover_color=COLORS.primary_dark,
            text_color=COLORS.text_primary,
            dropdown_fg_color=COLORS.bg_card,
            dropdown_text_color=COLORS.text_primary,
            dropdown_hover_color=COLORS.bg_main,
            height=38,
            width=100
        )
        self.combo_anio.pack(side="left")
        
        # Año actual por defecto o el último disponible
        current_year = str(datetime.now().year)
        if current_year in self.anios:
            self.combo_anio.set(current_year)
        else:
            self.combo_anio.set(self.anios[-1])

    def _on_change(self, _=None):
        if self.command:
            self.command()

    def get_value(self) -> str:
        """Retorna formato MM/AAAA"""
        mes = self.meses_map[self.combo_mes.get()]
        anio = self.combo_anio.get()
        return f"{mes}/{anio}"

    def set_value(self, mm_aaaa: str):
        """Establece el valor desde un string MM/AAAA"""
        try:
            mm, aaaa = mm_aaaa.split("/")
            idx = int(mm) - 1
            if 0 <= idx < 12:
                self.combo_mes.set(self.meses_nombres[idx])
            if aaaa in self.anios:
                self.combo_anio.set(aaaa)
        except:
            pass
