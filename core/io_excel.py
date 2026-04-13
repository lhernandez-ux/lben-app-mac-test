"""
core/io_excel.py
================
Lectura y escritura de archivos Excel para LBEn.
Soporta Análisis Exploratorio, Modelo M1, M2 y M3.
"""

import os
import shutil
from tkinter import filedialog, messagebox
from datetime import datetime
import pandas as pd
import numpy as np
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

# ── Rutas a plantillas ────────────────────────────────────────────────────────
_DIR_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DIR_DATA = os.path.join(_DIR_BASE, "data")
_PLANTILLA_M1 = os.path.join(_DIR_DATA, "Plantilla_LBEn_M1_modelo.xlsx")
_PLANTILLA_M2 = os.path.join(_DIR_DATA, "Plantilla_LBEn_M2_modelo.xlsx")
_PLANTILLA_M3 = os.path.join(_DIR_DATA, "Plantilla_LBEn_M3_modelo.xlsx")
_PLANTILLA_EXPLORATORIA = os.path.join(_DIR_DATA, "plantilla_exploracion_modelo.xlsx")

# ═══════════════════════════════════════════════════════════════════════════════
# A — GENERACIÓN DE PLANTILLAS
# ═══════════════════════════════════════════════════════════════════════════════

def generar_plantilla_exploratoria(nombre_proyecto, fecha_ini, fecha_fin, var_dep, vars_ind):
    if not os.path.exists(_PLANTILLA_EXPLORATORIA):
        messagebox.showerror("Error", f"No se encontró la plantilla.")
        return False
    nombre_archivo = f"exploracion_{_limpiar_nombre(nombre_proyecto)}.xlsx"
    ruta_destino = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile=nombre_archivo)
    if not ruta_destino: return False
    shutil.copy2(_PLANTILLA_EXPLORATORIA, ruta_destino)
    try:
        wb = load_workbook(ruta_destino)
        _escribir_hoja_periodo(wb, fecha_ini, fecha_fin, var_dep, vars_ind)
        wb.save(ruta_destino)
        messagebox.showinfo("Éxito", "Plantilla generada.")
        return True
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return False

def generar_plantilla_m1(data: dict) -> bool:
    return _generar_plantilla_generic(_PLANTILLA_M1, f"M1_{_limpiar_nombre(data['nombre'])}.xlsx", data, 1)

def generar_plantilla_m2(data: dict) -> bool:
    return _generar_plantilla_generic(_PLANTILLA_M2, f"M2_{_limpiar_nombre(data['nombre'])}.xlsx", data, 2)

def generar_plantilla_m3(data: dict) -> bool:
    return _generar_plantilla_generic(_PLANTILLA_M3, f"M3_{_limpiar_nombre(data['nombre'])}.xlsx", data, 3)

def _generar_plantilla_generic(path_tpl, default_name, data, mod_num):
    if not os.path.exists(path_tpl):
        messagebox.showerror("Error", "No se encontró la plantilla.")
        return False
    ruta_destino = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile=default_name)
    if not ruta_destino: return False
    try:
        shutil.copy2(path_tpl, ruta_destino)
        wb = load_workbook(ruta_destino)
        if mod_num == 1:
            _escribir_m1_identificacion(wb, data)
            _escribir_m1_periodo_base(wb, data)
            _escribir_m1_monitoreo(wb, data)
        elif mod_num == 2:
            _escribir_m2_identificacion(wb, data)
            _escribir_m1_periodo_base(wb, data)
            _escribir_m1_monitoreo(wb, data)
        elif mod_num == 3:
            _escribir_m3_identificacion(wb, data)
            _escribir_m3_hojas_datos(wb, data, "Período_Base")
            _escribir_m3_hojas_datos(wb, data, "Monitoreo")
        wb.save(ruta_destino)
        messagebox.showinfo("Éxito", "Plantilla generada.")
        return True
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return False

# ── Helpers Escritura ───────────────────────────────────────────────────────

def _escribir_m1_identificacion(wb, data):
    ws = wb["Modelo_LBEn"]
    ws["D5"] = data["nombre"]; ws["D6"] = data["fuente"]; ws["D7"] = data["unidad"]; ws["D8"] = data.get("zona"); ws["D9"] = data.get("area")

def _escribir_m1_periodo_base(wb, data):
    ws = wb["Período_Base"]
    fechas = _generar_fechas_mensuales(data["pb_ini"], data["pb_fin"])
    for i, f_str in enumerate(fechas): ws[f"B{8+i}"] = f_str

def _escribir_m2_identificacion(wb, data):
    _escribir_m1_identificacion(wb, data)
    ws = wb["Modelo_LBEn"]
    ws["D10"] = data.get("var_relevante_nom"); ws["D11"] = data.get("var_relevante_uni")

