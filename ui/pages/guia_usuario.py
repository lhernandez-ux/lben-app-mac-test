"""
ui/pages/guia_usuario.py
========================
Versión Final de Alta Fidelidad — Master Design V5.
Recreación 1:1 de las infografías del usuario utilizando paneles densos y headers oscuros.
"""

import customtkinter as ctk
from PIL import Image
import os
from ui.theme import COLORS, FONTS, DIMS

# ═══════════════════════════════════════════════════════════════════════════════
# BASE DE DATOS DE TEXTOS - TRANSCRIPCIÓN INTEGRAL 1:1
# ═══════════════════════════════════════════════════════════════════════════════

CONTENIDO_FULL = {
    "hero": {
        "titulo": "PLATAFORMA DE LÍNEA BASE ENERGÉTICA",
        "subtitulo": "Guía de Usuario y Especificaciones Técnicas",
        "pilares": [
            ("Análisis histórico", "Procesa registros mensuales de consumo (kWh) y detecta patrones estadísticos con normalización automática a 30 días.", "📈"),
            ("Filtrado inteligente", "Excluye outliers manualmente o por intervalo de confianza, garantizando datos representativos.", "🔍"),
            ("Reporte descargable", "Genera automáticamente la hoja Modelo_LBEn con tablas y gráficos listos para la UPME.", "📄")
        ]
    },
    "modelos": {
        "titulo": "¿Qué modelo usar? — Árbol de Decisión",
        "pregunta": "¿Qué datos tienes disponibles?",
        "tip": "Si no tienes claro cuál modelo usar, activa el Análisis Exploratorio desde la pantalla de Bienvenida — el sistema identificará las variables disponibles y recomendará el modelo más adecuado.",
        "opciones": [
            {
                "cod": "M1", "tit": "Consumo Absoluto", "sub": "Solo consumo mensual",
                "var": "Variable: consumo facturado (kWh/mes)",
                "ideal": "Consumo relativamente estable. Sin variables externas.\nPunto de entrada. Máxima simplicidad.",
                "color": "#A4D400" # Lima UPME
            },
            {
                "cod": "M2", "tit": "Modelo de Cociente", "sub": "Consumo normalizado",
                "var": "Variables: consumo + 1 variable (ej. área, ocupación)",
                "ideal": "Consumo proporcional a una variable externa conocida.\nEdificios con ocupación o producción variable.",
                "color": "#00838F" # Teal
            },
            {
                "cod": "M3", "tit": "Modelos Estadísticos", "sub": "Regresión lineal",
                "var": "Variables: consumo + 1 o más variables significativas",
                "ideal": "Relaciones complejas entre variables (temperatura, jornada...).\nEdificios con múltiples variables disponibles.",
                "color": "#F59E0B" # Orange
            }
        ]
    },
    "flujo": {
        "titulo": "Flujo de Uso — Paso a Paso",
        "pasos": [
            ("01", "Configuración Inicial", "Define fuente de energía, unidad (kWh), zona climática, área útil y los períodos base y de seguimiento.\n\nEl sistema pre-configura la plantilla Excel con las columnas correctas y el rango temporal seleccionado."),
            ("02", "Descarga de Plantilla Excel", "Descarga el Excel-Proyecto generado. Contiene las hojas: Instrucciones, Periodo_Base, Modelo_LBEn y Monitoreo.\n\nLas columnas en AZUL son calculadas automáticamente por la app. Solo completa las columnas en VERDE."),
            ("03", "Edición de Datos", "Ingresa un registro por fila: Fecha, Consumo facturado (kWh) y Días del período de facturación.\n\nMínimo recomendado: 36 registros (3 años). Registra el valor TOTAL de la factura, no el promedio diario."),
            ("04", "Carga y Procesamiento", "Sube el archivo. La app valida la estructura, normaliza consumos a 30 días y ejecuta el filtrado estadístico.\n\nEl sistema aplica el IC al ±10% (N<10 datos/mes) o ±2σ (N≥10). Los outliers se documentan automáticamente."),
            ("05", "Resultados y Meta", "Visualiza la LBEn mensual, el ahorro potencial por mes y los indicadores globales del modelo.\n\nCompara tu consumo contra la LBEn y verifica el avance hacia la meta del 15% anual (Ley 2294/2023)."),
            ("06", "Reporte Final", "Descarga el Excel-Proyecto actualizado con la hoja Modelo_LBEn poblada: tablas, estadísticos y gráficos G1–G3.\n\nEste archivo es el documento oficial para el reporte anual obligatorio ante la UPME (Art. 9, Res. 016/2024).")
        ]
    },
    "excel": {
        "titulo": "Configuración y Plantilla Excel",
        "config_tabla": [
            ("Fuente de Energía", "Electricidad / Gas / Otro"),
            ("Unidad de medida", "kWh (predeterminado para electricidad)"),
            ("Zona Climática", "Cálida / Templada / Fría (según UPME)"),
            ("Área útil (m²)", "Opcional — requerida para indicadores de intensidad"),
            ("Período Base (inicio)", "Mes y año de inicio del histórico a analizar"),
            ("Período Base (fin)", "Mes y año de cierre del período base"),
            ("Inicio de Seguimiento", "Mes desde el cual se registrará desempeño futuro")
        ],
        "hojas": [
            ("Instrucciones", "Guía rápida de uso integrada. Referencia de pasos y normativa.", "Solo lectura", "#757575"),
            ("Periodo_Base", "Ingresa aquí tus consumos históricos. Columnas obligatorias: Fecha, Consumo_kWh, Días. Mínimo 36 filas.", "Usuario completa VERDE", "#388E3C"),
            ("Modelo_LBEn", "Escrita automáticamente por la app. Tabla LBEn mensual, ahorro potencial, estadísticos y gráficos.", "App escribe AUTO", "#00838F"),
            ("Monitoreo", "Registro continuo del desempeño mes a mes. Agrega filas de consumo real y la app calcula resultados.", "Usuario agrega filas", "#F59E0B")
        ]
    },
    "pipeline": {
        "titulo": "Carga, Procesamiento y Resultados",
        "header_pipeline": "PIPELINE DE PROCESAMIENTO (automático al cargar el archivo)",
        "items": [
            ("A", "Lectura y Validación", "Verifica columnas obligatorias, tipos de dato, rango de días (20–45) y duplicados. Errores críticos detienen el proceso; advertencias se documentan."),
            ("B", "Normalización a 30 días", "C_norm = (C_factura / días_período) x 30 (Ec.1 — UPME 016/2024). Permite comparar meses con diferentes ciclos de facturación."),
            ("C", "Filtrado Estadístico", "IC = ±10% si N<10 datos/mes (Ec.3) | IC = ±2σ si N≥10 (Ec.4-5). Datos fuera del IC se documentan. El filtrado se ejecuta una sola vez."),
            ("D", "Cálculo LBEn", "LBEn_m = Σ(C_norm_i) / m por cada mes m (Ec.2). Resultado: 12 valores de referencia mensual con límites inferior y superior."),
            ("E", "Ahorro Potencial", "Ahorro_m = LBEn_m – min(C_norm del mes m) (Ec.9). Expresa cuánto podría reducirse el consumo si todos los meses igualaran su mínimo histórico.")
        ],
        "kpis": [
            ("Consumo Promedio Anual", "136,758", "kWh/mes"),
            ("Ahorro Potencial Anual", "5,598", "kWh"),
            ("Ahorro Potencial (%)", "4.1%", "estimado")
        ],
        "alertas": [
            "Mínimo 12 registros post-filtrado",
            "Mes sin datos → excluido del modelo",
            "Duplicado → conserva primero, notifica"
        ]
    },
    "salidas": {
        "titulo": "Salidas del Modelo — Hoja Modelo_LBEn y Monitoreo",
        "tablas": [
            ("Tabla LBEn Mensual", "Valores históricos promedio por mes, límites superior/inferior y número de datos validados."),
            ("Tabla Ahorro Potencial", "Diferencia entre LBEn y mínimo histórico. Indica ahorro potencial en kWh y %."),
            ("Hoja Monitoreo — Seguimiento continuo", "")
        ],
        "monitoreo_puntos": [
            "Consumo real mes a mes vs LBEn mensual",
            "Desempeño energético (kWh y %) acumulado",
            "Avance % respecto meta 15% anual (Ley 2294/2023)",
            "Desempeño económico (COP ahorro/sobrecosto)",
            "Reducción de emisiones CO2e (kgCO2e)"
        ]
    },
    "glosario": {
        "titulo": "Glosario e Interpretación de Resultados",
        "tec": [
            ("LBEn (Línea Base Energética)", "Referencia histórica de consumo 'normal'. Promedio mensual calculado sobre el período base validado. Es el punto de comparación para detectar mejoras o deterioros."),
            ("Período Base", "Ventana histórica usada para construir la LBEn. Mínimo 12 meses (1 año); se recomiendan 36 meses (3 años) para mayor robustez estadística."),
            ("Normalización a 30 días", "Ajuste que convierte cualquier consumo facturado al equivalente de un mes exacto de 30 días: C_norm = (C_factura / días_período) x 30."),
            ("Intervalo de Confianza (IC)", "Rango válido para cada mes. Si N<10 datos: ±10% del promedio. Si N≥10: ±2 desviaciones estándar. Datos fuera del IC se consideran atípicos."),
            ("Ahorro Potencial", "Diferencia entre la LBEn mensual y el consumo mínimo histórico del mismo mes. Indica cuánto podría reducirse el consumo si se replicaran las mejores condiciones."),
            ("Meta 15%", "Reducción mínima anual exigida por la Ley 2294/2023 (Art. 237). La app calcula el consumo base anual y muestra el avance en la hoja de Monitoreo."),
            ("Ajuste No Rutinario (NR)", "Corrección que se aplica cuando un cambio estructural (obras, ampliación, cambio de uso) altera el consumo base de forma permanente y justificada.")
        ],
        "int": [
            ("Ahorro", "Consumo actual < LBEn mensual", "El edificio operó mejor que su referencia histórica ese mes. Identifica y documenta las condiciones que lo permitieron.", COLORS.success),
            ("Sobreconsumo", "Consumo actual > LBEn mensual", "Se superó el comportamiento esperado. Revisa fugas, equipos encendidos fuera de hora, cambios de uso o fallas de mantenimiento.", COLORS.danger),
            ("Colinealidad", "Variables correlacionadas entre sí", "Aplica solo en M3. Indica que dos o más variables se mueven juntas y pueden distorsionar el modelo. Sigue la sugerencia de exclusión de la app.", COLORS.warning),
            ("Meta 15%", "Compromiso Ley 2294/2023 (Art. 237)", "La reducción anual obligatoria se calcula sobre el consumo base del período base. La hoja Monitoreo muestra el avance acumulado mes a mes.", COLORS.primary),
            ("Reporte UPME", "Art. 9, Sección 9.2 — Res. 016/2024", "Los campos obligatorios (período base, 12 valores LBEn, desviación estándar, ahorro mensual kWh y %) están precargados en la hoja Modelo_LBEn.", COLORS.primary_dark)
        ]
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# COMPONENTES DE INTERFAZ FIDELIDAD 1:1
# ═══════════════════════════════════════════════════════════════════════════════

class GuiaUsuarioPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Barra Superior
        topbar = ctk.CTkFrame(self, fg_color=COLORS.bg_card, height=45, corner_radius=0)
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        ctk.CTkButton(topbar, text="← Volver al Inicio", font=(FONTS.family, 12), fg_color="transparent", text_color=COLORS.primary, command=lambda: self.app.navegar("home")).pack(side="left", padx=24)
        ctk.CTkLabel(topbar, text="CENTRO DE AYUDA — Resolución UPME 016/2024", font=(FONTS.family, 13, "bold"), text_color=COLORS.primary).pack(side="left")
        ctk.CTkFrame(topbar, fg_color=COLORS.accent, height=2).place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        # Scroll principal
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.scroll.grid_columnconfigure(0, weight=1)

        self._render_all()

    def _section_title_bar(self, text, icon=""):
        f = ctk.CTkFrame(self.scroll, fg_color=COLORS.primary_dark, height=45, corner_radius=0)
        f.pack(fill="x", pady=(40, 0))
        f.pack_propagate(False)
        ctk.CTkLabel(f, text=f"{icon}  {text}", font=(FONTS.family, 17, "bold"), text_color="white", anchor="w").pack(side="left", padx=25)
        ctk.CTkFrame(f, fg_color=COLORS.accent, height=3).place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

    def _render_all(self):
        # 0. Hero (Dark)
        self._render_hero()

        # 1. Modelos
        self._section_title_bar(CONTENIDO_FULL["modelos"]["titulo"], "🧠")
        self._render_modelos()

        # 2. Flujo
        self._section_title_bar(CONTENIDO_FULL["flujo"]["titulo"], "🚀")
        self._render_flujo()

        # 3. Excel
        self._section_title_bar(CONTENIDO_FULL["excel"]["titulo"], "⚙️")
        self._render_excel()

        # 4. Pipeline
        self._section_title_bar(CONTENIDO_FULL["pipeline"]["titulo"], "📋")
        self._render_pipeline()

        # 5. Salidas
        self._section_title_bar(CONTENIDO_FULL["salidas"]["titulo"], "📊")
        self._render_salidas()

        # 6. Glosario
        self._section_title_bar(CONTENIDO_FULL["glosario"]["titulo"], "📖")
        self._render_glosario()

        ctk.CTkFrame(self.scroll, fg_color="transparent", height=100).pack()

    # ── MÓDULOS ESPECÍFICOS ──────────────────────────────────────────

    def _render_hero(self):
        h = CONTENIDO_FULL["hero"]
        f = ctk.CTkFrame(self.scroll, fg_color="#10251F", corner_radius=25)
        f.pack(fill="x", pady=20, padx=20)
        f.grid_columnconfigure(0, weight=1)
        f.grid_columnconfigure(1, weight=2)

        # Logo
        logo_path = os.path.join("assets", "logo_lben.png")
        if os.path.exists(logo_path):
            img = ctk.CTkImage(Image.open(logo_path), size=(150, 150))
            ctk.CTkLabel(f, image=img, text="").grid(row=0, column=0, pady=60)

        # Titulacion
        txt = ctk.CTkFrame(f, fg_color="transparent")
        txt.grid(row=0, column=1, sticky="nsew", padx=(0, 40), pady=60)
        ctk.CTkLabel(txt, text=h["titulo"], font=(FONTS.family, 32, "bold"), text_color=COLORS.accent, anchor="w").pack(fill="x")
        ctk.CTkLabel(txt, text=h["subtitulo"], font=(FONTS.family, 18), text_color="white", anchor="w").pack(fill="x", pady=(5, 30))

        # Cards
        c_cnt = ctk.CTkFrame(txt, fg_color="transparent")
        c_cnt.pack(fill="x", pady=(0, 60))
        c_cnt.grid_columnconfigure((0, 1, 2), weight=1)
        for i, (t, d, ico) in enumerate(h["pilares"]):
            c = ctk.CTkFrame(c_cnt, fg_color="#1D3830", corner_radius=15, border_width=1, border_color="#2D4F45")
            c.grid(row=0, column=i, padx=5, sticky="nsew")
            ctk.CTkLabel(c, text=ico, font=(FONTS.family, 26)).pack(pady=(15, 5))
            ctk.CTkLabel(c, text=t, font=(FONTS.family, 14, "bold"), text_color=COLORS.accent).pack()
            ctk.CTkLabel(c, text=d, font=(FONTS.family, 11), text_color="white", wraplength=190, justify="center").pack(pady=(10, 25), padx=15)

    def _render_modelos(self):
        m = CONTENIDO_FULL["modelos"]
        cnt = ctk.CTkFrame(self.scroll, fg_color=COLORS.bg_card, corner_radius=0)
        cnt.pack(fill="x", padx=0, pady=(0, 60))
        
        # Estructura Árbol
        ctk.CTkLabel(cnt, text=m["pregunta"], font=(FONTS.family, 16, "bold"), fg_color=COLORS.primary_dark, text_color="white", corner_radius=6, height=50, width=300).pack(pady=(0, 40))
        
        grid = ctk.CTkFrame(cnt, fg_color="transparent")
        grid.pack(fill="x", padx=40)
        grid.grid_columnconfigure((0, 1, 2), weight=1)

        for i, opt in enumerate(m["opciones"]):
            f = ctk.CTkFrame(grid, fg_color="white", corner_radius=15, border_width=1, border_color=COLORS.border)
            f.grid(row=0, column=i, padx=12, sticky="nsew")
            
            # Linea superior colorida
            ctk.CTkFrame(f, fg_color=opt["color"], height=8, corner_radius=15).pack(fill="x", pady=(10, 0), padx=10)
            
            # Badge
            b = ctk.CTkLabel(f, text=opt["cod"], font=(FONTS.family, 13, "bold"), fg_color=opt["color"], text_color="white", corner_radius=6, width=45, height=30)
            b.pack(pady=15, padx=15, anchor="w")
            
            ctk.CTkLabel(f, text=opt["tit"], font=(FONTS.family, 18, "bold"), text_color=COLORS.primary, anchor="w").pack(fill="x", padx=20)
            ctk.CTkLabel(f, text=opt["sub"], font=(FONTS.family, 13, "italic"), text_color=COLORS.text_secondary, anchor="w").pack(fill="x", padx=20, pady=(0, 15))
            ctk.CTkFrame(f, fg_color=COLORS.border, height=1).pack(fill="x", padx=20)
            ctk.CTkLabel(f, text=opt["var"], font=(FONTS.family, 12), text_color=COLORS.text_secondary, anchor="w").pack(fill="x", padx=20, pady=15)
            ctk.CTkLabel(f, text="Ideal cuando:", font=(FONTS.family, 12, "bold"), text_color=COLORS.primary, anchor="w").pack(fill="x", padx=20)
            ctk.CTkLabel(f, text=opt["ideal"], font=(FONTS.family, 12), text_color=opt["color"], anchor="w", justify="left").pack(fill="x", padx=20, pady=(5, 30))

        # Tip
        tip = ctk.CTkFrame(cnt, fg_color="#E8F5E9", corner_radius=10)
        tip.pack(fill="x", padx=50, pady=(40, 0))
        ctk.CTkLabel(tip, text=f"💡 {m['tip']}", font=(FONTS.family, 12), text_color="#2E7D32", wraplength=900).pack(pady=12, padx=25)

    def _render_flujo(self):
        f_data = CONTENIDO_FULL["flujo"]
        cnt = ctk.CTkFrame(self.scroll, fg_color=COLORS.bg_card, corner_radius=0)
        cnt.pack(fill="x", pady=(0, 60))
        
        grid = ctk.CTkFrame(cnt, fg_color="transparent")
        grid.pack(fill="x", padx=60)
        grid.grid_columnconfigure((0, 1), weight=1)

        for i, (num, tit, dsc) in enumerate(f_data["pasos"]):
            r, c = divmod(i, 2)
            card = ctk.CTkFrame(grid, fg_color="white", corner_radius=12, border_width=1, border_color=COLORS.border)
            card.grid(row=r, column=c, padx=15, pady=15, sticky="nsew")
            
            # Indicador lateral
            ctk.CTkFrame(card, fg_color=COLORS.primary_dark, width=6).pack(side="left", fill="y", padx=(15, 0), pady=15)
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(side="left", fill="both", expand=True, padx=20, pady=20)
            
            h = ctk.CTkFrame(inner, fg_color="transparent")
            h.pack(fill="x")
            ctk.CTkLabel(h, text=num, font=(FONTS.family, 14, "bold"), fg_color=COLORS.primary_dark, text_color="white", width=34, height=34, corner_radius=6).pack(side="left")
            ctk.CTkLabel(h, text=tit, font=(FONTS.family, 16, "bold"), text_color=COLORS.primary).pack(side="left", padx=15)
            
            ctk.CTkLabel(inner, text=dsc, font=(FONTS.family, 12), text_color=COLORS.text_secondary, wraplength=400, justify="left", anchor="w").pack(fill="x", pady=(15, 0))

    def _render_excel(self):
        ex = CONTENIDO_FULL["excel"]
        cnt = ctk.CTkFrame(self.scroll, fg_color=COLORS.bg_card, corner_radius=0)
        cnt.pack(fill="x", pady=(0, 60))
        
        grid = ctk.CTkFrame(cnt, fg_color="transparent")
        grid.pack(fill="x", padx=40)
        grid.grid_columnconfigure((0, 1), weight=1)

        # Config Panel
        pane1 = ctk.CTkFrame(grid, fg_color="white", corner_radius=15, border_width=1, border_color=COLORS.border)
        pane1.grid(row=0, column=0, padx=15, sticky="nsew")
        # Header oscuro interno
        h1 = ctk.CTkFrame(pane1, fg_color="#457864", height=40, corner_radius=0)
        h1.pack(fill="x")
        ctk.CTkLabel(h1, text="PASO 1–2: Pantalla de Configuración", font=(FONTS.family, 13, "bold"), text_color="white").pack(side="left", padx=20)
        
        # Tabla Config
        for i, (lab, val) in enumerate(ex["config_tabla"]):
            row = ctk.CTkFrame(pane1, fg_color="transparent" if i%2==0 else "#F9F9F9")
            row.pack(fill="x", padx=10, pady=1)
            ctk.CTkLabel(row, text=lab, font=(FONTS.family, 12, "bold"), text_color=COLORS.primary, width=180, anchor="w").pack(side="left", padx=20, pady=8)
            ctk.CTkLabel(row, text=val, font=(FONTS.family, 11), text_color=COLORS.text_secondary, anchor="w").pack(side="left", fill="x", expand=True)

        ctk.CTkButton(pane1, text="⬇ Confirmar y descargar plantilla M1", fg_color=COLORS.accent, text_color=COLORS.primary, font=(FONTS.family, 12, "bold"), height=40).pack(pady=30, padx=50, fill="x")

        # Excel Panel
        pane2 = ctk.CTkFrame(grid, fg_color="white", corner_radius=15, border_width=1, border_color=COLORS.border)
        pane2.grid(row=0, column=1, padx=15, sticky="nsew")
        h2 = ctk.CTkFrame(pane2, fg_color="#00838F", height=40, corner_radius=0)
        h2.pack(fill="x")
        ctk.CTkLabel(h2, text="📄 Estructura del Excel-Proyecto", font=(FONTS.family, 13, "bold"), text_color="white").pack(side="left", padx=20)

        for hj, dsc, meta, col in ex["hojas"]:
            c = ctk.CTkFrame(pane2, fg_color="transparent")
            c.pack(fill="x", padx=20, pady=15)
            # Badge superior de hoja
            b_f = ctk.CTkFrame(c, fg_color="transparent")
            b_f.pack(fill="x")
            ctk.CTkLabel(b_f, text=hj, font=(FONTS.family, 13, "bold"), text_color=COLORS.primary).pack(side="left")
            ctk.CTkLabel(b_f, text=meta, font=(FONTS.family, 10, "bold"), fg_color=col, text_color="white", corner_radius=6, padx=8).pack(side="right")
            ctk.CTkLabel(c, text=dsc, font=(FONTS.family, 11), text_color=COLORS.text_secondary, wraplength=400, justify="left", anchor="w").pack(fill="x", pady=(5, 0))
            ctk.CTkFrame(pane2, fg_color=COLORS.border, height=1).pack(fill="x", padx=20)

    def _render_pipeline(self):
        p = CONTENIDO_FULL["pipeline"]
        cnt = ctk.CTkFrame(self.scroll, fg_color=COLORS.bg_card, corner_radius=0)
        cnt.pack(fill="x", pady=(0, 60))
        
        # Header Pipeline sutil verde
        h_f = ctk.CTkFrame(cnt, fg_color="#E8F5E9", height=40)
        h_f.pack(fill="x", padx=40, pady=(0, 30))
        ctk.CTkLabel(h_f, text=p["header_pipeline"], font=(FONTS.family, 12, "bold"), text_color="#1B5E20").pack(side="left", padx=20)

        grid = ctk.CTkFrame(cnt, fg_color="transparent")
        grid.pack(fill="x", padx=40)
        grid.grid_columnconfigure(0, weight=3)
        grid.grid_columnconfigure(1, weight=1)

        # Left: Items Pipeline
        left = ctk.CTkFrame(grid, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        for let, tit, dsc in p["items"]:
            c = ctk.CTkFrame(left, fg_color="white", corner_radius=12, border_width=1, border_color=COLORS.border)
            c.pack(fill="x", pady=8)
            ctk.CTkLabel(c, text=let, font=(FONTS.family, 15, "bold"), fg_color="#10251F", text_color="white", width=36, height=36, corner_radius=6).pack(side="left", padx=20, pady=15)
            txt_f = ctk.CTkFrame(c, fg_color="transparent")
            txt_f.pack(side="left", fill="both", expand=True, pady=15)
            ctk.CTkLabel(txt_f, text=tit, font=(FONTS.family, 14, "bold"), text_color=COLORS.primary, anchor="w").pack(fill="x")
            ctk.CTkLabel(txt_f, text=dsc, font=(FONTS.family, 11), text_color=COLORS.text_secondary, wraplength=550, justify="left", anchor="w").pack(fill="x")

        # Right: KPIs y Alertas
        right = ctk.CTkFrame(grid, fg_color="#10251F", corner_radius=15)
        right.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(right, text="INDICADORES DE RESULTADOS", font=(FONTS.family, 11, "bold"), text_color=COLORS.accent).pack(pady=25)
        
        for name, val, unit in p["kpis"]:
            k = ctk.CTkFrame(right, fg_color="#18362E", corner_radius=10, border_width=1, border_color="#2D4F45")
            k.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(k, text=name, font=(FONTS.family, 10), text_color="white").pack(pady=(10, 0))
            ctk.CTkLabel(k, text=val, font=(FONTS.family, 22, "bold"), text_color="white").pack()
            ctk.CTkLabel(k, text=unit, font=(FONTS.family, 9), text_color=COLORS.text_secondary).pack(pady=(0, 10))

        # Alertas Box
        a_f = ctk.CTkFrame(right, fg_color="#441111", corner_radius=8, border_width=1, border_color="#662222")
        a_f.pack(fill="x", padx=20, pady=(30, 25))
        ctk.CTkLabel(a_f, text="⚠️ Validaciones críticas", font=(FONTS.family, 10, "bold"), text_color="#FF8888", anchor="w").pack(fill="x", padx=15, pady=(10, 5))
        for al in p["alertas"]:
            ctk.CTkLabel(a_f, text=f"• {al}", font=(FONTS.family, 10), text_color="#FFCCCC", anchor="w", justify="left").pack(fill="x", padx=15, pady=1)

    def _render_salidas(self):
        s = CONTENIDO_FULL["salidas"]
        cnt = ctk.CTkFrame(self.scroll, fg_color=COLORS.bg_card, corner_radius=0)
        cnt.pack(fill="x", pady=(0, 60))
        
        grid = ctk.CTkFrame(cnt, fg_color="transparent")
        grid.pack(fill="x", padx=40)
        grid.grid_columnconfigure((0, 1), weight=1)

        # Tablas Panel
        p1 = ctk.CTkFrame(grid, fg_color="white", corner_radius=15, border_width=1, border_color=COLORS.border)
        p1.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 30))
        
        for tit, dsc in s["tablas"][:2]:
            row = ctk.CTkFrame(p1, fg_color="transparent")
            row.pack(fill="x", padx=40, pady=25)
            ctk.CTkLabel(row, text="📋", font=(FONTS.family, 24)).pack(side="left")
            t_f = ctk.CTkFrame(row, fg_color="transparent")
            t_f.pack(side="left", padx=25, fill="x", expand=True)
            ctk.CTkLabel(t_f, text=tit, font=(FONTS.family, 15, "bold"), text_color=COLORS.primary, anchor="w").pack(fill="x")
            ctk.CTkLabel(t_f, text=dsc, font=(FONTS.family, 12), text_color=COLORS.text_secondary, anchor="w").pack(fill="x")
            ctk.CTkFrame(p1, fg_color=COLORS.border, height=1).pack(fill="x", padx=60)

        # Monitoreo Panel
        p2 = ctk.CTkFrame(grid, fg_color="#F59E0B", corner_radius=10) # Orange UPME
        p2.grid(row=1, column=0, columnspan=2, sticky="nsew")
        h = ctk.CTkFrame(p2, fg_color="transparent", height=45)
        h.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(h, text=s["tablas"][2][0], font=(FONTS.family, 14, "bold"), text_color=COLORS.primary_dark).pack(side="left")
        
        list_f = ctk.CTkFrame(p2, fg_color="white", corner_radius=0)
        list_f.pack(fill="x", padx=1, pady=(0, 1))
        for pt in s["monitoreo_puntos"]:
            row = ctk.CTkFrame(list_f, fg_color="transparent")
            row.pack(fill="x", padx=40, pady=8)
            ctk.CTkLabel(row, text="•", font=(FONTS.family, 14, "bold"), text_color=COLORS.primary).pack(side="left")
            ctk.CTkLabel(row, text=pt, font=(FONTS.family, 12), text_color=COLORS.text_secondary, anchor="w").pack(side="left", padx=10)

    def _render_glosario(self):
        g = CONTENIDO_FULL["glosario"]
        cnt = ctk.CTkFrame(self.scroll, fg_color=COLORS.bg_card, corner_radius=0)
        cnt.pack(fill="x", pady=(0, 60))
        
        grid = ctk.CTkFrame(cnt, fg_color="transparent")
        grid.pack(fill="x", padx=40)
        grid.grid_columnconfigure((0, 1), weight=1)

        # Glosario Técnico
        p1 = ctk.CTkFrame(grid, fg_color="white", corner_radius=15, border_width=1, border_color=COLORS.border)
        p1.grid(row=0, column=0, padx=15, sticky="nsew")
        # Header oscuro interno EXACTO
        h1 = ctk.CTkFrame(p1, fg_color="#2D4F45", height=45, corner_radius=0)
        h1.pack(fill="x")
        ctk.CTkLabel(h1, text="📖 Glosario Técnico", font=(FONTS.family, 13, "bold"), text_color="white").pack(side="left", padx=20)
        
        for t, d in g["tec"]:
            item = ctk.CTkFrame(p1, fg_color="transparent")
            item.pack(fill="x", padx=25, pady=12)
            ctk.CTkLabel(item, text=t, font=(FONTS.family, 13, "bold"), text_color=COLORS.primary_dark, anchor="w").pack(fill="x")
            ctk.CTkLabel(item, text=d, font=(FONTS.family, 11), text_color=COLORS.text_secondary, wraplength=450, justify="left", anchor="w").pack(fill="x", pady=(2, 0))
            ctk.CTkFrame(p1, fg_color=COLORS.border, height=1).pack(fill="x", padx=25)

        # Interpretación
        p2 = ctk.CTkFrame(grid, fg_color="white", corner_radius=15, border_width=1, border_color=COLORS.border)
        p2.grid(row=0, column=1, padx=15, sticky="nsew")
        h2 = ctk.CTkFrame(p2, fg_color="#457864", height=45, corner_radius=0)
        h2.pack(fill="x")
        ctk.CTkLabel(h2, text="📊 Interpretación de Resultados", font=(FONTS.family, 13, "bold"), text_color="white").pack(side="left", padx=20)

        for tit, sub, dsc, col in g["int"]:
            row = ctk.CTkFrame(p2, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=12)
            # Badge + Texto
            ctk.CTkFrame(row, fg_color=col, width=5).pack(side="left", fill="y", padx=(0, 15), pady=5)
            inf = ctk.CTkFrame(row, fg_color="transparent")
            inf.pack(side="left", fill="both", expand=True)
            head = ctk.CTkFrame(inf, fg_color="transparent")
            head.pack(fill="x")
            ctk.CTkLabel(head, text=tit, font=(FONTS.family, 12, "bold"), fg_color=col if tit!="Reporte UPME" else "transparent", text_color="white" if tit!="Reporte UPME" else COLORS.primary_dark, corner_radius=4, padx=8).pack(side="left")
            ctk.CTkLabel(head, text=sub, font=(FONTS.family, 12, "bold"), text_color=COLORS.primary).pack(side="left", padx=10)
            ctk.CTkLabel(inf, text=dsc, font=(FONTS.family, 11), text_color=COLORS.text_secondary, wraplength=380, justify="left", anchor="w").pack(fill="x", pady=(5, 0))
            ctk.CTkFrame(p2, fg_color=COLORS.border, height=1).pack(fill="x", padx=20)
