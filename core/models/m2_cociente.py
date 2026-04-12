"""
core/models/m2_cociente.py
==========================
Motor de cálculo para el Modelo M2: Cociente de Valores Medidos.
Implementa Indicador (E/X), Normalización, Filtrado Estadístico y Seguimiento.
"""

import pandas as pd
import numpy as np
import warnings

# Silenciar avisos de futuras versiones
pd.set_option('future.no_silent_downcasting', True)

def procesar_m2(df_base: pd.DataFrame, df_monitoreo: pd.DataFrame = None):
    """
    Procesa el modelo M2 completo (Cocientes).
    """
    if df_base is None or df_base.empty:
        return None, None, None, None

    # --- 1. PROCESAMIENTO PERIODO BASE ---
    dfb = df_base.copy()
    cols_b = dfb.columns 
    # Mapeo M2: 0:Fecha, 1:Cons, 2:VarRel, 3:Dias, 4:Tarifa, 5:Factor, 6:AjusteNR, 8:Excluir
    
    dfb['Consumo_Num'] = pd.to_numeric(dfb[cols_b[1]], errors='coerce').fillna(0)
    dfb['VarRel_Num']  = pd.to_numeric(dfb[cols_b[2]], errors='coerce').fillna(0)
    dfb['Dias_Num']    = pd.to_numeric(dfb[cols_b[3]], errors='coerce').fillna(30)
    
    # 1.1 Normalización Energía a 30 días
    dfb['Normalizado'] = (dfb['Consumo_Num'] / dfb['Dias_Num']) * 30
    
    # Parser de fechas robusto
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
    
    # 1.2 Ajuste NR Periodo Base (Metodología B aplicada a Energía)
    dfb['Ajuste_NR_Bool'] = dfb[cols_b[6]].astype(str).str.upper() == 'SI'
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

    # 1.3 Cálculo del Cociente (Indicador)
    # I = Ajustado / VarRel
    dfb['Cociente'] = dfb.apply(lambda r: (r['Ajustado'] / r['VarRel_Num']) if r['VarRel_Num'] > 0 else 0, axis=1)

    # --- 2. FILTRADO ESTADÍSTICO SOBRE COCIENTES ---
    resultados_lben = []
    excluidos_lista = []
    
    # Exclusiones manuales (Col J - índice 8)
    df_man = df_base[df_base[df_base.columns[8]].astype(str).str.upper() == 'SI'].copy()
    for _, row in df_man.iterrows():
        excluidos_lista.append({'Fecha': row[df_base.columns[0]], 'Consumo': row[df_base.columns[1]], 'Motivo': 'Manual'})
    
    df_para_lben = dfb[dfb[cols_b[8]].astype(str).str.upper() != 'SI'].copy()
    
    meses_indices = range(1, 13)
    meses_nombres = ["?", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

    for m_idx in meses_indices:
        datos_mes = df_para_lben[df_para_lben['Month'] == m_idx]
        vals_cociente = datos_mes['Cociente']
        n_mes = len(vals_cociente)
        
        if n_mes == 0:
            resultados_lben.append({'mes': meses_nombres[m_idx], 'lben':0, 'n_usados':0, 'n_ini':0, 'lim_inf':0, 'lim_sup':0, 'min_hist':0, 'prom_var_rel':0})
            continue
            
        mean_val = vals_cociente.mean()
        std_val  = vals_cociente.std()
        
        if n_mes < 10:
            f_mask = (vals_cociente >= mean_val * 0.9) & (vals_cociente <= mean_val * 1.1)
        else:
            f_mask = (vals_cociente >= mean_val - 2*std_val) & (vals_cociente <= mean_val + 2*std_val)
            
        filtered_rows = datos_mes[f_mask]
        n_final = len(filtered_rows)
        lben_cociente = filtered_rows['Cociente'].mean() if n_final > 0 else 0
        prom_var_mes  = filtered_rows['VarRel_Num'].mean() if n_final > 0 else 0
        
        # Guardar excluidos estadísticos
        outliers = datos_mes[~f_mask]
        for idx in outliers.index:
            excluidos_lista.append({'Fecha': dfb.loc[idx, cols_b[0]], 'Consumo': dfb.loc[idx, 'Consumo_Num'], 'Motivo': 'Estadístico'})

        # Límites estadísticos según Res. 016
        if n_final > 1:
            l_inf = lben_cociente - (filtered_rows['Cociente'].std() * 2) if n_mes >= 10 else lben_cociente * 0.9
            l_sup = lben_cociente + (filtered_rows['Cociente'].std() * 2) if n_mes >= 10 else lben_cociente * 1.1
        else:
            l_inf, l_sup = lben_cociente * 0.9, lben_cociente * 1.1

        resultados_lben.append({
            'mes': meses_nombres[m_idx], 
            'lben': lben_cociente,  # Esto es LBEn(I)
            'n_usados': n_final, 
            'n_ini': n_mes,
            'lim_inf': l_inf, 
            'lim_sup': l_sup,
            'min_hist': filtered_rows['Cociente'].min() if n_final > 0 else 0,
            'prom_var_rel': prom_var_mes # G16:G27
        })
        
    df_lben = pd.DataFrame(resultados_lben)
    df_excluidos = pd.DataFrame(excluidos_lista)
    
    # --- 3. MONITOREO M2 ---
    res_monitoreo = None
    if df_monitoreo is not None and not df_monitoreo.empty:
        dfm = df_monitoreo.copy()
        cols_m = dfm.columns
        # 0:Fecha, 1:Cons, 2:VarRel, 3:Dias, 4:Tarifa, 5:Factor, 6:AjusteNR, 8:Excluir
        
        dfm['Cons_Num']   = pd.to_numeric(dfm[cols_m[1]], errors='coerce')
        dfm['VarRel_Num'] = pd.to_numeric(dfm[cols_m[2]], errors='coerce').fillna(0)
        dfm = dfm[dfm['Cons_Num'].notna()].copy()
        
        if dfm.empty:
            return df_lben, None, dfb, df_excluidos
            
        dfm['Dias_Num'] = pd.to_numeric(dfm[cols_m[3]], errors='coerce').fillna(30)
        dfm['Normalizado'] = (dfm['Cons_Num'] / dfm['Dias_Num']) * 30
        
        fechas_m = dfm[cols_m[0]].apply(parse_fecha_es)
        dfm['Year'] = fechas_m.dt.year
        dfm['Month'] = fechas_m.dt.month
        
        # P: LBEn mes (Indicador base)
        dict_lben = df_lben.set_index(df_lben.index + 1)['lben'].to_dict()
        dfm['LBEn_Ratio'] = dfm['Month'].map(dict_lben).fillna(0)
        
        # N: Ajustado NR y O: Cociente Real
        dfm['Ajustado'] = dfm['Normalizado'].copy()
        for idx, row in dfm.iterrows():
            m_idx = row['Month']
            if pd.isna(m_idx): continue
            if str(row[cols_m[6]]).upper() == 'SI':
                # Si hay Ajuste NR, el consumo ajustado se iguala a la LBEn del mes * VarRel actual
                dfm.at[idx, 'Ajustado'] = dict_lben.get(m_idx, 0) * row['VarRel_Num']
            # Exclusión Manual (J)
            if str(row[cols_m[8]]).upper() == 'SI':
                dfm.at[idx, 'Ajustado'] = 0
                dfm.at[idx, 'LBEn_Ratio'] = 0

        dfm['Cociente_Real'] = dfm.apply(lambda r: (r['Ajustado'] / r['VarRel_Num']) if r['VarRel_Num'] > 0 else 0, axis=1)

        # Q: Desempeño Energético (kWh) -> Q = (Cociente_Real - LBEn_Ratio) * VarRel_Num
        dfm['Desemp_kWh'] = (dfm['Cociente_Real'] - dfm['LBEn_Ratio']) * dfm['VarRel_Num']
        # R: Desempeño %
        dfm['Desemp_Pct'] = dfm.apply(lambda r: (r['Desemp_kWh'] / (r['LBEn_Ratio'] * r['VarRel_Num']) * 100) 
                                      if (r['LBEn_Ratio'] * r['VarRel_Num']) > 0 else 0, axis=1)
        
        # T, V: Económico y Ambiental
        tarifa = pd.to_numeric(dfm[cols_m[4]], errors='coerce').fillna(0)
        factor = pd.to_numeric(dfm[cols_m[5]], errors='coerce').fillna(0)
        dfm['Desemp_COP'] = dfm['Desemp_kWh'] * tarifa
        dfm['Desemp_CO2'] = dfm['Desemp_kWh'] * factor

        # CUSUM con Reinicio Anual
        meta_data = calcular_resumen_metricas_m2(df_lben, df_base)
        pot_anual = meta_data['potencial_ahorro_kwh']
        meta_15   = meta_data['meta_15']

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


def calcular_resumen_metricas_m2(df_lben, df_base_raw):
    """Calcula el resumen granular para M2."""
    # M7 = J28 * Sum(G16:G27) -> Promedio de cocientes * Suma de promedios de variables
    prom_ratio_anual = df_lben['lben'].mean()
    suma_vars_anual  = df_lben['prom_var_rel'].sum()
    consumo_anual    = prom_ratio_anual * suma_vars_anual
    
    # M8 (Ahorro kWh) = Suma( (LBEn(I) - MinHist(I)) * PromVarRel )
    df_lben['ahorro_kwh_mes'] = (df_lben['lben'] - df_lben['min_hist']) * df_lben['prom_var_rel']
    ahorro_anual = df_lben['ahorro_kwh_mes'].sum()
    
    n_inicial = len(df_base_raw)
    n_exch_man = (df_base_raw[df_base_raw.columns[8]].astype(str).str.upper() == 'SI').sum()
    n_final = df_lben['n_usados'].sum()
    
    # Construir tabla de potenciales para la UI
    tabla_potenciales = []
    meses_nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    for i, row in df_lben.iterrows():
        tabla_potenciales.append([
            meses_nombres[i],
            row['lben'],
            row['min_hist'],
            row['lben'] - row['min_hist'],
            row['ahorro_kwh_mes'],
            (row['ahorro_kwh_mes'] / (row['lben'] * row['prom_var_rel']) * 100) if (row['lben'] * row['prom_var_rel']) > 0 else 0
        ])
    
    # Agregar fila de promedio anual
    tabla_potenciales.append([
        "PROMEDIO ANUAL",
        prom_ratio_anual,
        df_lben['min_hist'].mean(),
        prom_ratio_anual - df_lben['min_hist'].mean(),
        ahorro_anual,
        (ahorro_anual / consumo_anual * 100) if consumo_anual > 0 else 0
    ])

    return {
        "consumo_promedio_anual": consumo_anual,
        "potencial_ahorro_kwh": ahorro_anual,
        "potencial_ahorro_pct": (ahorro_anual / consumo_anual * 100) if consumo_anual > 0 else 0,
        "n_inicial": n_inicial,
        "n_filtrado": n_inicial - n_final,
        "n_final": n_final,
        "fiabilidad": (n_final / n_inicial * 100) if n_inicial > 0 else 0,
        "periodo_inicio": str(df_base_raw.iloc[0,0]),
        "periodo_fin": str(df_base_raw.iloc[-1,0]),
        "meta_15": consumo_anual * 0.15,
        "tabla_potenciales": tabla_potenciales
    }
