"""
core/io_excel.py
================
Lectura y escritura de archivos Excel.
Ruta 1 — Análisis Exploratorio.
"""

import os
import shutil
from tkinter import filedialog, messagebox
from datetime import datetime, date
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side
)
from openpyxl.utils import get_column_letter


# ── Ruta a la plantilla base ──────────────────────────────────────────────────
_DIR_DATA = os.path.join(os.path.dirname(__file__), "..", "data")
_PLANTILLA_EXPLORATORIA = os.path.join(
    _DIR_DATA, "plantilla_exploracion_modelo.xlsx"
)


# ═══════════════════════════════════════════════════════════════════════════════
# A — GENERACIÓN DE PLANTILLA EXPLORATORIA
# ═══════════════════════════════════════════════════════════════════════════════

def generar_plantilla_exploratoria(
    nombre_proyecto: str,
    fecha_ini: str,
    fecha_fin: str,
    var_dep: str,
    vars_ind: list[str]
) -> bool:
    """
    Toma la plantilla base, la personaliza con los parámetros del proyecto
    y abre el diálogo para que el usuario elija dónde guardarla.

    Retorna True si se guardó correctamente, False si el usuario canceló.
    """
    if not os.path.exists(_PLANTILLA_EXPLORATORIA):
        messagebox.showerror(
            "Plantilla no encontrada",
            f"No se encontró la plantilla base en:\n{_PLANTILLA_EXPLORATORIA}"
        )
        return False

    # Diálogo para guardar
    nombre_archivo = f"exploracion_{_limpiar_nombre(nombre_proyecto)}.xlsx"
    ruta_destino = filedialog.asksaveasfilename(
        title="Guardar plantilla de exploración",
        initialfile=nombre_archivo,
        defaultextension=".xlsx",
        filetypes=[("Excel", "*.xlsx")]
    )
    if not ruta_destino:
        return False

    # Copiar plantilla base
    shutil.copy2(_PLANTILLA_EXPLORATORIA, ruta_destino)

    # Personalizar
    wb = load_workbook(ruta_destino)
    _escribir_hoja_instrucciones(wb, var_dep, vars_ind, fecha_ini, fecha_fin)
    _escribir_hoja_periodo(wb, fecha_ini, fecha_fin, var_dep, vars_ind)
    wb.save(ruta_destino)

    messagebox.showinfo(
        "Plantilla generada",
        f"Plantilla guardada exitosamente en:\n{ruta_destino}\n\n"
        "Llena la hoja 'Periodo_Análisis' con tus datos y luego cárgala en la app."
    )
    return True


def _escribir_hoja_instrucciones(wb, var_dep, vars_ind, fecha_ini, fecha_fin):
    """Escribe metadatos en la hoja Instrucciones."""
    ws = wb["Instrucciones"]

    # C11: variable dependiente
    ws["C11"] = var_dep

    # C12: variables independientes
    ws["C12"] = ", ".join(vars_ind) if vars_ind else "—"

    # C13: rango de fechas
    ws["C13"] = f"{fecha_ini} — {fecha_fin}"

    # C3: recomendación (vacía hasta que se analice, placeholder)
    ws["C3"] = "Pendiente de análisis"


def _escribir_hoja_periodo(wb, fecha_ini, fecha_fin, var_dep, vars_ind):
    """
    Escribe encabezados y fechas en la hoja Periodo_Analisis.
    - Fila 6: encabezados (Fecha en B, var_dep en C, vars_ind en D, E, F...)
    - Fila 7: hints
    - Desde B8: fechas mensuales en formato Mmm-AAAA
    """
    ws = wb["Periodo_Análisis"]

    # ── Encabezados fila 6 ────────────────────────────────────────────────────
    ws["B6"] = "Fecha"
    ws["C6"] = var_dep

    for i, var in enumerate(vars_ind):
        col = get_column_letter(4 + i)   # D=4, E=5, F=6...
        ws[f"{col}6"] = var
        # Extender formato si hay más de 5 variables
        _aplicar_estilo_encabezado(ws[f"{col}6"])

    # ── Hints fila 7 ─────────────────────────────────────────────────────────
    ws["B7"] = "(automático)"
    ws["C7"] = "Consumo Facturado en kWh"
    for i in range(len(vars_ind)):
        col = get_column_letter(4 + i)
        ws[f"{col}7"] = "Numérico"

    # ── Fechas desde B8 ───────────────────────────────────────────────────────
    fechas = _generar_fechas_mensuales(fecha_ini, fecha_fin)
    for fila_idx, fecha_str in enumerate(fechas):
        fila_excel = 8 + fila_idx
        ws[f"B{fila_excel}"] = fecha_str

        # Formato numérico con separador de miles para columnas de datos
        for i in range(len(vars_ind) + 1):   # +1 por var_dep
            col = get_column_letter(3 + i)
            celda = ws[f"{col}{fila_excel}"]
            celda.number_format = "#,##0.00"


