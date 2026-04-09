"""
ui/app.py
=========
Ventana principal y navegación entre pantallas.
"""

import customtkinter as ctk
from ui.theme import COLORS, FONTS, DIMS


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ── Configuración ventana ─────────────────────────────────────────────
        self.title("Línea Base Energética — UPME 016/2024")
        self.geometry("1100x700")
        self.minsize(1000, 650)
        self.configure(fg_color=COLORS.bg_main)

        # ── Estado global de sesión ───────────────────────────────────────────
        self.session = {
            "ruta": None,               # "exploratorio" | "modelado" | "monitoreo"
            "proyecto_nombre": None,
            "fecha_inicio": None,
            "fecha_fin": None,
            "var_dependiente": None,
            "vars_independientes": [],
            "excel_path": None,         # ruta al Excel cargado
            "df_datos": None,           # DataFrame con datos cargados
            "resultados_exploratorio": None,
        }

        # ── Contenedor principal ──────────────────────────────────────────────
        self._frame_actual = None
        self._iniciar_navegacion()

    # ── Navegación ────────────────────────────────────────────────────────────
    def _iniciar_navegacion(self):
        self.navegar("home")

    def navegar(self, destino: str, **kwargs):
        """
        Destruye el frame actual y carga el nuevo.
        destino: nombre de la pantalla
        kwargs:  parámetros opcionales para la pantalla destino
        """
        if self._frame_actual is not None:
            self._frame_actual.destroy()

        frame = self._crear_frame(destino, **kwargs)
        frame.pack(fill="both", expand=True)
        self._frame_actual = frame

    def _crear_frame(self, destino: str, **kwargs):
        # Importaciones locales para evitar ciclos
        if destino == "home":
            from ui.pages.home import HomePage
            return HomePage(self)

        elif destino == "exploratorio_config":
            from ui.pages.exploratorio_config import ExploratorioConfigPage
            return ExploratorioConfigPage(self)

        elif destino == "exploratorio_carga":
            from ui.pages.exploratorio_carga import ExploratorioCargaPage
            return ExploratorioCargaPage(self)

        elif destino == "exploratorio_resultados":
            from ui.pages.exploratorio_resultados import ExploratorioResultadosPage
            return ExploratorioResultadosPage(self)

        elif destino == "seleccion_modelo":
            from ui.pages.seleccion_modelo import SeleccionModeloPage
            return SeleccionModeloPage(self)

        elif destino == "m1_config":
            from ui.pages.m1_config import M1ConfigPage
            return M1ConfigPage(self)

        elif destino == "m1_carga":
            from ui.pages.m1_carga import M1CargaPage
            return M1CargaPage(self)

        elif destino == "m1_resultados":
            from ui.pages.m1_resultados import M1ResultadosPage
            return M1ResultadosPage(self)

        else:
            raise ValueError(f"Destino desconocido: {destino}")