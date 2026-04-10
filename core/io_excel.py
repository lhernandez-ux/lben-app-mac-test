"""
core/io_excel.py
================
Lectura y escritura de archivos Excel para LBEn.
Soporta Análisis Exploratorio y Modelo M1 (Consumo Absoluto).
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
_PLANTILLA_M1 = os.path.join(_DIR_DATA, "Plantilla_LBEn_M1_modelo.xlsx")
_PLANTILLA_EXPLORATORIA = os.path.join(_DIR_DATA, "plantilla_exploracion_modelo.xlsx")

# ═══════════════════════════════════════════════════════════════════════════════
# A — GENERACIÓN DE PLANTILLAS
# ═══════════════════════════════════════════════════════════════════════════════

def generar_plantilla_exploratoria(nombre_proyecto, fecha_ini, fecha_fin, var_dep, vars_ind):
    if not os.path.exists(_PLANTILLA_EXPLORATORIA):
        messagebox.showerror("Error", f"No se encontró la plantilla en: {_PLANTILLA_EXPLORATORIA}")
        return False

    nombre_archivo = f"exploracion_{_limpiar_nombre(nombre_proyecto)}.xlsx"
    ruta_destino = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile=nombre_archivo, filetypes=[("Excel", "*.xlsx")])
    if not ruta_destino: return False

    shutil.copy2(_PLANTILLA_EXPLORATORIA, ruta_destino)
    try:
        wb = load_workbook(ruta_destino)
        _escribir_hoja_instrucciones(wb, var_dep, vars_ind, fecha_ini, fecha_fin)
        _escribir_hoja_periodo(wb, fecha_ini, fecha_fin, var_dep, vars_ind)
        wb.save(ruta_destino)
        messagebox.showinfo("Éxito", f"Plantilla generada en:\n{ruta_destino}")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Error al generar: {e}")
        return False

def generar_plantilla_m1(data: dict) -> bool:
    if not os.path.exists(_PLANTILLA_M1):
        messagebox.showerror("Error", f"No se encontró la plantilla M1 en:\n{_PLANTILLA_M1}")
        return False

    nombre_archivo = f"M1_{_limpiar_nombre(data['nombre'])}.xlsx"
    ruta_destino = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile=nombre_archivo, filetypes=[("Excel", "*.xlsx")])
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
    except Exception as e:
        messagebox.showerror("Error", f"Error al generar: {e}")
        return False

# ── Helpers Escritura Inicial ───────────────────────────────────────────────

def _escribir_m1_identificacion(wb, data):
    ws = wb["Modelo_LBEn"]
    ws["D5"] = data["nombre"]
    ws["D6"] = data["fuente"]
    ws["D7"] = data["unidad"]

def _escribir_m1_periodo_base(wb, data):
    ws = wb["Período_Base"]
    fechas = _generar_fechas_mensuales(data["pb_ini"], data["pb_fin"])
    for i, f_str in enumerate(fechas): ws[f"B{8+i}"] = f_str

def _escribir_m1_monitoreo(wb, data):
    ws = wb["Monitoreo"]
    fechas = _generar_fechas_mensuales(data["pr_ini"], data["pr_fin"])
    for i, f_str in enumerate(fechas): ws[f"B{8+i}"] = f_str

def _escribir_hoja_instrucciones(wb, var_dep, vars_ind, fecha_ini, fecha_fin):
    ws = wb["Instrucciones"]
    ws["C11"] = var_dep
    ws["C12"] = ", ".join(vars_ind) if vars_ind else "—"
    ws["C13"] = f"{fecha_ini} — {fecha_fin}"

def _escribir_hoja_periodo(wb, fecha_ini, fecha_fin, var_dep, vars_ind):
    ws = wb["Periodo_Análisis"]
    ws["B6"] = "Fecha"
    ws["C6"] = var_dep
    for i, var in enumerate(vars_ind):
        col = get_column_letter(4 + i)
        ws[f"{col}6"] = var
        _aplicar_estilo_encabezado(ws[f"{col}6"])
    fechas = _generar_fechas_mensuales(fecha_ini, fecha_fin)
    for i, f_str in enumerate(fechas): ws[f"B{8+i}"] = f_str

def _aplicar_estilo_encabezado(celda):
    celda.font = Font(bold=True, color="FFFFFF", size=11)
    celda.fill = PatternFill("solid", start_color="204339")
    celda.alignment = Alignment(horizontal="center", vertical="center")

def _generar_fechas_mensuales(f_ini, f_fin):
    meses_es = {1:"Ene", 2:"Feb", 3:"Mar", 4:"Abr", 5:"May", 6:"Jun", 7:"Jul", 8:"Ago", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dic"}
    try:
        ini = datetime.strptime(f_ini, "%m/%Y")
        fin = datetime.strptime(f_fin, "%m/%Y")
        res = []
        curr = ini
        while curr <= fin:
            res.append(f"{meses_es[curr.month]}-{curr.year}")
            if curr.month == 12: curr = curr.replace(year=curr.year+1, month=1)
            else: curr = curr.replace(month=curr.month+1)
        return res
    except: return []

# ═══════════════════════════════════════════════════════════════════════════════
# B — LECTURA DE DATOS
# ═══════════════════════════════════════════════════════════════════════════════

def leer_excel_exploratorio(path):
    if not os.path.exists(path): return None, {}, ["No encontrado"]
    wb = load_workbook(path, data_only=True)
    if "Periodo_Análisis" not in wb.sheetnames: return None, {}, ["Falta hoja"]
    ws = wb["Periodo_Análisis"]
    
    headers = []
    c = 2
    while True:
        v = ws.cell(row=6, column=c).value
        if not v: break
        headers.append(str(v).strip())
        c += 1
    
    datos = []
    r = 8
    while True:
        fv = ws.cell(row=r, column=2).value
        if not fv: break
        row = {"Fecha": str(fv).strip()}
        for i, h in enumerate(headers[1:]): row[h] = ws.cell(row=r, column=3+i).value
        datos.append(row)
        r += 1
    
    df = pd.DataFrame(datos)
    meta = {"var_dep": headers[1], "vars_ind": headers[2:], "fecha_ini": df["Fecha"].iloc[0], "fecha_fin": df["Fecha"].iloc[-1]}
    return df, meta, []

def leer_excel_m1(path):
    errores = []
    wb = load_workbook(path, data_only=True)
    for s in ["Período_Base", "Monitoreo"]:
        if s not in wb.sheetnames: errores.append(f"Falta hoja {s}")
    if errores: return None, None, {}, errores

    df_b = _leer_hoja_datos_m1(wb["Período_Base"])
    df_m = _leer_hoja_datos_m1(wb["Monitoreo"])
    ws_mod = wb["Modelo_LBEn"] 
    meta = {"entidad": ws_mod["D5"].value, "fuente": ws_mod["D6"].value, "unidad": ws_mod["D7"].value}
    return df_b, df_m, meta, []

def _leer_hoja_datos_m1(ws):
    headers = []
    for c in range(2, 11): # B a J (Usuario llena hasta J)
        v = ws.cell(row=6, column=c).value
        if v: headers.append(str(v).strip())
        else: break
    datos = []
    for r in range(8, ws.max_row + 1):
        f = ws.cell(row=r, column=2).value
        if not f: break
        row = {"Fecha": str(f)}
        for i, h in enumerate(headers[1:]): row[h] = ws.cell(row=r, column=3+i).value
        datos.append(row)
    return pd.DataFrame(datos)

# ═══════════════════════════════════════════════════════════════════════════════
# C — ESCRITURA DE RESULTADOS
# ═══════════════════════════════════════════════════════════════════════════════

def escribir_resultados_exploratorios(path, recomendacion, justificacion, tabla_resultados):
    wb = load_workbook(path)
    ws_inst = wb["Instrucciones"]; ws_model = wb["Modelo_LBEn"]
    ws_inst["C3"] = recomendacion
    ws_model["C5"] = recomendacion; ws_model["C6"] = "UPME 016/2024"; ws_model["C7"] = justificacion
    for ri, row in enumerate(tabla_resultados):
        f = 13 + ri
        vals = [row.get("variable"), row.get("r_pearson"), row.get("p_valor"), "Sí" if row.get("significativa") else "No", row.get("grado"), row.get("interpretacion")]
        for ci, v in enumerate(vals): ws_model.cell(row=f, column=2+ci, value=v)
    wb.save(path)
    return True

def escribir_resultados_m1(path, df_lben, df_mon, df_base_f, df_excluidos, meta, config):
    if not os.path.exists(path): return False
    wb = load_workbook(path)
    fmt_num = "#,##0.00"

    # 1. Hoja Período_Base: Llenar K y L
    if df_base_f is not None:
        ws_base = wb["Período_Base"]
        for i, row in df_base_f.iterrows():
            f = 8 + i
            ws_base[f"K{f}"].value = row.get("Normalizado"); ws_base[f"K{f}"].number_format = fmt_num
            ws_base[f"L{f}"].value = row.get("Ajustado"); ws_base[f"L{f}"].number_format = fmt_num

    # 2. Hoja Modelo_LBEn: Ficha Técnica (K5:M10)
    ws_mod = wb["Modelo_LBEn"]
    ws_mod["D5"] = config.get("nombre"); ws_mod["D6"] = config.get("fuente"); ws_mod["D7"] = config.get("unidad")
    ws_mod["K5"] = "M1 (Consumo Absoluto)"
    ws_mod["K6"] = meta.get("n_inicial"); ws_mod["K7"] = meta.get("n_filt_est"); ws_mod["K8"] = meta.get("n_filt_man"); ws_mod["K9"] = meta.get("n_final")
    ws_mod["K10"].value = meta.get("fiabilidad"); ws_mod["K10"].number_format = "0.0%"
    ws_mod["M5"] = config.get("pb_ini"); ws_mod["M6"] = config.get("pb_fin")
    c_prom = meta.get("consumo_promedio_anual", 0)
    ws_mod["M7"].value = c_prom; ws_mod["M7"].number_format = fmt_num
    ws_mod["M8"].value = meta.get("potencial_ahorro_kwh", 0); ws_mod["M8"].number_format = fmt_num
    ws_mod["M9"].value = meta.get("potencial_ahorro_pct", 0); ws_mod["M9"].number_format = "0.0%"
    ws_mod["M10"].value = meta.get("meta_15", 0); ws_mod["M10"].number_format = fmt_num

    # Tablas Modelo
    for i, row in df_lben.iterrows():
        f = 16 + i
        for col_l, field in zip(["C", "D", "E", "F"], ["lben", "n_usados", "min_hist", "max_hist"]):
            c = ws_mod[f"{col_l}{f}"]
            c.value = row[field]; c.number_format = fmt_num if field != "n_usados" else "0"
        ahorro_v = row['lben'] - row['min_hist']
        ws_mod[f"J{f}"].value = row['lben']; ws_mod[f"J{f}"].number_format = fmt_num
        ws_mod[f"K{f}"].value = row['min_hist']; ws_mod[f"K{f}"].number_format = fmt_num
        ws_mod[f"L{f}"].value = ahorro_v; ws_mod[f"L{f}"].number_format = fmt_num
        if row['lben'] > 0: ws_mod[f"M{f}"].value = ahorro_v / row['lben']; ws_mod[f"M{f}"].number_format = "0.0%"
    
    # Informe de Datos Excluidos (B35:D35)
    if df_excluidos is not None and not df_excluidos.empty:
        for i, row in df_excluidos.iterrows():
            f = 35 + i
            ws_mod[f"B{f}"] = row['Fecha']
            ws_mod[f"D{f}"].value = row['Consumo']; ws_mod[f"D{f}"].number_format = fmt_num

    # 3. Monitoreo Triple Meta
    if df_mon is not None and not df_mon.empty:
        ws_mon = wb["Monitoreo"]
        for i, row in df_mon.iterrows():
            f = 8 + i
            cols_map = {"L": "Normalizado", "M": "Ajustado", "N": "LBEn_Mes", "O": "Desemp_kWh", "P": "Desemp_Pct", "Q": "CUSUM_kWh", "R": "Desemp_COP", "S": "CUSUM_COP", "T": "Desemp_CO2", "U": "CUSUM_CO2"}
            for let, field in cols_map.items():
                c = ws_mon[f"{let}{f}"]
                val = row.get(field, 0)
                if field == "Desemp_Pct": c.value = val/100; c.number_format = "0.0%"
                else: c.value = val; c.number_format = fmt_num

    try:
        wb.save(path)
        return True
    except: return False

def _limpiar_nombre(n):
    import re
    return re.sub(r"[^\w\s-]", "", n.strip().lower()).replace(" ", "_")[:50]