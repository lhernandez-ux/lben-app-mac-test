"""
core/exploratorio.py
====================
Cálculos estadísticos para el análisis exploratorio.
Ruta 1 — Pearson, p-valor, clasificación y recomendación de modelo.
Sin imports de tkinter ni openpyxl.
"""

import numpy as np
import pandas as pd
from scipy import stats


# ═══════════════════════════════════════════════════════════════════════════════
# CLASIFICACIÓN DE CORRELACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

def clasificar_correlacion(r: float) -> str:
    """
    Clasifica la correlación según el valor absoluto de r.
    Solo informativa, no afecta la decisión del modelo.
    """
    r_abs = abs(r)
    if r_abs >= 0.90:
        return "Fuerte"
    elif r_abs >= 0.70:
        return "Moderada"
    elif r_abs >= 0.50:
        return "Débil"
    else:
        return "Muy débil / Sin inf."


# ═══════════════════════════════════════════════════════════════════════════════
# CÁLCULO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def calcular_correlaciones(
    df: pd.DataFrame,
    var_dep: str,
    vars_ind: list[str],
    alpha: float = 0.05
) -> list[dict]:
    """
    Calcula r de Pearson y p-valor para cada variable independiente
    contra la variable dependiente.

    Parámetros
    ----------
    df       : DataFrame con los datos (ya validados y numéricos)
    var_dep  : nombre columna dependiente (consumo)
    vars_ind : lista de nombres de variables independientes
    alpha    : nivel de significancia (default 0.05)

    Retorna
    -------
    Lista de dicts con keys:
        variable, r_pearson, p_valor, significativa, grado, interpretacion, n
    """
    resultados = []

    if var_dep not in df.columns:
        return resultados

    y = pd.to_numeric(df[var_dep], errors="coerce")

    # 1. Cálculo base de correlaciones
    for var in vars_ind:
        if var not in df.columns:
            continue

        x = pd.to_numeric(df[var], errors="coerce")
        mask  = y.notna() & x.notna()
        y_val = y[mask].values
        x_val = x[mask].values
        n     = len(x_val)

        if n < 3:
            resultados.append({
                "variable":       var,
                "r_pearson":      None,
                "p_valor":        None,
                "significativa":  False,
                "grado":          "Sin datos",
                "interpretacion": f"Mínimo 3 datos.",
                "sugerencia":     "Excluir",
                "vif":            None,
                "n":              n
            })
            continue

        r, p_valor = stats.pearsonr(x_val, y_val)
        resultados.append({
            "variable":       var,
            "r_pearson":      round(r, 4),
            "p_valor":        round(p_valor, 4),
            "significativa":  p_valor < alpha,
            "grado":          clasificar_correlacion(r),
            "vif":            1.0, # Placeholder
            "n":              n
        })

    # 2. Análisis de Colinealidad (VIF) y Selección Sugerida
    # Filtramos las que son al menos significativas para el análisis de competencia
    vars_validas = [r["variable"] for r in resultados if r["significativa"]]
    
    # Cálculo de VIF si hay más de una variable significativa
    vifs = {}
    if len(vars_validas) > 1:
        try:
            from statsmodels.stats.outliers_influence import variance_inflation_factor
            import statsmodels.api as sm
            X = df[vars_validas].apply(pd.to_numeric, errors='coerce').dropna()
            if len(X) > len(vars_validas):
                X_const = sm.add_constant(X)
                for i, var in enumerate(vars_validas):
                    # +1 porque el índice 0 es la constante
                    vifs[var] = variance_inflation_factor(X_const.values, i + 1)
        except Exception: pass

    # 3. Lógica de Sugerencia Decisiva (Competencia por Colinealidad)
    # Paso A: Marcar las no significativas
    for res in resultados:
        if not res["significativa"]:
            res["sugerencia"] = "Excluir"
            res["interpretacion"] = "No representativa (p >= 0.05)."
            res["vif"] = round(vifs.get(res["variable"], 1.0), 2)

    # Paso B: Tratar las significativas y resolver colinealidad
    sig_res = [r for r in resultados if r["significativa"]]
    
    # Ordenamos las significativas por |r| de mayor a menor para que la "mejor" tenga prioridad
    sig_res.sort(key=lambda d: abs(d["r_pearson"]), reverse=True)
    
    variables_ya_excluidas = set()
    
    for i, res in enumerate(sig_res):
        var = res["variable"]
        res["vif"] = round(vifs.get(var, 1.0), 2)
        
        if var in variables_ya_excluidas:
            continue

        # Si tiene VIF alto (>5), buscamos con quién colisiona
        if res["vif"] > 5:
            v_validas = [r["variable"] for r in sig_res]
            corr_matrix = df[v_validas].apply(pd.to_numeric, errors="coerce").corr().abs()
            
            for j in range(i + 1, len(sig_res)):
                comp = sig_res[j]
                v_comp = comp["variable"]
                
                if v_comp in variables_ya_excluidas: continue
                
                # Si son muy similares (>0.85), excluimos a la competidora (porque r_i > r_j)
                if corr_matrix.loc[var, v_comp] > 0.85:
                    comp["sugerencia"] = "Excluir"
                    # Construir interpretación compuesta para la excluida
                    base_int = _generar_interpretacion(v_comp, comp["r_pearson"], comp["p_valor"], True, comp["grado"])
                    # Quitamos el final estándar de "Incluir..." si existiera
                    base_int = base_int.split(". Incluir")[0] + "."
                    comp["interpretacion"] = f"{base_int} Colineal con '{var}'. Use solo una."
                    variables_ya_excluidas.add(v_comp)

        # Si no fue excluida por colinealidad previa, se incluye definitivamente
        if "sugerencia" not in res:
            res["sugerencia"] = "Incluir"
            res["interpretacion"] = _generar_interpretacion(var, res["r_pearson"], res["p_valor"], True, res["grado"])

    # Ordenar por |r| descendente para la vista final
    resultados.sort(key=lambda d: abs(d["r_pearson"]) if d["r_pearson"] is not None else 0, reverse=True)
    return resultados