def _aplicar_estilo_encabezado(celda):
    """Aplica estilo verde oscuro a celdas de encabezado."""
    celda.font = Font(bold=True, color="FFFFFF", name="Arial", size=11)
    celda.fill = PatternFill("solid", start_color="204339")
    celda.alignment = Alignment(horizontal="center", vertical="center")


def _generar_fechas_mensuales(fecha_ini: str, fecha_fin: str) -> list[str]:
    """
    Genera lista de fechas mensuales entre fecha_ini y fecha_fin.
    Formato entrada: MM/AAAA  →  Formato salida: Ene-2022
    """
    meses_es = {
        1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
        5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
    }

    try:
        ini = datetime.strptime(fecha_ini, "%m/%Y")
        fin = datetime.strptime(fecha_fin, "%m/%Y")
    except ValueError:
        return []

    fechas = []
    actual = ini
    while actual <= fin:
        fechas.append(f"{meses_es[actual.month]}-{actual.year}")
        # Avanzar un mes
        if actual.month == 12:
            actual = actual.replace(year=actual.year + 1, month=1)
        else:
            actual = actual.replace(month=actual.month + 1)

    return fechas


# ═══════════════════════════════════════════════════════════════════════════════
# B — LECTURA DEL EXCEL EXPLORATORIO
# ═══════════════════════════════════════════════════════════════════════════════

def leer_excel_exploratorio(path: str) -> tuple[pd.DataFrame, dict, list]:
    """
    Lee la hoja Periodo_Analisis del Excel exploratorio.

    Retorna:
        df       : DataFrame con los datos (fecha + consumo + variables)
        meta     : dict con var_dep, vars_ind, fecha_ini, fecha_fin
        errores  : lista de strings con errores encontrados
    """
    errores = []

    if not os.path.exists(path):
        return None, {}, [f"Archivo no encontrado: {path}"]

    # Verificar hoja obligatoria
    wb = load_workbook(path, data_only=True)
    if "Periodo_Análisis" not in wb.sheetnames:
        return None, {}, ["El archivo no contiene la hoja 'Periodo_Análisis'."]

    ws = wb["Periodo_Análisis"]

    # ── Leer encabezados desde fila 6 ────────────────────────────────────────
    encabezados = []
    col = 2   # columna B
    while True:
        val = ws.cell(row=6, column=col).value
        if val is None:
            break
        encabezados.append(str(val).strip())
        col += 1

    if len(encabezados) < 2:
        return None, {}, [
            "No se encontraron suficientes columnas en la fila 6. "
            "Se requiere al menos: Fecha y una columna de consumo."
        ]

    col_fecha = encabezados[0]       # "Fecha"
    var_dep   = encabezados[1]       # consumo
    vars_ind  = encabezados[2:]      # variables independientes

    # ── Leer datos desde fila 8 ───────────────────────────────────────────────
    datos = []
    fila  = 8
    while True:
        fecha_val = ws.cell(row=fila, column=2).value
        if fecha_val is None:
            break

        fila_datos = {"Fecha": str(fecha_val).strip()}
        for i, col_nombre in enumerate(encabezados[1:]):
            val = ws.cell(row=fila, column=3 + i).value
            fila_datos[col_nombre] = val
        datos.append(fila_datos)
        fila += 1

    if not datos:
        return None, {}, ["No se encontraron datos desde la fila 8."]

    df = pd.DataFrame(datos)

    # ── Validaciones básicas ──────────────────────────────────────────────────
    for col_nombre in [var_dep] + vars_ind:
        if col_nombre in df.columns:
            df[col_nombre] = pd.to_numeric(df[col_nombre], errors="coerce")
            nulos = df[col_nombre].isna().sum()
            if nulos > 0:
                errores.append(
                    f"Columna '{col_nombre}': {nulos} valores no numéricos o vacíos."
                )

    if len(df) < 3:
        errores.append(
            f"Solo se encontraron {len(df)} registros. "
            "El mínimo técnico es 3. Se recomiendan 12 o más."
        )

    # ── Metadatos ─────────────────────────────────────────────────────────────
    meta = {
        "var_dep":   var_dep,
        "vars_ind":  vars_ind,
        "n_datos":   len(df),
        "fecha_ini": df["Fecha"].iloc[0]  if len(df) > 0 else "",
        "fecha_fin": df["Fecha"].iloc[-1] if len(df) > 0 else "",
    }

    return df, meta, errores


