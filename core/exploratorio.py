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

    for var in vars_ind:
        if var not in df.columns:
            continue

        x = pd.to_numeric(df[var], errors="coerce")

        # Eliminar filas con NaN en cualquiera de las dos series
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
                "grado":          "Sin datos suficientes",
                "interpretacion": f"Solo {n} datos válidos. Mínimo requerido: 3.",
                "n":              n
            })
            continue

        # Cálculo con scipy (incluye t-estadístico internamente)
        r, p_valor = stats.pearsonr(x_val, y_val)

        significativa = p_valor < alpha
        grado         = clasificar_correlacion(r)
        interpretacion = _generar_interpretacion(var, r, p_valor,
                                                  significativa, grado)

        resultados.append({
            "variable":       var,
            "r_pearson":      round(r, 4),
            "p_valor":        round(p_valor, 4),
            "significativa":  significativa,
            "grado":          grado,
            "interpretacion": interpretacion,
            "n":              n
        })

    # Ordenar por |r| descendente
    resultados.sort(
        key=lambda d: abs(d["r_pearson"]) if d["r_pearson"] is not None else 0,
        reverse=True
    )

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
        return {
            "modelo":      "M1",
            "codigo":      "M1",
            "titulo":      "Modelo de Promedio (M1)",
            "justificacion": (
                "No se detectaron variables estadísticamente significativas "
                f"(p < 0.05). El modelo M1 construirá la línea base como el "
                "promedio histórico del consumo mensual."
            ),
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
        return (
            f"Correlación {grado.lower()} {direccion} con el consumo. "
            f"Variable dominante. Incluir en modelo LBEn."
        )
    else:
        return (
            f"No significativa (p ≥ 0.05). No incluir en modelo LBEn."
        )