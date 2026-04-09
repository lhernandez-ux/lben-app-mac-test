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
_PLANTILLA_M1 = os.path.join(
    _DIR_DATA, "Plantilla_LBEn_M1_modelo.xlsx"
)

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
    try:
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
    except PermissionError:
        messagebox.showerror("Error de acceso", 
                             f"No se pudo guardar la plantilla en:\n{ruta_destino}\n\n"
                             "El archivo ya existe y está abierto. Ciérralo e intenta de nuevo.")
        return False
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado al generar la plantilla: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# B — GENERACIÓN DE PLANTILLA M1 (CONSUMO ABSOLUTO)
# ═══════════════════════════════════════════════════════════════════════════════

def generar_plantilla_m1(data: dict) -> bool:
    """
    Personaliza y guarda la plantilla para el Modelo M1.
    data: {nombre, fuente, unidad, pb_ini, pb_fin, pr_ini, pr_fin}
    """
    if not os.path.exists(_PLANTILLA_M1):
        messagebox.showerror("Error", f"No se encontró la plantilla M1 en:\n{_PLANTILLA_M1}")
        return False

    nombre_archivo = f"M1_{_limpiar_nombre(data['nombre'])}.xlsx"
    ruta_destino = filedialog.asksaveasfilename(
        title="Guardar plantilla M1",
        initialfile=nombre_archivo,
        defaultextension=".xlsx",
        filetypes=[("Excel", "*.xlsx")]
    )
    if not ruta_destino: return False

    try:
        shutil.copy2(_PLANTILLA_M1, ruta_destino)
        wb = load_workbook(ruta_destino)
        
        _escribir_m1_identificacion(wb, data)
        _escribir_m1_periodo_base(wb, data)
        _escribir_m1_monitoreo(wb, data)
        
        wb.save(ruta_destino)
        messagebox.showinfo("Éxito", f"Plantilla M1 generada en:\n{ruta_destino}")
        return True
    except PermissionError:
        messagebox.showerror("Error de acceso", 
                             f"No se puede crear el archivo:\n{ruta_destino}\n\n"
                             "¿El archivo ya existe y está abierto en Excel? Ciérralo e intenta de nuevo.")
        return False
    except Exception as e:
        messagebox.showerror("Error", f"Error al generar plantilla M1: {e}")
        return False

def _escribir_m1_identificacion(wb, data):
    """Escribe nombre, fuente y unidad en la hoja Modelo_LBEn."""
    ws = wb["Modelo_LBEn"]
    # Según usuario: D5, D6, D7
    ws["D5"] = data["nombre"]
    ws["D6"] = data["fuente"]
    ws["D7"] = data["unidad"]

def _escribir_m1_periodo_base(wb, data):
    ws = wb["Período_Base"]
    # B8 en adelante para fechas
    fechas = _generar_fechas_mensuales(data["pb_ini"], data["pb_fin"])
    for i, f_str in enumerate(fechas):
        ws[f"B{8+i}"] = f_str

def _escribir_m1_monitoreo(wb, data):
    ws = wb["Monitoreo"]
    # B8 en adelante para fechas
    fechas = _generar_fechas_mensuales(data["pr_ini"], data["pr_fin"])
    for i, f_str in enumerate(fechas):
        ws[f"B{8+i}"] = f_str


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
# C — LECTURA DEL EXCEL M1 (CONSUMO ABSOLUTO)
# ═══════════════════════════════════════════════════════════════════════════════

def leer_excel_m1(path: str) -> tuple[pd.DataFrame, pd.DataFrame, dict, list]:
    """
    Lee las hojas Periodo_Base y Monitoreo del Excel M1.
    Retorna (df_base, df_monitoreo, meta, errores).
    """
    errores = []
    if not os.path.exists(path):
        return None, None, {}, [f"Archivo no encontrado: {path}"]

    wb = load_workbook(path, data_only=True)
    
    # Validar hojas
    for s in ["Período_Base", "Monitoreo"]:
        if s not in wb.sheetnames:
            errores.append(f"Falta la hoja obligatoria: {s}")
    
    if errores: return None, None, {}, errores

    # Leer Período_Base
    df_base = _leer_hoja_datos_m1(wb["Período_Base"])
    # Leer Monitoreo
    df_monitoreo = _leer_hoja_datos_m1(wb["Monitoreo"])

    # Metadatos desde Instrucciones
    ws_inst = wb["Instrucciones"]
    meta = {
        "entidad": ws_inst["C12"].value,
        "fuente": ws_inst["C13"].value,
        "unidad": ws_inst["C14"].value,
        "periodo_base_text": ws_inst["C15"].value
    }

    return df_base, df_monitoreo, meta, errores