def _escribir_m3_identificacion(wb, data):
    _escribir_m1_identificacion(wb, data)
    ws = wb["Modelo_LBEn"]
    vars_ind = data.get("vars_ind", [])
    for i in range(5):
        # Corregido: C10-C14 combinadas con B, escribir en B
        ws[f"B{10+i}"] = vars_ind[i] if i < len(vars_ind) else "—"

def _escribir_m3_hojas_datos(wb, data, sheet_name):
    ws = wb[sheet_name]
    vars_ind = data.get("vars_ind", [])
    for i in range(5):
        col_let = get_column_letter(5 + i)
        if i < len(vars_ind): ws[f"{col_let}6"].value = vars_ind[i]
        else: ws[f"{col_let}6"].value = "—"; ws.column_dimensions[col_let].hidden = True
    f_ini = data["pb_ini"] if sheet_name == "Período_Base" else data["pr_ini"]
    f_fin = data["pb_fin"] if sheet_name == "Período_Base" else "12/2050"
    fechas = _generar_fechas_mensuales(f_ini, f_fin)
    for i, f_str in enumerate(fechas): ws[f"B{8+i}"] = f_str

def _escribir_m1_monitoreo(wb, data):
    ws = wb["Monitoreo"]
    fechas = _generar_fechas_mensuales(data["pr_ini"], data["pr_fin"])
    for i, f_str in enumerate(fechas): ws[f"B{8+i}"] = f_str

def _escribir_hoja_periodo(wb, f_ini, f_fin, var_dep, vars_ind):
    ws = wb["Periodo_Análisis"]
    ws["C6"] = var_dep
    for i, var in enumerate(vars_ind or []):
        col = get_column_letter(4 + i)
        ws[f"{col}6"] = var
    fechas = _generar_fechas_mensuales(f_ini, f_fin)
    for i, f_str in enumerate(fechas): ws[f"B{8+i}"] = f_str

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

def _limpiar_nombre(n):
    import re
    return re.sub(r"[^\w\s-]", "", n.strip().lower()).replace(" ", "_")[:50]

# ═══════════════════════════════════════════════════════════════════════════════
# B — LECTURA DE DATOS
# ═══════════════════════════════════════════════════════════════════════════════

def leer_excel_exploratorio(path):
    wb = load_workbook(path, data_only=True)
    ws = wb["Periodo_Análisis"]
    headers = []
    c = 2
    while True:
        v = ws.cell(row=6, column=c).value
        if not v: break
        headers.append(str(v).strip()); c += 1
    datos = []
    r = 8
    while True:
        fv = ws.cell(row=r, column=2).value
        if not fv: break
        row = {"Fecha": str(fv)}
        for i, h in enumerate(headers[1:]): row[h] = ws.cell(row=r, column=3+i).value
        datos.append(row); r += 1
    df = pd.DataFrame(datos)
    return df, {"var_dep": headers[1], "vars_ind": headers[2:]}, []

def leer_excel_m1(path):
    wb = load_workbook(path, data_only=True)
    df_b = _leer_hoja_datos_generica(wb["Período_Base"])
    df_m = _leer_hoja_datos_generica(wb["Monitoreo"])
    ws_mod = wb["Modelo_LBEn"]
    meta = {"entidad": ws_mod["D5"].value, "fuente": ws_mod["D6"].value, "unidad": ws_mod["D7"].value}
    return df_b, df_m, meta, []

def leer_excel_m2(path):
    df_b, df_m, meta, err = leer_excel_m1(path)
    wb = load_workbook(path, data_only=True)
    ws_mod = wb["Modelo_LBEn"]
    meta.update({"var_relevante_nom": ws_mod["D10"].value, "var_relevante_uni": ws_mod["D11"].value})
    return df_b, df_m, meta, err

def _leer_hoja_datos_generica(ws):
    headers = ["Fecha"]
    for c in range(3, 15):
        v = ws.cell(row=6, column=c).value
        if v: headers.append(str(v).strip())
        else: break
    datos = []
    for r in range(8, 2000):
        f = ws.cell(row=r, column=2).value
        if not f: break
        row = {"Fecha": str(f)}
        for i, h in enumerate(headers[1:]): row[h] = ws.cell(row=r, column=3+i).value
        datos.append(row)
    return pd.DataFrame(datos)

# ═══════════════════════════════════════════════════════════════════════════════
# C — ESCRITURA DE RESULTADOS
# ═══════════════════════════════════════════════════════════════════════════════

def escribir_resultados_exploratorios(path, rec, just, tabla):
    wb = load_workbook(path)
    ws_mod = wb["Modelo_LBEn"]
    ws_mod["C5"] = rec; ws_mod["C7"] = just
    for i, row in enumerate(tabla):
        f = 13 + i
        ws_mod.cell(row=f, column=2, value=row.get("variable"))
        ws_mod.cell(row=f, column=3, value=row.get("r_pearson"))
        ws_mod.cell(row=f, column=4, value=row.get("p_valor"))
    wb.save(path)
    return True