# ═══════════════════════════════════════════════════════════════════════════════
# RECOMENDACIÓN DE MODELO
# ═══════════════════════════════════════════════════════════════════════════════

def recomendar_modelo(resultados: list[dict]) -> dict:
    """
    Determina el modelo recomendado según número de variables significativas.

    Lógica:
        S = 0  →  M1 (Promedios)
        S = 1  →  M2 (Cociente)
        S ≥ 2  →  M3 (Regresión Lineal Múltiple)

    Retorna dict con:
        modelo, codigo, titulo, justificacion, vars_significativas
    """
    vars_sig = [
        r for r in resultados
        if r["significativa"] and r["r_pearson"] is not None
    ]
    s = len(vars_sig)

    if s == 0:
        if not resultados:
            justificacion = (
                "Se analizó únicamente el consumo histórico. "
                "El modelo M1 construirá la línea base como el "
                "promedio histórico del consumo mensual."
            )
        else:
            justificacion = (
                "No se detectaron variables estadísticamente significativas "
                "(p < 0.05). El modelo M1 construirá la línea base como el "
                "promedio histórico del consumo mensual."
            )

        return {
            "modelo":      "M1",
            "codigo":      "M1",
            "titulo":      "Modelo de Consumo Absoluto (M1)",
            "justificacion": justificacion,
            "vars_significativas": []
        }
    elif s == 1:
        var_nombre = vars_sig[0]["variable"]
        return {
            "modelo":      "M2",
            "codigo":      "M2",
            "titulo":      "Modelo de Cociente (M2)",
            "justificacion": (
                f"Se detectó 1 variable estadísticamente significativa "
                f"(p < 0.05): '{var_nombre}'. El modelo M2 construirá "
                f"el indicador de consumo como Energía / {var_nombre}."
            ),
            "vars_significativas": [v["variable"] for v in vars_sig]
        }
    else:
        vars_nombres = ", ".join(v["variable"] for v in vars_sig)
        return {
            "modelo":      "M3",
            "codigo":      "M3",
            "titulo":      "Regresión Lineal Múltiple (M3)",
            "justificacion": (
                f"Se detectaron {s} variables estadísticamente significativas "
                f"(p < 0.05): {vars_nombres}. El modelo M3 combinará estos "
                "factores para una línea base precisa y ajustada a la "
                "realidad operativa."
            ),
            "vars_significativas": [v["variable"] for v in vars_sig]
        }