def _leer_hoja_datos_m1(ws):
    """Auxiliar para leer la estructura de B6:K en M1"""
    # 1. Detectar encabezados en fila 6
    headers = []
    for col in range(2, 13): # B a L
        val = ws.cell(row=6, column=col).value
        if val: headers.append(str(val).strip())
        else: break
    
    # 2. Leer datos desde fila 8
    datos = []
    for r in range(8, ws.max_row + 1):
        fecha = ws.cell(row=r, column=2).value # Col B
        if not fecha: break
        
        row_dict = {"Fecha": str(fecha)}
        for i, h in enumerate(headers[1:]): # Resto de columnas
            row_dict[h] = ws.cell(row=r, column=3 + i).value
        datos.append(row_dict)
    
    return pd.DataFrame(datos)


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

    try:
        wb.save(path)
        return True
    except PermissionError:
        messagebox.showerror("Archivo en uso",
                             f"No se pudo actualizar el archivo:\n{path}\n\n"
                             "Por favor, cierra el Excel y vuelve a intentarlo.")
        return False
    except Exception as e:
        messagebox.showerror("Error al guardar", f"No se pudo guardar el archivo: {e}")
        return False


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


# ═══════════════════════════════════════════════════════════════════════════════
# D — ESCRITURA DE RESULTADOS M1 (CONSUMO ABSOLUTO)
# ═══════════════════════════════════════════════════════════════════════════════

def escribir_resultados_m1(path: str, df_lben: pd.DataFrame, df_mon: pd.DataFrame, meta: dict) -> bool:
    """
    Escribe resultados de cálculo en la hoja Modelo_LBEn y Monitoreo del Excel M1.
    """
    if not os.path.exists(path): return False
    wb = load_workbook(path)
    
    # 1. Hoja Modelo_LBEn: Identificación y Métricas
    ws_mod = wb["Modelo_LBEn"]
    ws_mod["D5"] = meta.get("entidad", "—")
    ws_mod["D6"] = meta.get("fuente", "—")
    ws_mod["D7"] = meta.get("unidad", "—")
    
    # Métricas (Basado en inspección previa)
    ws_mod["K5"] = meta.get("periodo_base_text", "—").split("-")[0].strip() # Inicio
    ws_mod["K6"] = meta.get("periodo_base_text", "—").split("-")[-1].strip() # Fin
    ws_mod["K7"] = df_lben['lben'].sum() # Consumo promedio anual
    
    # 2. Hoja Modelo_LBEn: Tabla LBEn Mensual (Desde B16)
    for i, row in df_lben.iterrows():
        fila = 16 + i
        ws_mod[f"C{fila}"] = row['lben']
        ws_mod[f"D{fila}"] = row['n_usados']
        ws_mod[f"E{fila}"] = row['lim_inf']
        ws_mod[f"F{fila}"] = row['lim_sup']

    # 3. Hoja Monitoreo: Columnas Azules (Desde Col L en adelante)
    if df_mon is not None and not df_mon.empty:
        ws_mon = wb["Monitoreo"]
        for i, row in df_mon.iterrows():
            fila = 8 + i
            # L: Normalizado, M: Normalizado y Ajustado (M1 asume iguales salvo ajuste NR)
            ws_mon[f"L{fila}"] = row.get("Normalizado", 0)
            ws_mon[f"M{fila}"] = row.get("Normalizado", 0) # Simplificado M1
            ws_mon[f"N{fila}"] = row.get("LBEn_Mes", 0)
            ws_mon[f"O{fila}"] = row.get("Ahorro_kWh", 0)
            ws_mon[f"P{fila}"] = row.get("Ahorro_Pct", 0) / 100 # Para formato %

    try:
        wb.save(path)
        return True
    except PermissionError:
        messagebox.showerror("Archivo en uso",
                             f"No se pueden guardar los resultados en:\n{path}\n\n"
                             "El archivo está abierto en Excel. Ciérralo y vuelve a intentarlo.")
        return False
    except Exception as e:
        messagebox.showerror("Error grave", f"Ocurrió un error al guardar los resultados M1: {e}")
        return False