def escribir_resultados_m1(path, df_lben, df_mon, df_b_f, df_excl, meta, config):
    wb = load_workbook(path)
    fmt = "#,##0.00"
    ws_mod = wb["Modelo_LBEn"]
    ws_mod["K5"] = "M1 (Consumo Absoluto)"
    ws_mod["M7"].value = meta.get("consumo_promedio_anual", 0); ws_mod["M7"].number_format = fmt
    ws_mod["M8"].value = meta.get("potencial_ahorro_kwh", 0); ws_mod["M8"].number_format = fmt
    ws_mod["M9"].value = meta.get("potencial_ahorro_pct", 0)/100; ws_mod["M9"].number_format = "0.0%"
    wb.save(path)
    return True

def escribir_resultados_m2(path, df_lben, df_mon, df_b_f, df_excl, meta, config):
    escribir_resultados_m1(path, df_lben, df_mon, df_b_f, df_excl, meta, config)
    wb = load_workbook(path)
    ws_mod = wb["Modelo_LBEn"]
    ws_mod["K5"] = "M2 (Cociente Normalizado)"
    wb.save(path)
    return True

def escribir_resultados_m3(path, res, config):
    if not os.path.exists(path): return False
    wb = load_workbook(path)
    fmt_num = "#,##0.00"; fmt_pct = "0.0%"
    
    # 1. Hoja Período_Base (Q, R, S)
    ws_base = wb["Período_Base"]
    df_b = res['df_base']
    for i, row in df_b.iterrows():
        f = 8 + i
        ws_base[f"Q{f}"].value = row.get('Consumo', 0) + (row.get('Afectacion') if row.get('Afectacion') else 0)
        ws_base[f"R{f}"].value = row.get('y_pred_lben', 0)
        ws_base[f"S{f}"].value = ws_base[f"Q{f}"].value - ws_base[f"R{f}"].value
        for c in ["Q", "R", "S"]: ws_base[f"{c}{f}"].number_format = fmt_num

    # 2. Hoja Diag_Modelo
    ws_diag = wb["Diag_Modelo"]
    m = res['metrics']
    mappings = {"C7": m['r2'], "C8": m['r2_adj'], "C9": m['rmse'], "C10": m['cv_rmse']/100, "C11": m['f_pval']}
    for cell, val in mappings.items(): 
        ws_diag[cell].value = val
        ws_diag[cell].number_format = fmt_pct if cell == "C10" else fmt_num

    ct = res['coef_table']
    for i in range(len(ct['vars'])):
        f = 15 + i
        ws_diag[f"B{f}"] = ct['vars'][i]
        ws_diag[f"C{f}"] = ct['betas'][i]; ws_diag[f"D{f}"] = ct['std_err'][i]; ws_diag[f"E{f}"] = ct['p_vals'][i]
        if not np.isnan(ct['vif'][i]): ws_diag[f"F{f}"] = ct['vif'][i]
        for c in ["C", "D", "E", "F"]: ws_diag[f"{c}{f}"].number_format = fmt_num
    
    from core.models.m3_regresion import formatear_ecuacion
    ws_diag["B21"] = formatear_ecuacion(res['model_lben'], config['vars_ind'])
    ws_diag["D36"] = m['bp_pval']; ws_diag["D36"].number_format = fmt_num

    # 3. Hoja Modelo_LBEn (AJUSTADO PARA MERGED CELLS B e I)
    ws_mod = wb["Modelo_LBEn"]
    p = res['potenciales']
    ws_mod["I6"] = len(res['df_base']) + len(res['df_excluidos'])
    ws_mod["I7"] = len(res['df_excluidos'])
    ws_mod["I9"] = len(res['df_base'])
    ws_mod["I10"].value = m['r2']; ws_mod["I10"].number_format = fmt_pct
    
    ws_mod["L7"].value = p['prom_real']*12; ws_mod["L8"].value = p['ahorro_kwh']*12
    ws_mod["M9"].value = p['ahorro_pct']/100; ws_mod["M10"].value = (p['prom_real']*12)*0.15
    for c in ["L7", "L8", "M10"]: ws_mod[c].number_format = fmt_num
    ws_mod["M9"].number_format = fmt_pct
    
    ws_mod["D17"] = formatear_ecuacion(res['model_lben'], config['vars_ind'])
    ws_mod["D18"] = formatear_ecuacion(res['model_lmen'], config['vars_ind'])
    ws_mod["D19"] = p['prom_real']; ws_mod["D20"] = p['prom_lben']; ws_mod["D22"] = p['ahorro_kwh']
    
    try:
        wb.save(path)
        return True
    except: return False