# ═══════════════════════════════════════════════════════════════════════════════
# C — ESCRITURA DE RESULTADOS EXPLORATORIOS AL EXCEL
# ═══════════════════════════════════════════════════════════════════════════════

def escribir_resultados_exploratorios(
    path: str,
    recomendacion: str,
    justificacion: str,
    tabla_resultados: list[dict],
) -> bool:
    """
    Escribe los resultados del análisis en la hoja Modelo_LBEn.

    tabla_resultados: lista de dicts con keys:
        variable, r_pearson, p_valor, significativa, grado, interpretacion
    """
    if not os.path.exists(path):
        messagebox.showerror("Error", f"No se encontró el archivo:\n{path}")
        return False

    wb = load_workbook(path)

    if "Modelo_LBEn" not in wb.sheetnames:
        messagebox.showerror(
            "Error",
            "El archivo no contiene la hoja 'Modelo_LBEn'."
        )
        return False

    ws_inst  = wb["Instrucciones"]
    ws_model = wb["Modelo_LBEn"]

    # ── Hoja Instrucciones: C3 ────────────────────────────────────────────────
    ws_inst["C3"] = recomendacion

    # ── Hoja Modelo_LBEn: C5, C6, C7 (celdas ancla de rangos combinados) ────
    ws_model["C5"] = recomendacion
    ws_model["C6"] = "p-valor < 0.05 (α=0.05, bilateral) | Resolución UPME 016/2024"
    ws_model["C7"] = justificacion

    # ── Tabla desde B12 ───────────────────────────────────────────────────────
    encabezados_tabla = [
        "Variable Independiente", "Coeficiente r (Pearson)",
        "p-valor (bilateral)", "¿Significativa? (α=0.05)",
        "Grado de Influencia", "Interpretación"
    ]

    # Encabezado fila 12
    for ci, txt in enumerate(encabezados_tabla):
        celda = ws_model.cell(row=12, column=2 + ci, value=txt)
        celda.font      = Font(bold=True, color="FFFFFF",
                               name="Arial", size=10)
        celda.fill      = PatternFill("solid", start_color="204339")
        celda.alignment = Alignment(horizontal="center",
                                    vertical="center", wrap_text=True)

    # Filas de datos desde fila 13
    for ri, row in enumerate(tabla_resultados):
        fila_excel = 13 + ri
        valores = [
            row.get("variable", ""),
            row.get("r_pearson", ""),
            row.get("p_valor", ""),
            "Sí" if row.get("significativa") else "No",
            row.get("grado", ""),
            row.get("interpretacion", ""),
        ]
        bg = "F2F2F2" if ri % 2 == 0 else "FFFFFF"
        for ci, val in enumerate(valores):
            celda = ws_model.cell(row=fila_excel, column=2 + ci, value=val)
            celda.fill      = PatternFill("solid", start_color=bg)
            celda.alignment = Alignment(horizontal="center",
                                        vertical="center", wrap_text=True)
            celda.font      = Font(name="Arial", size=10)

            # Colorear columna significativa
            if ci == 3:
                celda.font = Font(
                    name="Arial", size=10, bold=True,
                    color="2D6A4F" if row.get("significativa") else "E63946"
                )

    wb.save(path)
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# D — UTILIDADES
# ═══════════════════════════════════════════════════════════════════════════════

def _limpiar_nombre(nombre: str) -> str:
    """Limpia el nombre del proyecto para usarlo como nombre de archivo."""
    import re
    nombre = nombre.strip().lower()
    nombre = re.sub(r"[^\w\s-]", "", nombre)
    nombre = re.sub(r"[\s]+", "_", nombre)
    return nombre[:50]