# ═══════════════════════════════════════════════════════════════════════════════
# ANÁLISIS AVANZADO (OUTLIERS, COLINEALIDAD, PATRONES)
# ═══════════════════════════════════════════════════════════════════════════════

def obtener_diagnostico_avanzado(df: pd.DataFrame, var_dep: str, vars_ind: list[str]) -> dict:
    """
    Ejecuta un diagnóstico completo de la calidad de los datos.
    """
    return {
        "outliers":      detectar_outliers(df, var_dep),
        "colinealidad":  detectar_colinealidad(df, vars_ind),
        "estacionalidad": analizar_estacionalidad(df, var_dep)
    }

def detectar_outliers(df: pd.DataFrame, col: str) -> dict:
    """
    Detecta valores atípicos usando el método IQR (Rango Intercuartílico).
    """
    if col not in df.columns: return {"conteo": 0, "mensajes": []}
    
    y = pd.to_numeric(df[col], errors="coerce").dropna()
    if len(y) < 5: return {"conteo": 0, "mensajes": []}

    q1 = y.quantile(0.25)
    q3 = y.quantile(0.75)
    iqr = q3 - q1
    limite_inf = q1 - 1.5 * iqr
    limite_sup = q3 + 1.5 * iqr

    outliers_mask = (y < limite_inf) | (y > limite_sup)
    indices = y[outliers_mask].index.tolist()
    
    mensajes = []
    if len(indices) > 0:
        for idx in indices:
            fecha_str = df.loc[idx, "Fecha"] if "Fecha" in df.columns else f"registro {idx+1}"
            valor = y[idx]
            tipo = "inusualmente alto" if valor > limite_sup else "inusualmente bajo"
            mensajes.append(f"El {fecha_str} se detectó un consumo {tipo} ({valor:,.0f}).")
            
    return {
        "conteo": len(indices),
        "indices": indices,
        "mensajes": mensajes,
        "limites": (limite_inf, limite_sup)
    }

def detectar_colinealidad(df: pd.DataFrame, vars_ind: list[str], threshold: float = 0.85) -> list:
    """
    Detecta si dos variables independientes son muy parecidas (colinealidad).
    """
    alertas = []
    v_validas = [v for v in vars_ind if v in df.columns]
    
    if len(v_validas) < 2: return alertas

    # Matriz de correlación solo para variables independientes
    corr_matrix = df[v_validas].apply(pd.to_numeric, errors="coerce").corr().abs()

    for i in range(len(v_validas)):
        for j in range(i + 1, len(v_validas)):
            v1, v2 = v_validas[i], v_validas[j]
            r = corr_matrix.loc[v1, v2]
            if r > threshold:
                alertas.append({
                    "variables": (v1, v2),
                    "r": round(r, 2),
                    "mensaje": f"'{v1}' y '{v2}' están altamente correlacionadas entre sí (r={r:.2f}). Esta colinealidad sugiere usar solo una de ellas para evitar inestabilidad en el modelo."
                })
    return alertas

