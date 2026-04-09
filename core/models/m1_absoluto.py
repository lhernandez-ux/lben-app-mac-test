"""
core/models/m1_absoluto.py
==========================
Lógica de cálculo para el Modelo M1 de Consumo Absoluto.
Sigue los lineamientos de la Resolución UPME 016/2024.
"""

import pandas as pd
import numpy as np

def procesar_m1(df_base: pd.DataFrame, df_monitoreo: pd.DataFrame = None):
    """
    Motor principal del Modelo M1.
    Calcula la LBEn mensual, filtrando datos atípicos.
    """
    
    # 1. Limpieza y Normalización Inicial
    # Aseguramos nombres de columnas estándar internamente
    # Col B: Fecha, Col C: Consumo, Col D: Días
    dfb = df_base.copy()
    
    # Intentamos identificar columnas por posición o nombre aproximado
    # Suponiendo: Fecha (0), Consumo (1), Dias (2)
    col_consumo = dfb.columns[1]
    col_dias = dfb.columns[2]
    
    dfb['Consumo_Num'] = pd.to_numeric(dfb[col_consumo], errors='coerce')
    dfb['Dias_Num'] = pd.to_numeric(dfb[col_dias], errors='coerce')
    
    # Normalización a 30 días
    dfb['Normalizado'] = (dfb['Consumo_Num'] / dfb['Dias_Num']) * 30
    
    # Extraer Mes (1-12)
    # Nota: El formato de fecha en el Excel es 'Ene-2022' o similar
    # Para mayor robustez, intentaremos parsear
    dfb['Month'] = pd.to_datetime(dfb['Fecha'], errors='coerce').dt.month
    
    # 2. Filtrado y Cálculo de LBEn por Mes
    resultados_lben = []
    
    for mes in range(1, 13):
        n_mes = {1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril', 5:'Mayo', 6:'Junio',
                 7:'Julio', 8:'Agosto', 9:'Septiembre', 10:'Octubre', 11:'Noviembre', 12:'Diciembre'}[mes]
        
        datos_mes = dfb[dfb['Month'] == mes]['Normalizado'].dropna()
        n_inicial = len(datos_mes)
        
        if n_inicial == 0:
            resultados_lben.append({
                'mes': n_mes, 'lben': 0, 'n_usados': 0, 
                'lim_inf': 0, 'lim_sup': 0, 'min_hist': 0
            })
            continue
            
        mean_val = datos_mes.mean()
        std_val = datos_mes.std()
        
        # Lógica de filtrado solicitada
        if n_inicial <= 10:
            # Filtro +/- 10%
            filtered = datos_mes[(datos_mes >= mean_val * 0.9) & (datos_mes <= mean_val * 1.1)]
        else:
            # Filtro +/- 2 SD
            filtered = datos_mes[(datos_mes >= mean_val - 2*std_val) & (datos_mes <= mean_val + 2*std_val)]
            
        n_final = len(filtered)
        lben_val = filtered.mean() if n_final > 0 else mean_val
        
        # Límites estadísticos (ej. para gráficos)
        resultados_lben.append({
            'mes': n_mes,
            'lben': lben_val,
            'n_usados': n_final,
            'n_inicial': n_inicial,
            'lim_inf': lben_val - (filtered.std() * 2 if n_final > 1 else 0),
            'lim_sup': lben_val + (filtered.std() * 2 if n_final > 1 else 0),
            'min_hist': filtered.min() if n_final > 0 else 0
        })
        
    df_lben = pd.DataFrame(resultados_lben)
    
    # 3. Monitoreo (si existe)
    res_monitoreo = None
    if df_monitoreo is not None and not df_monitoreo.empty:
        dfm = df_monitoreo.copy()
        dfm['Month'] = pd.to_datetime(dfm['Fecha'], errors='coerce').dt.month
        
        # Unir con la LBEn calculada
        dfm = dfm.merge(df_lben[['mes', 'lben']], left_on='Month', right_index=True, how='left')
        # Nota: Mejor merge por nombre de mes o numero de mes
        # map lben to months
        lben_map = df_lben.set_index(df_lben.index + 1)['lben'].to_dict()
        dfm['LBEn_Mes'] = dfm['Month'].map(lben_map)
        
        # Normalización monitoreo
        col_c_m = dfm.columns[1]
        col_d_m = dfm.columns[2]
        dfm['Normalizado'] = (pd.to_numeric(dfm[col_c_m], errors='coerce') / 
                              pd.to_numeric(dfm[col_d_m], errors='coerce')) * 30
        
        # Desempeño
        dfm['Ahorro_kWh'] = dfm['LBEn_Mes'] - dfm['Normalizado']
        dfm['Ahorro_Pct'] = (dfm['Ahorro_kWh'] / dfm['LBEn_Mes']) * 100
        
        res_monitoreo = dfm
        
    return df_lben, res_monitoreo

def calcular_resumen_metricas(df_lben):
    """Calcula totales como potencial de ahorro anual."""
    consumo_anual_lben = df_lben['lben'].sum()
    consumo_anual_min = df_lben['min_hist'].sum()
    
    potencial_ahorro_kwh = consumo_anual_lben - consumo_anual_min
    potencial_ahorro_pct = (potencial_ahorro_kwh / consumo_anual_lben * 100) if consumo_anual_lben > 0 else 0
    
    return {
        "consumo_promedio_anual": consumo_anual_lben,
        "potencial_ahorro_anual": potencial_ahorro_pct,
        "total_datos_usados": df_lben['n_usados'].sum()
    }
