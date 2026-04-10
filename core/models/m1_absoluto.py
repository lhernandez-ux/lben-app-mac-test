"""
core/models/m1_absoluto.py
==========================
Motor de cálculo para el Modelo M1: Consumo Absoluto.
Implementa Normalización, Ajuste NR (Metodología B), Filtrado Estadístico (Res. 016)
y Seguimiento Triple Meta con CUSUM con reinicio anual.
"""

import pandas as pd
import numpy as np
import warnings

def procesar_m1(df_base: pd.DataFrame, df_monitoreo: pd.DataFrame = None):
    """
    Procesa el modelo M1 completo.
    1. Normalización y Ajuste NR del periodo base.
    2. Filtrado estadístico mensual (LBEn).
    3. Evaluación del periodo de monitoreo con CUSUM anual.
    """
    if df_base is None or df_base.empty:
        return None, None, None, None

    # --- 1. PROCESAMIENTO PERIODO BASE ---
    dfb = df_base.copy()
    cols_b = dfb.columns # B:Fecha, C:Cons, D:Dias, E:Tarifa, F:Factor, G:AjusteNR, I:Excluir
    
    dfb['Consumo_Num'] = pd.to_numeric(dfb[cols_b[1]], errors='coerce').fillna(0)
    dfb['Dias_Num'] = pd.to_numeric(dfb[cols_b[2]], errors='coerce').fillna(30)
    dfb['Normalizado'] = (dfb['Consumo_Num'] / dfb['Dias_Num']) * 30
    
    # Parser de fechas robusto para español
    def parse_fecha_es(val):
        if pd.isna(val): return pd.NaT
        val_str = str(val).lower().strip()
        meses_map = {
            'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'ago': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12,
            'set': 9, 'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5,
            'junio': 6, 'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10,
            'noviembre': 11, 'diciembre': 12
        }
        d = pd.to_datetime(val, errors='coerce', dayfirst=True)
        if pd.notna(d): return d
        for m_nom, m_num in meses_map.items():
            if m_nom in val_str:
                try:
                    import re
                    year_match = re.search(r'\d{4}', val_str)
                    anio = int(year_match.group()) if year_match else 2022
                    return pd.Timestamp(year=anio, month=m_num, day=1)
                except: pass
        return pd.NaT

    dfb['Fecha_DT'] = dfb[cols_b[0]].apply(parse_fecha_es)
    dfb['Year'] = dfb['Fecha_DT'].dt.year
    dfb['Month'] = dfb['Fecha_DT'].dt.month
    
    # Ajuste NR Periodo Base (Comparación Anual)
    dfb['Ajuste_NR_Bool'] = dfb[cols_b[5]].astype(str).str.upper() == 'SI'
    dfb['Ajustado'] = dfb['Normalizado'].copy()
    
    for year in dfb['Year'].unique():
        if pd.isna(year): continue
        df_year = dfb[dfb['Year'] == year]
        anomalos = df_year[df_year['Ajuste_NR_Bool']]
        normales = df_year[~df_year['Ajuste_NR_Bool']]
        if not anomalos.empty and not normales.empty:
            prom_norm = normales['Normalizado'].mean()
            prom_anom = anomalos['Normalizado'].mean()
            if prom_anom > 0:
                factor = prom_norm / prom_anom
                dfb.loc[anomalos.index, 'Ajustado'] = dfb.loc[anomalos.index, 'Normalizado'] * factor

    # --- 2. FILTRADO ESTADÍSTICO Y LBEn MENSUAL ---
    resultados_lben = []
    excluidos_lista = []
    
    # Capturar exclusiones manuales (Columna I - índice 7)
    df_man = df_base[df_base[df_base.columns[7]].astype(str).str.upper() == 'SI'].copy()
    for _, row in df_man.iterrows():
        excluidos_lista.append({'Fecha': row[df_base.columns[0]], 'Consumo': row[df_base.columns[1]], 'Motivo': 'Manual'})
    
    # Filtrar solo los NO excluidos manualmente para LBEn
    df_para_lben = dfb[dfb[cols_b[7]].astype(str).str.upper() != 'SI'].copy()
    
    meses_indices = range(1, 13)
    meses_nombres = ["?", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

    for m_idx in meses_indices:
        datos_mes = df_para_lben[df_para_lben['Month'] == m_idx]['Ajustado']
        n_mes = len(datos_mes)
        if n_mes == 0:
            resultados_lben.append({'mes': meses_nombres[m_idx], 'lben':0, 'n_usados':0, 'n_ini':0, 'lim_inf':0, 'lim_sup':0, 'min_hist':0, 'max_hist':0})
            continue
            
        mean_val = datos_mes.mean()
        std_val = datos_mes.std()
        if n_mes < 10:
            f_mask = (datos_mes >= mean_val * 0.9) & (datos_mes <= mean_val * 1.1)
        else:
            f_mask = (datos_mes >= mean_val - 2*std_val) & (datos_mes <= mean_val + 2*std_val)
            
        filtered = datos_mes[f_mask]
        n_final = len(filtered)
        lben_mes = filtered.mean() if n_final > 0 else 0
        
        # Guardar excluidos estadísticos
        outliers = datos_mes[~f_mask]
        for idx in outliers.index:
            excluidos_lista.append({'Fecha': dfb.loc[idx, cols_b[0]], 'Consumo': dfb.loc[idx, 'Consumo_Num'], 'Motivo': 'Estadístico'})

        resultados_lben.append({
            'mes': meses_nombres[m_idx], 'lben': lben_mes, 'n_usados': n_final, 'n_ini': n_mes,
            'lim_inf': lben_mes - (filtered.std()*2 if n_final > 1 else lben_mes*0.1),
            'lim_sup': lben_mes + (filtered.std()*2 if n_final > 1 else lben_mes*0.1),
            'min_hist': filtered.min() if n_final > 0 else 0,
            'max_hist': filtered.max() if n_final > 0 else 0
        })
        
    df_lben = pd.DataFrame(resultados_lben)
    df_excluidos = pd.DataFrame(excluidos_lista)
    
    # --- 3. MONITOREO Y TRIPLE META ---
    res_monitoreo = None
    if df_monitoreo is not None and not df_monitoreo.empty:
        dfm = df_monitoreo.copy()
        cols_m = dfm.columns
        
        dfm['Cons_Num'] = pd.to_numeric(dfm[cols_m[1]], errors='coerce').fillna(0)
        dfm['Dias_Num'] = pd.to_numeric(dfm[cols_m[2]], errors='coerce').fillna(30)
        dfm['Normalizado'] = (dfm['Cons_Num'] / dfm['Dias_Num']) * 30
        
        fechas_m = dfm[cols_m[0]].apply(parse_fecha_es)
        dfm['Year'] = fechas_m.dt.year
        dfm['Month'] = fechas_m.dt.month
        
        # N: LBEn mes
        dict_lben = df_lben.set_index(df_lben.index + 1)['lben'].to_dict()
        dfm['LBEn_Mes'] = dfm['Month'].map(dict_lben).fillna(0)
        
        # M: Ajustado NR (Metodología B)
        dfm['Ajustado'] = dfm['Normalizado'].copy()
        for idx, row in dfm.iterrows():
            m_idx = row['Month']
            if pd.isna(m_idx): continue
            if str(row[cols_m[5]]).upper() == 'SI':
                dfm.at[idx, 'Ajustado'] = dict_lben.get(m_idx, row['Normalizado'])
            # Exclusión Manual (I)
            if str(row[cols_m[7]]).upper() == 'SI':
                dfm.at[idx, 'Ajustado'] = 0
                dfm.at[idx, 'LBEn_Mes'] = 0

        # O, P: Desempeño Energético
        dfm['Desemp_kWh'] = dfm['Ajustado'] - dfm['LBEn_Mes']
        dfm['Desemp_Pct'] = dfm.apply(lambda r: (r['Desemp_kWh'] / r['LBEn_Mes'] * 100) if r['LBEn_Mes'] > 0 else 0, axis=1)
        
        # T, V: Económico y Ambiental
        tarifa = pd.to_numeric(dfm[cols_m[3]], errors='coerce').fillna(0)
        factor = pd.to_numeric(dfm[cols_m[4]], errors='coerce').fillna(0)
        dfm['Desemp_COP'] = dfm['Desemp_kWh'] * tarifa
        dfm['Desemp_CO2'] = dfm['Desemp_kWh'] * factor

        # Q, U, W: CUSUM con Reinicio Anual + R, S: Avances
        meta_data = calcular_resumen_metricas(df_lben, df_base)
        pot_anual = meta_data['potencial_ahorro_kwh']
        meta_15 = meta_data['meta_15']

        dfm['CUSUM_kWh'] = 0.0
        dfm['Avance_Pot'] = 0.0
        dfm['Avance_15'] = 0.0
        dfm['CUSUM_COP'] = 0.0
        dfm['CUSUM_CO2'] = 0.0

        for anio in dfm['Year'].unique():
            if pd.isna(anio): continue
            idx_year = dfm[dfm['Year'] == anio].index
            dfm.loc[idx_year, 'CUSUM_kWh'] = dfm.loc[idx_year, 'Desemp_kWh'].cumsum()
            dfm.loc[idx_year, 'CUSUM_COP'] = dfm.loc[idx_year, 'Desemp_COP'].cumsum()
            dfm.loc[idx_year, 'CUSUM_CO2'] = dfm.loc[idx_year, 'Desemp_CO2'].cumsum()
            
            if pot_anual > 0:
                dfm.loc[idx_year, 'Avance_Pot'] = (dfm.loc[idx_year, 'CUSUM_kWh'] / pot_anual) * -100
            if meta_15 > 0:
                dfm.loc[idx_year, 'Avance_15'] = (dfm.loc[idx_year, 'CUSUM_kWh'] / meta_15) * -100
        
        res_monitoreo = dfm.fillna(0)

    return df_lben, res_monitoreo, dfb, df_excluidos


def calcular_resumen_metricas(df_lben, df_base_raw):
    """Calcula el resumen granular para la Ficha Técnica."""
    consumo_anual = df_lben['lben'].sum()
    ahorro_anual = (df_lben['lben'] - df_lben['min_hist']).sum()
    
    n_inicial = len(df_base_raw)
    n_exch_man = (df_base_raw[df_base_raw.columns[7]].astype(str).str.upper() == 'SI').sum()
    n_final = df_lben['n_usados'].sum()
    
    return {
        "consumo_promedio_anual": consumo_anual,
        "potencial_ahorro_kwh": ahorro_anual,
        "potencial_ahorro_pct": ahorro_anual / consumo_anual if consumo_anual > 0 else 0,
        "n_inicial": n_inicial,
        "n_filt_est": n_inicial - n_final - n_exch_man,
        "n_filt_man": n_exch_man,
        "n_final": n_final,
        "fiabilidad": n_final / n_inicial if n_inicial > 0 else 0,
        "meta_15": consumo_anual * 0.15
    }