def analizar_tendencia(df: pd.DataFrame, col: str) -> dict:
    """
    Calcula la tendencia lineal del consumo (creciente, decreciente o estacionaria).
    """
    if col not in df.columns: return {"clase": "N/D", "pendiente": 0}
    
    y = pd.to_numeric(df[col], errors="coerce").dropna().values
    if len(y) < 3: return {"clase": "Insuficiente", "pendiente": 0}

    # Normalizar y para que la pendiente sea comparable
    y_norm = (y - y.min()) / (y.max() - y.min()) if (y.max() - y.min()) != 0 else y
    x = np.arange(len(y_norm))
    
    slope, *_ = stats.linregress(x, y_norm)
    
    if slope > 0.015:
        clase = "Creciente"
        desc = "Tendencia Creciente a largo plazo."
    elif slope < -0.015:
        clase = "Decreciente"
        desc = "Tendencia Decreciente a largo plazo."
    else:
        clase = "Estacionaria"
        desc = "Comportamiento Estacionario a largo plazo."
        
    return {"clase": clase, "descripcion": desc, "pendiente": round(slope, 4)}

def analizar_estacionalidad(df: pd.DataFrame, col: str) -> dict:
    """
    Identifica el tipo de ciclo (Unimodal, Bimodal, Estable) y meses críticos.
    Basado en el promedio mensual y umbrales de picos.
    """
    if col not in df.columns: return {"pico": "N/D", "valle": "N/D", "tipo": "N/D", "mensaje": "Sin datos"}
    
    df_copy = df.copy()
    df_copy[col] = pd.to_numeric(df_copy[col], errors="coerce")
    
    try:
        if "Fecha" in df_copy.columns:
            # Silenciar el warning de inferencia de formato
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                fechas_dt = pd.to_datetime(df_copy["Fecha"], errors='coerce', dayfirst=True)
            
            df_copy["Mes_Num"] = fechas_dt.dt.month
            
            df_val = df_copy[df_copy["Mes_Num"].notna()].copy()
            if df_val.empty: return {"pico": "N/D", "valle": "N/D", "tipo": "N/D", "mensaje": "Fecha inválida"}

            promedios = df_val.groupby("Mes_Num")[col].mean()
            global_avg = df_val[col].mean()
            
            # Identificar Picos (> 1.15 x promedio)
            picos_indices = promedios[promedios > (global_avg * 1.15)].index.tolist()
            meses_nombres = ["?", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            
            n_picos = len(picos_indices)
            if n_picos == 1:
                tipo = "Ciclo Unimodal"
                detalle = f"Un solo periodo de alta demanda detectado en {meses_nombres[picos_indices[0]]}."
            elif n_picos == 2:
                tipo = "Ciclo Bimodal"
                detalle = f"Dos temporadas de alta demanda en {meses_nombres[picos_indices[0]]} y {meses_nombres[picos_indices[1]]}."
            elif n_picos > 2:
                tipo = "Alta Volatilidad"
                detalle = "Consumo irregular con múltiples fluctuaciones significativas."
            else:
                tipo = "Estable / Plano"
                detalle = "Carga constante: Ningún mes se aleja más del 15% del promedio anual."

            mes_pico = int(promedios.idxmax())
            mes_valle = int(promedios.idxmin())
            
            return {
                "pico": meses_nombres[mes_pico],
                "valle": meses_nombres[mes_valle],
                "tipo": tipo,
                "mensaje": detalle,
                "tendencia": analizar_tendencia(df, col)
            }
    except Exception as e:
        print(f"Error estacionalidad: {e}")
    
    return {"pico": "N/D", "valle": "N/D", "tipo": "N/D", "mensaje": "Error en cálculo de ciclos"}

def calcular_puntajes_sincronia(resultados_pearson: list[dict]) -> dict:
    """
    Convierte r de Pearson en un diagnóstico de sincronía (Directa/Inversa).
    """
    diagnosticos = {}
    for r in resultados_pearson:
        val = r["r_pearson"]
        if val is not None:
            # Magnitud
            mag = abs(val) * 100
            if mag < 40:
                nivel = "Baja / Independiente"
                tipo = "Independiente"
            elif mag < 75:
                nivel = "Moderada"
                tipo = "Directa" if val > 0 else "Inversa"
            else:
                nivel = "Alta"
                tipo = "Directa" if val > 0 else "Inversa"
            
            diagnosticos[r["variable"]] = {
                "porcentaje": round(mag, 1),
                "nivel": nivel,
                "tipo": tipo,
                "mensaje": f"{nivel} ({tipo})" if tipo != "Independiente" else nivel
            }
    return diagnosticos


# ═══════════════════════════════════════════════════════════════════════════════
# DATOS PARA GRÁFICOS
# ═══════════════════════════════════════════════════════════════════════════════

def preparar_datos_scatter(
    df: pd.DataFrame,
    var_dep: str,
    var_ind: str
) -> dict:
    """
    Prepara datos limpios para un scatter plot entre var_dep y var_ind.

    Retorna dict con:
        x, y        : arrays limpios
        x_trend     : array para línea de tendencia
        y_trend     : array para línea de tendencia
        r, p_valor  : estadísticos
        n           : número de puntos válidos
    """
    y = pd.to_numeric(df[var_dep], errors="coerce")
    x = pd.to_numeric(df[var_ind], errors="coerce")

    mask  = y.notna() & x.notna()
    x_val = x[mask].values
    y_val = y[mask].values
    n     = len(x_val)

    if n < 3:
        return {"x": x_val, "y": y_val, "n": n,
                "x_trend": [], "y_trend": [],
                "r": None, "p_valor": None}

    r, p_valor = stats.pearsonr(x_val, y_val)

    # Línea de tendencia (regresión simple)
    slope, intercept, *_ = stats.linregress(x_val, y_val)
    x_trend = np.linspace(x_val.min(), x_val.max(), 100)
    y_trend = slope * x_trend + intercept

    return {
        "x":       x_val,
        "y":       y_val,
        "x_trend": x_trend,
        "y_trend": y_trend,
        "r":       round(r, 4),
        "p_valor": round(p_valor, 4),
        "n":       n
    }


def preparar_datos_sincronia(
    df: pd.DataFrame,
    var_dep: str,
    vars_ind: list[str]
) -> dict:
    """
    Normaliza consumo y variables entre 0 y 1 para el gráfico
    de sincronía temporal.

    Retorna dict con:
        fechas      : lista de etiquetas
        series      : dict {nombre_variable: array_normalizado}
    """
    fechas = df["Fecha"].tolist() if "Fecha" in df.columns else \
             list(range(len(df)))

    series = {}

    # Consumo
    y = pd.to_numeric(df[var_dep], errors="coerce").values
    series[var_dep] = _normalizar(y)

    # Variables independientes
    for var in vars_ind:
        if var in df.columns:
            x = pd.to_numeric(df[var], errors="coerce").values
            series[var] = _normalizar(x)

    return {"fechas": fechas, "series": series}


# ═══════════════════════════════════════════════════════════════════════════════
# UTILIDADES INTERNAS
# ═══════════════════════════════════════════════════════════════════════════════

def _normalizar(arr: np.ndarray) -> np.ndarray:
    """Normaliza array entre 0 y 1 (min-max)."""
    arr = arr.astype(float)
    mn, mx = np.nanmin(arr), np.nanmax(arr)
    if mx == mn:
        return np.zeros_like(arr)
    return (arr - mn) / (mx - mn)


def _generar_interpretacion(
    var: str,
    r: float,
    p_valor: float,
    significativa: bool,
    grado: str
) -> str:
    """Genera texto de interpretación para la tabla de resultados."""
    if significativa:
        direccion = "positiva" if r > 0 else "negativa"
        fuerza = grado.lower()
        impacto = "Variable dominante" if fuerza in ["alto", "muy alto"] else "Impacto moderado"
        return f"Correlación {fuerza} {direccion} con el consumo. {impacto}. Incluir en modelo LBEn."
    else:
        return (
            f"No significativa (p ≥ 0.05). No incluir en modelo LBEn."
        )