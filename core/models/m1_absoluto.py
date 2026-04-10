"""
core/models/m1_absoluto.py
==========================
Lógica de cálculo para el Modelo M1 de Consumo Absoluto.
Sigue los lineamientos de la Resolución UPME 016/2024.
"""

import pandas as pd
import numpy as np
import warnings

def procesar_m1(df_base: pd.DataFrame, df_monitoreo: pd.DataFrame = None):
    """
    Motor principal del Modelo M1 (Consumo Absoluto).
    Implementa Ajuste NR y Filtrado según Res. 016.
    """
    # 1. Preparación y Normalización PB
    dfb = df_base.copy()
    
    # Identificar columnas (B=Fecha, C=Consumo, D=Dias, G=Ajuste NR)
    # Suponemos orden: Fecha(0), Consumo(1), Dias(2), ..., AjusteNR(5)
    cols = dfb.columns
    dfb['Consumo_Num'] = pd.to_numeric(dfb[cols[1]], errors='coerce')
    dfb['Dias_Num'] = pd.to_numeric(dfb[cols[2]], errors='coerce')
    
    # Normalización base 30 días (LA LÍNEA QUE FALTABA)
    dfb['Normalizado'] = (dfb['Consumo_Num'] / dfb['Dias_Num']) * 30
    # Tratamiento de Ajuste NR (Columna G - índice 5)
    dfb['Ajuste_NR'] = dfb[dfb.columns[5]].astype(str).str.upper() == 'SI'
    
    # Manejo de fechas robusto para español
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
        # Intentar parseo estándar primero
        d = pd.to_datetime(val, errors='coerce', dayfirst=True)
        if pd.notna(d): return d
        # Si falla, intentar buscar mes en texto
        for m_nom, m_num in meses_map.items():
            if m_nom in val_str:
                try: # Buscar un año de 4 dígitos
                    import re
                    year_match = re.search(r'\d{4}', val_str)
                    anio = int(year_match.group()) if year_match else 2022
                    return pd.Timestamp(year=anio, month=m_num, day=1)
                except: pass
        return pd.NaT

    dfb['Fecha_DT'] = dfb[dfb.columns[0]].apply(parse_fecha_es)
    dfb['Year'] = dfb['Fecha_DT'].dt.year
    dfb['Month'] = dfb['Fecha_DT'].dt.month
    
    # NUEVO: Filtrado de Exclusión Manual (Columna I - índice 7)
    # Si el usuario pone 'SI', el dato muere para el cálculo
    dfb['Excluir'] = dfb[dfb.columns[7]].astype(str).str.upper() == 'SI'
    dfb = dfb[~dfb['Excluir']].copy()
    
    dfb['Ajustado'] = dfb['Normalizado'] # Default
    
    for anio in dfb['Year'].unique():
        if pd.isna(anio): continue
        # Filtrar solo el año actual para evitar el UserWarning de reindexación
        data_year = dfb[dfb['Year'] == anio].copy()
        
        # Filtros locales al slice del año
        is_normal = ~data_year['Ajuste_NR']
        is_anom   = data_year['Ajuste_NR']
        
        norm_months = data_year.loc[is_normal, 'Normalizado']
        anom_months = data_year.loc[is_anom, 'Normalizado']
        
        if not norm_months.empty and not anom_months.empty:
            prom_norm = norm_months.mean()
            prom_anom = anom_months.mean()
            prop_ajuste = (prom_norm - prom_anom) / prom_norm if prom_norm != 0 else 0
            
            # Aplicar ajuste solo a los anómalos de ESTE año
            dfb.loc[data_year[is_anom].index, 'Ajustado'] = data_year.loc[is_anom, 'Normalizado'] * (1 + prop_ajuste)

    # 2. Filtrado Estadístico por Mes (Lógica Res. 016)
    resultados_lben = []
    meses_indices = range(1, 13)
    meses_nombres = ["?", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                     "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

    total_datos_iniciales = len(dfb.dropna(subset=['Ajustado']))
    
    for m_idx in meses_indices:
        datos_mes = dfb[dfb['Month'] == m_idx]['Ajustado'].dropna()
        n_mes = len(datos_mes)
        
        if n_mes == 0:
            resultados_lben.append({
                'mes': meses_nombres[m_idx], 'lben': 0, 'n_usados': 0, 'n_ini': 0,
                'lim_inf': 0, 'lim_sup': 0, 'min_hist': 0
            })
            continue
            
        mean_val = datos_mes.mean()
        std_val = datos_mes.std()
        
        # Filtro Res. 016
        if n_mes < 10:
            # +/- 10%
            f_mask = (datos_mes >= mean_val * 0.9) & (datos_mes <= mean_val * 1.1)
        else:
            # +/- 2 SD
            f_mask = (datos_mes >= mean_val - 2*std_val) & (datos_mes <= mean_val + 2*std_val)
            
        filtered = datos_mes[f_mask]
        n_final = len(filtered)
        lben_mes = filtered.mean() if n_final > 0 else mean_val
        
        resultados_lben.append({
            'mes': meses_nombres[m_idx],
            'lben': lben_mes,
            'n_usados': n_final,
            'n_ini': n_mes,
            'lim_inf': lben_mes - (filtered.std() * 2 if n_final > 1 else (lben_mes * 0.1)),
            'lim_sup': lben_mes + (filtered.std() * 2 if n_final > 1 else (lben_mes * 0.1)),
            'min_hist': filtered.min() if n_final > 0 else 0,
            'max_hist': filtered.max() if n_final > 0 else 0
        })
        
    df_lben = pd.DataFrame(resultados_lben)
    
    # 3. Monitoreo
    res_monitoreo = None
    if df_monitoreo is not None and not df_monitoreo.empty:
        dfm = df_monitoreo.copy()
        cols_m = dfm.columns
        dfm['Normalizado'] = (pd.to_numeric(dfm[cols_m[1]], errors='coerce') / 
                              pd.to_numeric(dfm[cols_m[2]], errors='coerce')) * 30
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            m_fechas = pd.to_datetime(dfm[cols_m[0]], errors='coerce', dayfirst=True)
        dfm['Month'] = m_fechas.dt.month
        
        # Merge con LBEn por mes
        lben_dict = df_lben.set_index(df_lben.index + 1)['lben'].to_dict()
        dfm['LBEn_Mes'] = dfm['Month'].map(lben_dict)
        
        # Ajuste NR en Monitoreo (CONTRA EL PROMEDIO DEL PERIODO BASE)
        dfm['Ajuste_NR'] = dfm[dfm.columns[5]].astype(str).str.upper() == 'SI'
        dfm['Ajustado'] = dfm['Normalizado']
        
        prom_lben_global = df_lben['lben'].mean()
        if prom_lben_global > 0:
            # Si hay NR en monitoreo, lo llevamos a la media de la LB con la misma prop
            for idx in dfm[dfm['Ajuste_NR']].index:
                val_m = dfm.loc[idx, 'Normalizado']
                # pr = (LB_prom - Val_Anom) / LB_prom
                pr = (prom_lben_global - val_m) / prom_lben_global
                dfm.loc[idx, 'Ajustado'] = val_m * (1 + pr)

        # --- DESEMPEÑO E INNOVACIÓN (TRIPLE META) ---
        # 1. Energético
        dfm['Desemp_kWh'] = dfm['Ajustado'] - dfm['LBEn_Mes']
        dfm['Desemp_Pct'] = (dfm['Desemp_kWh'] / dfm['LBEn_Mes'] * 100) if not dfm['LBEn_Mes'].empty else 0
        dfm['CUSUM_kWh']  = dfm['Desemp_kWh'].cumsum()
        
        # 2. Económico (Usando la Tarifa de la columna E - índice 3)
        tarifa = pd.to_numeric(dfm[cols_m[3]], errors='coerce').fillna(0)
        dfm['Desemp_COP'] = dfm['Desemp_kWh'] * tarifa
        dfm['CUSUM_COP']  = dfm['Desemp_COP'].cumsum()
        
        # 3. Ambiental (Usando el Factor de Emisión de la columna F - índice 4)
        fe = pd.to_numeric(dfm[cols_m[4]], errors='coerce').fillna(0)
        dfm['Desemp_CO2'] = dfm['Desemp_kWh'] * fe
        dfm['CUSUM_CO2']  = dfm['Desemp_CO2'].cumsum()
        
        res_monitoreo = dfm

    return df_lben, res_monitoreo, dfb

def calcular_resumen_metricas(df_lben, df_base_raw):
    """Calcula el resumen granular para la Ficha Técnica."""
    # 1. Energía y Ahorro
    consumo_anual_lben = df_lben['lben'].sum()
    ahorro_total_kwh = (df_lben['lben'] - df_lben['min_hist']).sum()
    ahorro_anual_pct = (ahorro_total_kwh / consumo_anual_lben) if consumo_anual_lben > 0 else 0
    
    # 2. Conteo Granular de Datos
    n_inicial = len(df_base_raw)
    n_excl_man = (df_base_raw[df_base_raw.columns[7]].astype(str).str.upper() == 'SI').sum()
    n_final = df_lben['n_usados'].sum()
    n_filt_est = n_inicial - n_final - n_excl_man
    
    fiabilidad = (n_final / n_inicial) if n_inicial > 0 else 0
    
    return {
        "consumo_promedio_anual": consumo_anual_lben,
        "potencial_ahorro_kwh": ahorro_total_kwh,
        "potencial_ahorro_pct": ahorro_anual_pct,
        "n_inicial": n_inicial,
        "n_filt_est": n_filt_est,
        "n_filt_man": n_excl_man,
        "n_final": n_final,
        "fiabilidad": fiabilidad,
        "meta_15": consumo_anual_lben * 0.15
    }
