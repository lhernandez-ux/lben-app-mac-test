# Código Completo del Proyecto

## Raíz del Proyecto

### .gitignore

```python
.venv/
__pycache__/
*.pyc
.ipynb_checkpoints/
.DS_Store
*.log
contexto/
app/data/temp/
results/
dist/
build/
*.spec

```

### README.md

```python

```

### main.py

```python
"""
main.py
=======
LBEn App — Resolución UPME 016/2024
Punto de entrada principal.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from ui.theme import aplicar_tema
from ui.app import App


def main():
    aplicar_tema()
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
```

### requirements.txt

```python
# GUI
customtkinter>=5.2.0
Pillow>=10.0.0

# Datos y cálculo
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.11.0
scikit-learn>=1.3.0
statsmodels>=0.14.0

# Gráficos
matplotlib>=3.7.0

# Excel
openpyxl>=3.1.0

# Empaquetado ejecutable
pyinstaller>=6.0.0
```

## Contexto

### arbol.txt

```python
LBEn_APP_Resol016/
├── main.py
├── requirements.txt
├── assets/                  # íconos, imágenes, logo
├── data/                    # plantillas Excel base
├── core/
│   ├── models/
│   │   ├── m1_absoluto.py
│   │   ├── m2_cociente.py
│   │   └── m3_regresion.py
│   ├── exploratorio.py      # Ruta 1: Pearson, p-valor, recomendación
│   ├── io_excel.py          # lectura/escritura Excel
│   └── ajuste_nr.py         # (rescatado y limpiado)
├── ui/
│   ├── app.py               # ventana principal + navegación
│   ├── theme.py             # colores y fuentes
│   ├── components/          # widgets reutilizables
│   └── pages/
│       ├── home.py          # pantalla de inicio
│       ├── exploratorio.py  # Ruta 1
│       ├── m1.py            # Ruta 2 - Método 1
│       ├── m2.py            # Ruta 2 - Método 2
│       ├── m3.py            # Ruta 2 - Método 3
│       └── monitoreo.py     # Ruta 3
└── state/
    └── session.py           # estado compartido entre pantallas
```

## Contexto / Exploracion

### exploracion.txt

```python
# Ruta 1: Análisis Exploratorio

## Especificación Funcional Ejecutable (EFE)

---

## 1. Objetivo

Implementar una funcionalidad que permita:

* Configurar un análisis exploratorio
* Generar una plantilla Excel estructurada
* Analizar correlaciones entre variables
* Evaluar significancia estadística
* Recomendar el modelo de línea base energética (LBEn)
* Exportar resultados al Excel

---

## 2. Alcance

### Incluye:

* Configuración del análisis exploratorio
* Generación de plantilla Excel
* Carga de archivo Excel
* Validación básica de datos
* Cálculo de correlaciones (r) y p-valores
* Visualización de resultados
* Recomendación de modelo

### No incluye:

* Construcción de modelos
* Optimización
* Monitoreo

---

## 3. Flujo general

1. Usuario configura análisis exploratorio
2. Usuario descarga plantilla Excel
3. Usuario diligencia datos
4. Usuario carga archivo Excel
5. Sistema procesa información
6. Sistema calcula correlaciones y p-valores
7. Sistema genera visualizaciones
8. Sistema recomienda modelo
9. Sistema permite exportar resultados al Excel

---

## 4. Módulo 1: Configuración de análisis

### Inputs requeridos:

* Nombre del proyecto
* Fecha inicio
* Fecha fin
* Variable dependiente (consumo)
* Variables independientes

### Reglas:

* La variable dependiente debe ir inmediatamente después de la fecha
* Las variables independientes se agregan dinámicamente
* Si se superan 5 variables, se deben crear nuevas columnas automáticamente

---

## 5. Módulo 2: Generación de plantilla Excel

### Nombre del archivo:

plantilla_exploracion_modelo.xlsx

### Estructura:

#### Hoja 1: Instrucciones

* Celda C3: recomendación del modelo
* Celdas C11–C13:

  * Variable dependiente
  * Variables independientes
  * Rango de fechas

---

#### Hoja 2: Periodo de análisis

* Columna B (desde B8): fechas (formato mes-año, frecuencia mensual)
* Fila 6:

  * Columna C: consumo
  * Columnas siguientes: variables independientes
* Fila 7: hints

### Reglas:

* El usuario SOLO llena esta hoja
* Datos deben ser numéricos
* Formato:

  * Separador de miles: ","
  * Decimales: "."

---

#### Hoja 3: Modelo

* Inicialmente vacía
* Se llena automáticamente luego del análisis

Se deben completar:

* Celdas D5, D6, D7
* Tabla desde B12

---

## 6. Módulo 3: Carga de Excel

### Validaciones mínimas:

* Archivo válido
* Hoja "Periodo de análisis" existe
* Datos numéricos
* No valores nulos críticos

---

## 7. Módulo 4: Cálculo estadístico

Para cada variable independiente Xi:

### 7.1 Correlación

Calcular r_i (Pearson) entre consumo (E) y Xi

r ∈ [-1, 1]

---

### 7.2 Estadístico t

t_i = r_i * sqrt(N - 2) / sqrt(1 - r_i²)

df = N - 2

---

### 7.3 p-valor

Calcular p_i usando distribución t de Student

Alternativa:
scipy.stats.pearsonr(x, y)

---

## 8. Criterio de significancia

Una variable es significativa si:

p_i < 0.05

---

## 9. Clasificación de correlación (informativa)

| |r| | Clasificación |
|-----|--------------|
| ≥ 0.90 | Fuerte |
| 0.70 – 0.89 | Moderada |
| 0.50 – 0.69 | Débil |
| < 0.50 | Muy débil |

Nota: solo informativa, no afecta la decisión del modelo

---

## 10. Lógica de recomendación de modelo

Definir:

S = número de variables con p_i < 0.05

---

### Caso 1: S = 0

Modelo: M1 (Promedios)
Interpretación: no hay relación estadística significativa
Acción: usar promedio histórico

---

### Caso 2: S = 1

Modelo: M2 (Cociente)
Interpretación: una variable explica el consumo
Acción: construir indicador E / X₁

---

### Caso 3: S ≥ 2

Modelo: M3 (Regresión múltiple)
Interpretación: múltiples variables explican el consumo
Acción: modelo lineal múltiple

---

## 11. Visualizaciones

### Por variable:

* Scatter plot

  * X: variable Xi
  * Y: consumo
  * Incluir línea de tendencia

Mostrar:

* r_i
* p_i
* clasificación

---

### Global:

* Gráfico de sincronía temporal

  * Series normalizadas (consumo y variables)

Objetivo:

* Validar visualmente la correlación

---

## 12. Outputs

* Tabla de resultados:

  * r_i
  * p_i
  * clasificación

* Modelo recomendado (M1, M2, M3)

* Excel actualizado con:

  * recomendación
  * resultados

---

## 13. Exportación

Botón: "Actualizar Excel"

Acción:

* Descargar archivo Excel actualizado

Contenido:

* Hoja instrucciones: recomendación
* Hoja modelo:

  * Celdas D5–D7
  * Tabla desde B12

---

## 14. Navegación

* Botón regresar
* Botón cargar archivo
* Botón continuar a selección de modelos

---

## 15. Restricciones

* Datos numéricos
* N ≥ 3 (mínimo técnico)
* Recomendado: N ≥ 12

---

## 16. Criterios de aceptación

El módulo es correcto si:

* Calcula r y p correctamente
* Identifica variables significativas
* Clasifica correctamente el modelo
* Genera todos los gráficos
* Permite exportar el Excel actualizado

---

## 17. Consideraciones futuras

* Control de outliers
* Multicolinealidad (VIF)
* Selección automática de variables
* Métodos avanzados (clustering, DTW)

```

## Contexto / Consumo

## Core

### ajuste_nr.py

```python

```

### exploratorio.py

```python
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
    Detecta si dos variables independientes son muy parecidas (redundantes).
    """
    alertas = []
    v_validas = [v for v in vars_ind if v in df.columns]
    
    if len(v_validas) < 2: return alertas

    # Matriz de correlación solo para variables independientes
    corr_matrix = df[v_validas].apply(pd.to_numeric, errors="coerce").corr().abs()

    parejas_vistas = set()
    for i in range(len(v_validas)):
        for j in range(i + 1, len(v_validas)):
            v1, v2 = v_validas[i], v_validas[j]
            r = corr_matrix.loc[v1, v2]
            if r > threshold:
                alertas.append({
                    "variables": (v1, v2),
                    "r": round(r, 2),
                    "mensaje": f"'{v1}' y '{v2}' son muy similares (r={r:.2f}). Usar ambas podría confundir al modelo."
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
        return (
            f"Correlación {grado.lower()} {direccion} con el consumo. "
            f"Variable dominante. Incluir en modelo LBEn."
        )
    else:
        return (
            f"No significativa (p ≥ 0.05). No incluir en modelo LBEn."
        )
```

### io_excel.py

```python
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
```

## Core / Models

### m1_absoluto.py

```python
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

```

### m2_cociente.py

```python

```

### m3_regresion.py

```python

```

## Ui

### app.py

```python
"""
ui/app.py
=========
Ventana principal y navegación entre pantallas.
"""

import customtkinter as ctk
from ui.theme import COLORS, FONTS, DIMS


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ── Configuración ventana ─────────────────────────────────────────────
        self.title("Línea Base Energética — UPME 016/2024")
        self.geometry("1100x700")
        self.minsize(1000, 650)
        self.configure(fg_color=COLORS.bg_main)

        # ── Estado global de sesión ───────────────────────────────────────────
        self.session = {
            "ruta": None,               # "exploratorio" | "modelado" | "monitoreo"
            "proyecto_nombre": None,
            "fecha_inicio": None,
            "fecha_fin": None,
            "var_dependiente": None,
            "vars_independientes": [],
            "excel_path": None,         # ruta al Excel cargado
            "df_datos": None,           # DataFrame con datos cargados
            "resultados_exploratorio": None,
        }

        # ── Contenedor principal ──────────────────────────────────────────────
        self._frame_actual = None
        self._iniciar_navegacion()

    # ── Navegación ────────────────────────────────────────────────────────────
    def _iniciar_navegacion(self):
        self.navegar("home")

    def navegar(self, destino: str, **kwargs):
        """
        Destruye el frame actual y carga el nuevo.
        destino: nombre de la pantalla
        kwargs:  parámetros opcionales para la pantalla destino
        """
        if self._frame_actual is not None:
            self._frame_actual.destroy()

        frame = self._crear_frame(destino, **kwargs)
        frame.pack(fill="both", expand=True)
        self._frame_actual = frame

    def _crear_frame(self, destino: str, **kwargs):
        # Importaciones locales para evitar ciclos
        if destino == "home":
            from ui.pages.home import HomePage
            return HomePage(self)

        elif destino == "exploratorio_config":
            from ui.pages.exploratorio_config import ExploratorioConfigPage
            return ExploratorioConfigPage(self)

        elif destino == "exploratorio_carga":
            from ui.pages.exploratorio_carga import ExploratorioCargaPage
            return ExploratorioCargaPage(self)

        elif destino == "exploratorio_resultados":
            from ui.pages.exploratorio_resultados import ExploratorioResultadosPage
            return ExploratorioResultadosPage(self)

        elif destino == "seleccion_modelo":
            from ui.pages.seleccion_modelo import SeleccionModeloPage
            return SeleccionModeloPage(self)

        elif destino == "m1_config":
            from ui.pages.m1_config import M1ConfigPage
            return M1ConfigPage(self)

        elif destino == "m1_carga":
            from ui.pages.m1_carga import M1CargaPage
            return M1CargaPage(self)

        elif destino == "m1_resultados":
            from ui.pages.m1_resultados import M1ResultadosPage
            return M1ResultadosPage(self)

        else:
            raise ValueError(f"Destino desconocido: {destino}")
```

### theme.py

```python
"""
ui/theme.py
===========
ADN Visual — LBEn App
Paleta: Proyectos E2
"""

import customtkinter as ctk

# ── Paleta de colores ─────────────────────────────────────────────────────────
class COLORS:
    # Primarios
    bg_main        = "#EAEAEA"       # Fondo base (light grey)
    primary        = "#204339"       # Verde oscuro (primario)
    primary_dark   = "#162E27"       # Verde muy oscuro (sidebar)
    accent         = "#C2D500"       # Lima (acento)

    # Superficies
    bg_card        = "#FFFFFF"       # Fondo de tarjetas
    bg_sidebar     = "#162E27"       # Fondo sidebar
    border         = "#D0D5CC"       # Bordes suaves

    # Texto
    text_primary   = "#1A1A1A"       # Texto principal
    text_secondary = "#5A6B63"       # Texto secundario
    text_white     = "#FFFFFF"       # Texto sobre fondo oscuro
    text_accent    = "#C2D500"       # Texto acento (sobre primario)

    # Semánticos
    success        = "#2D6A4F"       # Verde éxito
    warning        = "#F4A261"       # Naranja advertencia
    danger         = "#E63946"       # Rojo error
    improvement    = "#40916C"       # Verde mejora
    degradation    = "#E63946"       # Rojo degradación

    # Gradiente especial (para cards destacadas)
    gradient_start = "#162E27"
    gradient_mid   = "#204339"
    gradient_end   = "#C2D500"


# ── Tipografía ────────────────────────────────────────────────────────────────
class FONTS:
    family      = "Inter"
    family_mono = "Courier New"

    size_xs     = 11
    size_sm     = 12
    size_md     = 13
    size_lg     = 15
    size_xl     = 18
    size_xxl    = 24
    size_title  = 30


# ── Dimensiones ───────────────────────────────────────────────────────────────
class DIMS:
    sidebar_width    = 220
    topbar_height    = 50
    card_radius      = 10
    button_radius    = 20       # Pill buttons
    padding_card     = 20
    padding_section  = 30


# ── Configuración global CustomTkinter ───────────────────────────────────────
def aplicar_tema():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")
```

## Ui / Components

### __init__.py

```python
from .selector_fecha import SelectorFecha

```

### selector_fecha.py

```python
"""
ui/components/selector_fecha.py
==============================
Componente de selección de Mes/Año.
"""

import customtkinter as ctk
from datetime import datetime
from ui.theme import COLORS, FONTS

class SelectorFecha(ctk.CTkFrame):
    """
    Componente para seleccionar Mes y Año mediante menús desplegables.
    Retorna la fecha en formato MM/AAAA.
    """
    def __init__(self, master, label_text="Fecha", start_year=2015, end_year=2040, command=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.command = command
        self.meses_nombres = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        self.meses_map = {name: str(i+1).zfill(2) for i, name in enumerate(self.meses_nombres)}
        self.anios = [str(y) for y in range(start_year, end_year + 1)]

        # Layout
        self.grid_columnconfigure(0, weight=1)
        
        # Etiqueta opcional
        if label_text:
            self.label = ctk.CTkLabel(
                self, text=label_text,
                font=(FONTS.family, FONTS.size_xs),
                text_color=COLORS.text_secondary,
                anchor="w"
            )
            self.label.pack(side="top", anchor="w", pady=(0, 4))

        # Contenedor de menus
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="x")

        # Menu Mes
        self.combo_mes = ctk.CTkOptionMenu(
            self.container,
            values=self.meses_nombres,
            command=self._on_change,
            font=(FONTS.family, FONTS.size_sm),
            fg_color=COLORS.bg_card,
            button_color=COLORS.primary,
            button_hover_color=COLORS.primary_dark,
            text_color=COLORS.text_primary,
            dropdown_fg_color=COLORS.bg_card,
            dropdown_text_color=COLORS.text_primary,
            dropdown_hover_color=COLORS.bg_main,
            height=38,
            width=120
        )
        self.combo_mes.pack(side="left", padx=(0, 8))
        self.combo_mes.set("Enero")

        # Menu Año
        self.combo_anio = ctk.CTkOptionMenu(
            self.container,
            values=self.anios,
            command=self._on_change,
            font=(FONTS.family, FONTS.size_sm),
            fg_color=COLORS.bg_card,
            button_color=COLORS.primary,
            button_hover_color=COLORS.primary_dark,
            text_color=COLORS.text_primary,
            dropdown_fg_color=COLORS.bg_card,
            dropdown_text_color=COLORS.text_primary,
            dropdown_hover_color=COLORS.bg_main,
            height=38,
            width=100
        )
        self.combo_anio.pack(side="left")
        
        # Año actual por defecto o el último disponible
        current_year = str(datetime.now().year)
        if current_year in self.anios:
            self.combo_anio.set(current_year)
        else:
            self.combo_anio.set(self.anios[-1])

    def _on_change(self, _=None):
        if self.command:
            self.command()

    def get_value(self) -> str:
        """Retorna formato MM/AAAA"""
        mes = self.meses_map[self.combo_mes.get()]
        anio = self.combo_anio.get()
        return f"{mes}/{anio}"

    def set_value(self, mm_aaaa: str):
        """Establece el valor desde un string MM/AAAA"""
        try:
            mm, aaaa = mm_aaaa.split("/")
            idx = int(mm) - 1
            if 0 <= idx < 12:
                self.combo_mes.set(self.meses_nombres[idx])
            if aaaa in self.anios:
                self.combo_anio.set(aaaa)
        except:
            pass

```

## Ui / Pages

### exploratorio_carga.py

```python
"""
ui/pages/exploratorio_carga.py
================================
Pantalla de carga del Excel exploratorio.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from ui.theme import COLORS, FONTS, DIMS


class ExploratorioCargaPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        self.archivo_path = None
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_topbar()
        self._build_cuerpo()

    # ── Topbar ────────────────────────────────────────────────────────────────
    def _build_topbar(self):
        topbar = ctk.CTkFrame(
            self, fg_color=COLORS.bg_card,
            corner_radius=0, height=DIMS.topbar_height
        )
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)

        ctk.CTkFrame(
            topbar, fg_color=COLORS.accent,
            height=2, corner_radius=0
        ).place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        # Botón regresar a configuración
        ctk.CTkButton(
            topbar,
            text="← Configuración",
            font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent",
            text_color=COLORS.primary,
            hover_color=COLORS.bg_main,
            width=120, height=32,
            corner_radius=DIMS.button_radius,
            command=lambda: self.app.navegar("exploratorio_config")
        ).grid(row=0, column=0, padx=16, pady=8, sticky="w")

        # Título
        ctk.CTkLabel(
            topbar,
            text="Cargar datos",
            font=(FONTS.family, FONTS.size_md, "bold"),
            text_color=COLORS.primary
        ).grid(row=0, column=1, sticky="w", padx=8)

        # Botón inicio
        ctk.CTkButton(
            topbar,
            text="🏠 Inicio",
            font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent",
            text_color=COLORS.primary,
            hover_color=COLORS.bg_main,
            width=80, height=32,
            corner_radius=DIMS.button_radius,
            command=lambda: self.app.navegar("home")
        ).grid(row=0, column=2, padx=16, pady=8, sticky="e")

    # ── Cuerpo ────────────────────────────────────────────────────────────────
    def _build_cuerpo(self):
        cuerpo = ctk.CTkFrame(
            self, fg_color=COLORS.bg_main, corner_radius=0
        )
        cuerpo.grid(row=1, column=0, sticky="nsew")
        cuerpo.grid_columnconfigure(0, weight=1)
        cuerpo.grid_rowconfigure(1, weight=1)

        # ── Banner de sesión ──────────────────────────────────────────────────
        self._build_banner_sesion(cuerpo)

        # ── Card de carga ─────────────────────────────────────────────────────
        card = ctk.CTkFrame(
            cuerpo,
            fg_color=COLORS.bg_card,
            corner_radius=DIMS.card_radius,
            border_width=1,
            border_color=COLORS.border
        )
        card.grid(row=1, column=0, padx=48, pady=24, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)

        # Zona de drop / selección
        zona = ctk.CTkFrame(
            card, fg_color=COLORS.bg_main,
            corner_radius=8,
            border_width=2,
            border_color=COLORS.border
        )
        zona.grid(row=0, column=0, padx=32, pady=32, sticky="nsew")
        zona.grid_columnconfigure(0, weight=1)
        zona.grid_rowconfigure(0, weight=1)

        inner = ctk.CTkFrame(zona, fg_color="transparent")
        inner.grid(row=0, column=0)

        # Ícono carpeta
        ctk.CTkLabel(
            inner,
            text="📁",
            font=(FONTS.family, 48)
        ).pack(pady=(32, 8))

        ctk.CTkLabel(
            inner,
            text="Selecciona el archivo Excel con tus datos",
            font=(FONTS.family, FONTS.size_md, "bold"),
            text_color=COLORS.primary
        ).pack()

        ctk.CTkLabel(
            inner,
            text="El archivo debe tener la hoja 'Periodo_Analisis' con tus datos.",
            font=(FONTS.family, FONTS.size_sm),
            text_color=COLORS.text_secondary
        ).pack(pady=(4, 20))

        ctk.CTkButton(
            inner,
            text="Seleccionar archivo Excel",
            font=(FONTS.family, FONTS.size_sm, "bold"),
            fg_color=COLORS.primary,
            text_color=COLORS.text_white,
            hover_color=COLORS.primary_dark,
            corner_radius=DIMS.button_radius,
            height=40,
            width=220,
            command=self._seleccionar_archivo
        ).pack(pady=(0, 32))

        # Label de estado del archivo
        self.lbl_archivo = ctk.CTkLabel(
            card,
            text="Ningún archivo cargado",
            font=(FONTS.family, FONTS.size_sm),
            text_color=COLORS.text_secondary
        )
        self.lbl_archivo.grid(row=1, column=0, pady=(0, 8))

        # ── Botón continuar ───────────────────────────────────────────────────
        self.btn_continuar = ctk.CTkButton(
            cuerpo,
            text="Continuar a Análisis Exploratorio →",
            font=(FONTS.family, FONTS.size_md, "bold"),
            fg_color=COLORS.primary,
            text_color=COLORS.text_white,
            hover_color=COLORS.primary_dark,
            corner_radius=DIMS.button_radius,
            height=46,
            state="disabled",
            command=self._continuar
        )
        self.btn_continuar.grid(
            row=2, column=0,
            padx=48, pady=(0, 32),
            sticky="w"
        )

    def _build_banner_sesion(self, parent):
        """Muestra los parámetros de la sesión actual si existen."""
        sesion = self.app.session
        nombre   = sesion.get("proyecto_nombre", "")
        var_dep  = sesion.get("var_dependiente", "")
        f_ini    = sesion.get("fecha_inicio", "")
        f_fin    = sesion.get("fecha_fin", "")

        if not nombre and not var_dep:
            return

        banner = ctk.CTkFrame(
            parent,
            fg_color="#E8F5E9",
            corner_radius=8,
            border_width=1,
            border_color="#A5D6A7"
        )
        banner.grid(row=0, column=0, padx=48, pady=(20, 0), sticky="ew")

        texto = []
        if nombre:
            texto.append(f"Proyecto: {nombre}")
        if var_dep:
            texto.append(f"Consumo: {var_dep}")
        if f_ini and f_fin:
            texto.append(f"Período: {f_ini} — {f_fin}")

        ctk.CTkLabel(
            banner,
            text="  |  ".join(texto),
            font=(FONTS.family, FONTS.size_sm),
            text_color=COLORS.success
        ).pack(padx=16, pady=10)

    # ── Lógica ────────────────────────────────────────────────────────────────
    def _seleccionar_archivo(self):
        path = filedialog.askopenfilename(
            title="Seleccionar archivo Excel exploratorio",
            filetypes=[("Excel", "*.xlsx *.xls")]
        )
        if not path:
            return

        self.archivo_path = path
        nombre_archivo = os.path.basename(path)

        self.lbl_archivo.configure(
            text=f"✅  {nombre_archivo}",
            text_color=COLORS.success
        )
        self.btn_continuar.configure(state="normal")
        self.app.session["excel_path"] = path

    def _continuar(self):
        if not self.archivo_path:
            messagebox.showwarning(
                "Sin archivo",
                "Primero selecciona un archivo Excel."
            )
            return

        # Leer y validar el Excel
        from core.io_excel import leer_excel_exploratorio
        df, meta, errores = leer_excel_exploratorio(self.archivo_path)

        # Errores críticos
        if df is None:
            messagebox.showerror(
                "Error al leer archivo",
                "\n".join(errores)
            )
            return

        # Advertencias no críticas
        if errores:
            continuar = messagebox.askyesno(
                "Advertencias encontradas",
                "Se encontraron los siguientes problemas:\n\n" +
                "\n".join(f"• {e}" for e in errores) +
                "\n\n¿Deseas continuar de todas formas?"
            )
            if not continuar:
                return

        # Guardar en sesión
        self.app.session["df_datos"]        = df
        self.app.session["var_dependiente"] = meta.get("var_dep", "")
        self.app.session["vars_independientes"] = meta.get("vars_ind", [])

        self.app.navegar("exploratorio_resultados")
```

### exploratorio_config.py

```python
"""
ui/pages/exploratorio_config.py
================================
Pantalla de configuración del análisis exploratorio.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from ui.theme import COLORS, FONTS, DIMS
from ui.components import SelectorFecha


class ExploratorioConfigPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        self.vars_independientes = []  # lista de CTkEntry dinámicas
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_topbar()
        self._build_cuerpo()

    # ── Topbar ────────────────────────────────────────────────────────────────
    def _build_topbar(self):
        topbar = ctk.CTkFrame(
            self, fg_color=COLORS.bg_card,
            corner_radius=0, height=DIMS.topbar_height
        )
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)

        # Línea acento inferior
        ctk.CTkFrame(
            topbar, fg_color=COLORS.accent,
            height=2, corner_radius=0
        ).place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        # Botón regresar
        ctk.CTkButton(
            topbar,
            text="← Inicio",
            font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent",
            text_color=COLORS.primary,
            hover_color=COLORS.bg_main,
            width=90, height=32,
            corner_radius=DIMS.button_radius,
            command=lambda: self.app.navegar("home")
        ).grid(row=0, column=0, padx=16, pady=8, sticky="w")

        # Título
        ctk.CTkLabel(
            topbar,
            text="Análisis Exploratorio — Nuevo Proyecto",
            font=(FONTS.family, FONTS.size_md, "bold"),
            text_color=COLORS.primary
        ).grid(row=0, column=1, sticky="w", padx=8)

        # Botón ya tengo archivo
        ctk.CTkButton(
            topbar,
            text="🚀 Ya tengo archivo → Cargar datos",
            font=(FONTS.family, FONTS.size_sm),
            fg_color=COLORS.primary,
            text_color=COLORS.text_white,
            hover_color=COLORS.primary_dark,
            corner_radius=DIMS.button_radius,
            height=32,
            command=lambda: self.app.navegar("exploratorio_carga")
        ).grid(row=0, column=2, padx=16, pady=8, sticky="e")

    # ── Cuerpo scrollable ─────────────────────────────────────────────────────
    def _build_cuerpo(self):
        scroll = ctk.CTkScrollableFrame(
            self, fg_color=COLORS.bg_main, corner_radius=0
        )
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # Card principal
        card = ctk.CTkFrame(
            scroll, fg_color=COLORS.bg_card,
            corner_radius=DIMS.card_radius,
            border_width=1, border_color=COLORS.border
        )
        card.grid(row=0, column=0, padx=48, pady=24, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        pad = {"padx": DIMS.padding_card, "pady": (0, 16)}

        # ── Nombre del proyecto ───────────────────────────────────────────────
        self._seccion_label(card, "Nombre del proyecto")
        self.entry_nombre = self._entry(
            card, placeholder="Ej: Edificio"
        )
        self.entry_nombre.grid(row=2, column=0, sticky="ew", **pad)

        # ── Periodo de análisis ───────────────────────────────────────────────
        self._seccion_label(card, "Periodo de análisis", row=3)

        fechas_frame = ctk.CTkFrame(card, fg_color="transparent")
        fechas_frame.grid(row=4, column=0, sticky="ew", **pad)
        fechas_frame.grid_columnconfigure((0, 1), weight=1)

        # Fecha inicio
        self.sel_fecha_ini = SelectorFecha(
            fechas_frame, label_text="Fecha inicio", 
            command=self._actualizar_resumen_fechas
        )
        self.sel_fecha_ini.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        # Fecha fin
        self.sel_fecha_fin = SelectorFecha(
            fechas_frame, label_text="Fecha fin",
            command=self._actualizar_resumen_fechas
        )
        self.sel_fecha_fin.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        # Etiqueta de resumen (debajo de las fechas)
        self.lbl_resumen_fechas = ctk.CTkLabel(
            card, text="",
            font=(FONTS.family, FONTS.size_xs, "italic"),
            text_color=COLORS.success, anchor="w"
        )
        self.lbl_resumen_fechas.grid(row=5, column=0, sticky="w", padx=DIMS.padding_card, pady=(0, 16))
        
        # Inicializar resumen
        self._actualizar_resumen_fechas()

        # ── Variable dependiente ──────────────────────────────────────────────
        self._seccion_label(card, "Variable dependiente (consumo)", row=6)

        ctk.CTkLabel(
            card,
            text="Debe coincidir exactamente con el encabezado en la factura.",
            font=(FONTS.family, FONTS.size_xs),
            text_color=COLORS.text_secondary, anchor="w"
        ).grid(row=6, column=0, sticky="w", padx=DIMS.padding_card, pady=(0, 4))

        self.entry_var_dep = self._entry(
            card, placeholder="Ej: Consumo_kWh"
        )
        self.entry_var_dep.grid(row=8, column=0, sticky="ew", **pad)

        # ── Variables independientes ──────────────────────────────────────────
        self._seccion_label(card, "Variables independientes", row=9)

        ctk.CTkLabel(
            card,
            text="Agrega todas las variables que creas que pueden influir "
                 "en el consumo (Ej: Temperatura, Producción).",
            font=(FONTS.family, FONTS.size_xs),
            text_color=COLORS.text_secondary, anchor="w",
            wraplength=700, justify="left"
        ).grid(row=10, column=0, sticky="w",
               padx=DIMS.padding_card, pady=(0, 4))

        # Frame dinámico para variables
        self.vars_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.vars_frame.grid(row=11, column=0, sticky="ew",
                             padx=DIMS.padding_card, pady=0)
        self.vars_frame.grid_columnconfigure(0, weight=1)

        # Cargar la primera por defecto (Truco estético)
        self._agregar_variable()

        # Botón agregar variable
        ctk.CTkButton(
            card,
            text="+ Agregar variable independiente",
            font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent",
            text_color=COLORS.primary,
            hover_color=COLORS.bg_main,
            border_width=1,
            border_color=COLORS.primary,
            corner_radius=DIMS.button_radius,
            height=32,
            command=self._agregar_variable
        ).grid(row=12, column=0, sticky="w",
               padx=DIMS.padding_card, pady=(8, 20))

        # ── Botones de acción ─────────────────────────────────────────────────
        self._build_botones(scroll)

    def _build_botones(self, parent):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="ew", padx=48, pady=(0, 32))
        btn_frame.grid_columnconfigure(1, weight=1)

        # Confirmar + Descargar plantilla
        ctk.CTkButton(
            btn_frame,
            text="📥  Confirmar y descargar plantilla",
            font=(FONTS.family, FONTS.size_md, "bold"),
            fg_color=COLORS.accent,
            text_color=COLORS.primary,
            hover_color="#D4E800",
            corner_radius=DIMS.button_radius,
            height=44,
            command=self._confirmar_y_descargar
        ).grid(row=0, column=0, sticky="w")

    # ── Helpers UI ────────────────────────────────────────────────────────────
    def _seccion_label(self, parent, texto, row=0):
        ctk.CTkLabel(
            parent, text=texto,
            font=(FONTS.family, FONTS.size_sm, "bold"),
            text_color=COLORS.primary, anchor="w"
        ).grid(row=row, column=0, sticky="w",
               padx=DIMS.padding_card, pady=(16, 4))

    def _entry(self, parent, placeholder=""):
        return ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            font=(FONTS.family, FONTS.size_sm),
            fg_color=COLORS.bg_main,
            border_color=COLORS.border,
            text_color=COLORS.text_primary,
            height=38,
            corner_radius=8
        )

    def _agregar_variable(self):
        idx = len(self.vars_independientes) + 1
        fila = ctk.CTkFrame(self.vars_frame, fg_color="transparent")
        fila.grid(row=idx - 1, column=0, sticky="ew", pady=4)
        fila.grid_columnconfigure(0, weight=1)

        entry = ctk.CTkEntry(
            fila,
            placeholder_text=f"Variable {idx} (Ej: Temperatura_C)",
            font=(FONTS.family, FONTS.size_sm),
            fg_color=COLORS.bg_main,
            border_color=COLORS.border,
            text_color=COLORS.text_primary,
            height=38,
            corner_radius=8
        )
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        # Botón eliminar
        ctk.CTkButton(
            fila,
            text="✕",
            font=(FONTS.family, FONTS.size_sm),
            fg_color=COLORS.danger,
            text_color="white",
            hover_color="#C0392B",
            width=36, height=38,
            corner_radius=8,
            command=lambda f=fila, e=entry: self._eliminar_variable(f, e)
        ).grid(row=0, column=1)

        self.vars_independientes.append(entry)

    def _eliminar_variable(self, fila, entry):
        self.vars_independientes.remove(entry)
        fila.destroy()

    # ── Lógica de confirmación ────────────────────────────────────────────────
    def _confirmar_y_descargar(self):
        nombre    = self.entry_nombre.get().strip()
        fecha_ini = self.sel_fecha_ini.get_value()
        fecha_fin = self.sel_fecha_fin.get_value()
        var_dep   = self.entry_var_dep.get().strip()
        vars_ind  = [e.get().strip() for e in self.vars_independientes
                     if e.get().strip()]

        # Validaciones
        if not nombre:
            messagebox.showwarning("Campo requerido",
                                   "Ingresa el nombre del proyecto.")
            return
        if not self._validar_orden_fechas(fecha_ini, fecha_fin):
            messagebox.showerror("Rango inválido",
                                 "La fecha de fin debe ser posterior a la de inicio.")
            return
        if not var_dep:
            messagebox.showwarning("Campo requerido",
                                   "Ingresa el nombre de la variable dependiente.")
            return

        # Guardar en sesión
        self.app.session["proyecto_nombre"]    = nombre
        self.app.session["fecha_inicio"]       = fecha_ini
        self.app.session["fecha_fin"]          = fecha_fin
        self.app.session["var_dependiente"]    = var_dep
        self.app.session["vars_independientes"] = vars_ind

        # Generar y descargar plantilla
        from core.io_excel import generar_plantilla_exploratoria
        generar_plantilla_exploratoria(
            nombre_proyecto = nombre,
            fecha_ini       = fecha_ini,
            fecha_fin       = fecha_fin,
            var_dep         = var_dep,
            vars_ind        = vars_ind
        )

    def _actualizar_resumen_fechas(self):
        """Calcula meses entre fechas y actualiza el label de resumen."""
        f1 = self.sel_fecha_ini.get_value()
        f2 = self.sel_fecha_fin.get_value()
        
        try:
            d1 = datetime.strptime(f1, "%m/%Y")
            d2 = datetime.strptime(f2, "%m/%Y")
            
            # Cálculo de meses
            meses = (d2.year - d1.year) * 12 + (d2.month - d1.month) + 1
            
            # Formateo nombres cortos para el label
            meses_abr = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
            f1_txt = f"{meses_abr[d1.month-1]}-{d1.year}"
            f2_txt = f"{meses_abr[d2.month-1]}-{d2.year}"
            
            if meses > 0:
                self.lbl_resumen_fechas.configure(
                    text=f"✓ {f1_txt} → {f2_txt} ({meses} meses)",
                    text_color=COLORS.success
                )
            else:
                self.lbl_resumen_fechas.configure(
                    text="✕ Fecha fin debe ser posterior a inicio",
                    text_color=COLORS.danger
                )
        except:
            pass

    def _validar_orden_fechas(self, f1_str, f2_str):
        try:
            d1 = datetime.strptime(f1_str, "%m/%Y")
            d2 = datetime.strptime(f2_str, "%m/%Y")
            return d2 >= d1
        except:
            return False
```

### exploratorio_resultados.py

```python
"""
ui/pages/exploratorio_resultados.py
=====================================
Pantalla de resultados del análisis exploratorio.
Muestra: recomendación, diagnóstico avanzado, tabla Pearson, scatters, sincronía temporal.
"""

import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os
from PIL import Image
from ui.theme import COLORS, FONTS, DIMS


class ExploratorioResultadosPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        self._resultados    = None
        self._recomendacion = None
        self._diagnostico   = None
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_topbar()
        self._calcular()
        self._build_cuerpo()

    # ── Topbar ────────────────────────────────────────────────────────────────
    def _build_topbar(self):
        topbar = ctk.CTkFrame(
            self, fg_color=COLORS.bg_card,
            corner_radius=0, height=DIMS.topbar_height
        )
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)

        ctk.CTkFrame(
            topbar, fg_color=COLORS.accent,
            height=2, corner_radius=0
        ).place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        ctk.CTkButton(
            topbar,
            text="← Datos",
            font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent",
            text_color=COLORS.primary,
            hover_color=COLORS.bg_main,
            width=80, height=32,
            corner_radius=DIMS.button_radius,
            command=lambda: self.app.navegar("exploratorio_carga")
        ).grid(row=0, column=0, padx=16, pady=8, sticky="w")

        ctk.CTkLabel(
            topbar,
            text="Análisis Exploratorio de Datos",
            font=(FONTS.family, FONTS.size_md, "bold"),
            text_color=COLORS.primary
        ).grid(row=0, column=1, sticky="w", padx=8)

        ctk.CTkButton(
            topbar,
            text="🏠 Inicio",
            font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent",
            text_color=COLORS.primary,
            hover_color=COLORS.bg_main,
            width=80, height=32,
            corner_radius=DIMS.button_radius,
            command=lambda: self.app.navegar("home")
        ).grid(row=0, column=2, padx=16, pady=8, sticky="e")

    # ── Cálculos ──────────────────────────────────────────────────────────────
    def _calcular(self):
        from core.exploratorio import calcular_correlaciones, recomendar_modelo, obtener_diagnostico_avanzado
        sesion   = self.app.session
        df       = sesion.get("df_datos")
        var_dep  = sesion.get("var_dependiente", "")
        vars_ind = sesion.get("vars_independientes", [])

        if df is None or not var_dep:
            return

        self._resultados    = calcular_correlaciones(df, var_dep, vars_ind)
        self._recomendacion = recomendar_modelo(self._resultados)
        self._diagnostico   = obtener_diagnostico_avanzado(df, var_dep, vars_ind)

        # Guardar en sesión
        sesion["resultados_exploratorio"] = {
            "correlaciones":  self._resultados,
            "recomendacion":  self._recomendacion,
            "diagnostico":    self._diagnostico
        }

    # ── Cuerpo scrollable ─────────────────────────────────────────────────────
    def _build_cuerpo(self):
        self.scroll = ctk.CTkScrollableFrame(
            self, fg_color=COLORS.bg_main, corner_radius=0
        )
        self.scroll.grid(row=1, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

        fila = 0

        # 1 — Card recomendación
        self._build_card_recomendacion(self.scroll, fila)
        fila += 1

        # 1.5 — Card Diagnóstico Avanzado
        self._build_card_diagnostico(self.scroll, fila)
        fila += 1

        # 2 — Card tabla Pearson
        self._build_card_tabla(self.scroll, fila)
        fila += 1

        # 3 — Scatters por variable
        self._build_scatters(self.scroll, fila)
        fila += 1

        # 4 — Sincronía temporal
        self._build_sincronia(self.scroll, fila)
        fila += 1

        # 4.5 — Guía de interpretación (Glosario)
        self._build_glosario(self.scroll, fila)
        fila += 1

        # 5 — Botones de acción
        self._build_botones(self.scroll, fila)

    # ── Card recomendación ────────────────────────────────────────────────────
    def _build_card_recomendacion(self, parent, fila):
        if not self._recomendacion:
            return

        rec = self._recomendacion
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS.primary,
            corner_radius=DIMS.card_radius
        )
        card.grid(row=fila, column=0, padx=48, pady=(24, 8), sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        icon_map = {"M1": "m1_icon.png", "M2": "m2_icon.png", "M3": "m3_icon.png"}
        icon_path = os.path.join("assets", icon_map.get(rec["codigo"], "m1_icon.png"))
        
        try:
            pil_img = Image.open(icon_path)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(48, 48))
            ctk.CTkLabel(card, text="", image=ctk_img).grid(row=0, column=0, rowspan=2, padx=20, pady=20)
        except:
            ctk.CTkLabel(card, text="📊", font=(FONTS.family, 36), text_color=COLORS.accent).grid(row=0, column=0, rowspan=2, padx=20, pady=20)

        ctk.CTkLabel(
            card,
            text=rec["titulo"],
            font=(FONTS.family, FONTS.size_xl, "bold"),
            text_color=COLORS.text_white,
            anchor="w"
        ).grid(row=0, column=1, sticky="w", padx=(0, 20), pady=(20, 4))

        ctk.CTkLabel(
            card,
            text="Recomendación del Sistema",
            font=(FONTS.family, FONTS.size_xs, "bold"),
            text_color=COLORS.accent,
            anchor="w"
        ).grid(row=0, column=2, sticky="e", padx=20, pady=(20, 4))

        ctk.CTkLabel(
            card,
            text=rec["justificacion"],
            font=(FONTS.family, FONTS.size_sm),
            text_color="#A8C4BC",
            anchor="w",
            wraplength=700,
            justify="left"
        ).grid(row=1, column=1, columnspan=2,
               sticky="w", padx=(0, 20), pady=(0, 20))

    # ── Card Diagnóstico ──────────────────────────────────────────────────────
    def _build_card_diagnostico(self, parent, fila):
        if not self._diagnostico:
            return
        
        diag = self._diagnostico
        card = self._card(parent, fila, "🔍  Calidad y Diagnóstico de los Datos")
        
        container = ctk.CTkFrame(card, fg_color="transparent")
        container.pack(fill="x", padx=16, pady=(0, 16))
        container.grid_columnconfigure((0, 1, 2), weight=1)

        # --- A. OUTLIERS ---
        out = diag["outliers"]
        color_out = COLORS.danger if out["conteo"] > 0 else COLORS.success
        f_out = ctk.CTkFrame(container, fg_color=COLORS.bg_main, corner_radius=8, border_width=1, border_color=color_out)
        f_out.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        
        ctk.CTkLabel(f_out, text="Calidad de Datos", font=(FONTS.family, FONTS.size_xs, "bold"), text_color=COLORS.primary).pack(pady=(8, 2))
        if out["conteo"] > 0:
            msg = f"Se detectaron {out['conteo']} anomalías.\nEl consumo presenta picos fuera de lo común."
            ctk.CTkLabel(f_out, text="ALERTA", font=(FONTS.family, 10, "bold"), text_color=COLORS.danger).pack()
            ctk.CTkLabel(f_out, text=msg, font=(FONTS.family, 11), text_color=COLORS.text_primary, wraplength=200).pack(padx=10, pady=(4, 8))
        else:
            ctk.CTkLabel(f_out, text="Datos Limpios", font=(FONTS.family, 10, "bold"), text_color=COLORS.success).pack()
            ctk.CTkLabel(f_out, text="No se detectaron valores inusuales en el periodo.", font=(FONTS.family, 11), text_color=COLORS.text_secondary, wraplength=200).pack(padx=10, pady=(4, 8))

        # --- B. REDUNDANCIA ---
        colin = diag["colinealidad"]
        color_col = COLORS.warning if colin else COLORS.success
        f_col = ctk.CTkFrame(container, fg_color=COLORS.bg_main, corner_radius=8, border_width=1, border_color=color_col)
        f_col.grid(row=0, column=1, padx=4, sticky="nsew")

        ctk.CTkLabel(f_col, text="Independencia", font=(FONTS.family, FONTS.size_xs, "bold"), text_color=COLORS.primary).pack(pady=(8, 2))
        if colin:
            msg = colin[0]["mensaje"]
            ctk.CTkLabel(f_col, text="REDUNDANCIA", font=(FONTS.family, 10, "bold"), text_color=COLORS.warning).pack()
            ctk.CTkLabel(f_col, text=msg, font=(FONTS.family, 11), text_color=COLORS.text_primary, wraplength=200).pack(padx=10, pady=(4, 8))
        else:
            ctk.CTkLabel(f_col, text="Óptima", font=(FONTS.family, 10, "bold"), text_color=COLORS.success).pack()
            ctk.CTkLabel(f_col, text="Las variables aportan información única y valiosa.", font=(FONTS.family, 11), text_color=COLORS.text_secondary, wraplength=200).pack(padx=10, pady=(4, 8))

        # --- C. COMPORTAMIENTO ESTACIONAL DEL CONSUMO ---
        est = diag["estacionalidad"]
        f_est = ctk.CTkFrame(container, fg_color=COLORS.bg_main, corner_radius=8, border_width=1, border_color=COLORS.primary)
        f_est.grid(row=0, column=2, padx=(8, 0), sticky="nsew")

        ctk.CTkLabel(f_est, text="Patrón del Consumo", font=(FONTS.family, FONTS.size_xs, "bold"), text_color=COLORS.primary).pack(pady=(8, 2))
        if est and est["tipo"] != "N/D":
            ctk.CTkLabel(f_est, text=est["tipo"].upper(), font=(FONTS.family, 10, "bold"), text_color=COLORS.primary).pack()
            
            tendencia = est.get("tendencia", {}).get("clase", "Estable")
            msg = f"Tendencia a largo plazo: {tendencia}\nPeriodo Pico: {est['pico']}\nPeriodo Valle: {est['valle']}"
            ctk.CTkLabel(f_est, text=msg, font=(FONTS.family, 11), text_color=COLORS.text_primary, wraplength=200, justify="left").pack(padx=10, pady=(4, 8))
        else:
            ctk.CTkLabel(f_est, text="No detectado", font=(FONTS.family, 10, "bold"), text_color=COLORS.text_secondary).pack()
            ctk.CTkLabel(f_est, text="Datos insuficientes para análisis estacional.", font=(FONTS.family, 11), text_color=COLORS.text_secondary, wraplength=200).pack(padx=10, pady=(4, 8))

    def _build_glosario(self, parent, fila):
        card = ctk.CTkFrame(parent, fg_color="transparent")
        card.grid(row=fila, column=0, padx=48, pady=(8, 24), sticky="ew")
        
        lbl = ctk.CTkLabel(
            card, text="📖  Guía de Interpretación de Resultados",
            font=(FONTS.family, FONTS.size_sm, "bold"),
            text_color=COLORS.text_secondary
        )
        lbl.pack(anchor="w", pady=(0, 8))

        texto_ayuda = (
            "• Estacionalidad Estable: El consumo es constante; ningún mes varía más del 15% del promedio anual.\n"
            "• Ciclos (Uni/Bimodal): Indican 1 o 2 periodos de alta demanda al año (estacionalidad clara).\n"
            "• Tendencia a largo plazo: Indica si el edificio está aumentando o disminuyendo su carga base con el tiempo.\n"
            "• Sincronía: Cuantifica qué tan parecidas son las formas de las curvas. Si es Alta Inversa, cuando una sube la otra siempre baja."
        )

        ctk.CTkLabel(
            card, text=texto_ayuda,
            font=(FONTS.family, 11),
            text_color=COLORS.text_secondary,
            justify="left", anchor="w"
        ).pack(anchor="w", padx=10)

    # ── Card tabla Pearson ────────────────────────────────────────────────────
    def _build_card_tabla(self, parent, fila):
        if not self._resultados:
            return

        card = self._card(parent, fila, "🔗  Influencia de las Variables (Pearson)")

        # Encabezados
        cols = ["Variable Independiente", "r (Pearson)",
                "p-valor", "¿Significativa?", "Grado", "Interpretación"]
        anchos = [180, 90, 90, 110, 120, 0]

        enc = ctk.CTkFrame(card, fg_color=COLORS.primary, corner_radius=6)
        enc.pack(fill="x", padx=16, pady=(0, 4))

        for ci, (col, ancho) in enumerate(zip(cols, anchos)):
            enc.grid_columnconfigure(ci, weight=1 if ancho == 0 else 0,
                                     minsize=ancho)
            ctk.CTkLabel(
                enc, text=col,
                font=(FONTS.family, FONTS.size_xs, "bold"),
                text_color="white", anchor="center"
            ).grid(row=0, column=ci, sticky="ew", padx=6, pady=8)

        # Filas
        for ri, res in enumerate(self._resultados):
            bg = COLORS.bg_main if ri % 2 == 0 else COLORS.bg_card
            fila_frame = ctk.CTkFrame(card, fg_color=bg, corner_radius=0)
            fila_frame.pack(fill="x", padx=16, pady=1)

            for ci, ancho in enumerate(anchos):
                fila_frame.grid_columnconfigure(
                    ci, weight=1 if ancho == 0 else 0, minsize=ancho
                )

            ctk.CTkLabel(fila_frame, text=res["variable"], font=(FONTS.family, FONTS.size_xs, "bold"), text_color=COLORS.primary, anchor="center").grid(row=0, column=0, sticky="ew", padx=6, pady=6)

            r_val = res["r_pearson"]
            r_txt = f"{r_val:+.4f}" if r_val is not None else "—"
            r_color = self._color_r(r_val)
            ctk.CTkLabel(fila_frame, text=r_txt, font=(FONTS.family_mono, FONTS.size_xs, "bold"), text_color=r_color, anchor="center").grid(row=0, column=1, sticky="ew", padx=6, pady=6)

            p_val = res["p_valor"]
            p_txt = f"{p_val:.4f}" if p_val is not None else "—"
            p_color = COLORS.success if res["significativa"] else COLORS.danger
            ctk.CTkLabel(fila_frame, text=p_txt, font=(FONTS.family_mono, FONTS.size_xs), text_color=p_color, anchor="center").grid(row=0, column=2, sticky="ew", padx=6, pady=6)

            sig_txt   = "✅ Sí" if res["significativa"] else "❌ No"
            sig_color = COLORS.success if res["significativa"] else COLORS.danger
            ctk.CTkLabel(fila_frame, text=sig_txt, font=(FONTS.family, FONTS.size_xs, "bold"), text_color=sig_color, anchor="center").grid(row=0, column=3, sticky="ew", padx=6, pady=6)

            ctk.CTkLabel(fila_frame, text=res["grado"], font=(FONTS.family, FONTS.size_xs), text_color=COLORS.text_secondary, anchor="center").grid(row=0, column=4, sticky="ew", padx=6, pady=6)
            ctk.CTkLabel(fila_frame, text=res["interpretacion"], font=(FONTS.family, FONTS.size_xs), text_color=COLORS.text_primary, anchor="w", wraplength=300, justify="left").grid(row=0, column=5, sticky="ew", padx=6, pady=6)

        ctk.CTkFrame(card, fg_color="transparent", height=12).pack()

    # ── Scatters ──────────────────────────────────────────────────────────────
    def _build_scatters(self, parent, fila):
        sesion   = self.app.session
        df       = sesion.get("df_datos")
        var_dep  = sesion.get("var_dependiente", "")
        vars_ind = sesion.get("vars_independientes", [])

        if df is None or not vars_ind:
            return

        from core.exploratorio import preparar_datos_scatter

        card = self._card(parent, fila, "📊  Análisis de Dispersión y Proporcionalidad")

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=16, pady=(0, 16))
        grid.grid_columnconfigure((0, 1), weight=1)

        for idx, var in enumerate(vars_ind):
            datos = preparar_datos_scatter(df, var_dep, var)
            col   = idx % 2
            row   = idx // 2

            fig = self._crear_scatter(datos, var_dep, var)
            canvas_frame = ctk.CTkFrame(grid, fg_color=COLORS.bg_card, corner_radius=8, border_width=1, border_color=COLORS.border)
            canvas_frame.grid(row=row, column=col, padx=(0, 8) if col == 0 else 0, pady=8, sticky="nsew")
            canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
            plt.close(fig)

    def _crear_scatter(self, datos, var_dep, var_ind):
        fig, ax = plt.subplots(figsize=(5, 3.5))
        fig.patch.set_facecolor(COLORS.bg_card)
        ax.set_facecolor("#F8FAF9")
        ax.scatter(datos["x"], datos["y"], color=COLORS.primary, alpha=0.7, s=50, zorder=3, edgecolors="white", linewidths=0.5)
        if len(datos["x_trend"]) > 0:
            ax.plot(datos["x_trend"], datos["y_trend"], color=COLORS.accent, linewidth=2, linestyle="--", zorder=2)
        ax.set_xlabel(var_ind, fontsize=9, color=COLORS.text_secondary)
        ax.set_ylabel(var_dep, fontsize=9, color=COLORS.text_secondary)
        titulo = f"Dispersión: {var_dep} vs {var_ind}"
        if datos["r"] is not None:
            sig = "✓ sig." if (datos["p_valor"] < 0.05) else "✗ no sig."
            titulo += f"\nr = {datos['r']:+.3f}  |  p = {datos['p_valor']:.4f}  |  {sig}"
        ax.set_title(titulo, fontsize=8.5, color=COLORS.primary, fontweight="bold", pad=10)
        ax.tick_params(colors=COLORS.text_secondary, labelsize=8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_color(COLORS.border)
        ax.grid(True, alpha=0.3, color=COLORS.border)
        fig.tight_layout()
        return fig

    # ── Sincronía temporal ────────────────────────────────────────────────────
    def _build_sincronia(self, parent, fila):
        sesion   = self.app.session
        df       = sesion.get("df_datos")
        var_dep  = sesion.get("var_dependiente", "")
        vars_ind = sesion.get("vars_independientes", [])

        if df is None: return

        from core.exploratorio import preparar_datos_sincronia, calcular_puntajes_sincronia
        datos = preparar_datos_sincronia(df, var_dep, vars_ind)
        # Diagnóstico de sincronía basado en Pearson
        diagnosticos = calcular_puntajes_sincronia(self._resultados if self._resultados else [])

        card = self._card(parent, fila, "📈  Sincronía Temporal (Consumo vs Variables)")

        fig = self._crear_sincronia(datos, var_dep)
        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=(0, 4))
        plt.close(fig)

        # NOTA EXPLICATIVA + PUNTAJES
        insight_frame = ctk.CTkFrame(card, fg_color=COLORS.bg_main, corner_radius=8)
        insight_frame.pack(fill="x", padx=16, pady=(0, 16))
        
        ctk.CTkLabel(
            insight_frame,
            text="💡 Guía Visual: Observa si el consumo y las variables suben y bajan al mismo tiempo (Directa) o en sentido contrario (Inversa).",
            font=(FONTS.family, FONTS.size_xs, "bold"),
            text_color=COLORS.primary, anchor="w", wraplength=700, justify="left"
        ).pack(padx=12, pady=(8, 4), anchor="w")

        resumen_sync = []
        for var, d in diagnosticos.items():
            if var == var_dep: continue
            resumen_sync.append(f"• {var}: {d['porcentaje']}% de sincronía — {d['mensaje']}")
        
        txt_sync = "\n".join(resumen_sync) if resumen_sync else "No hay variables para comparar."
        
        ctk.CTkLabel(
            insight_frame, text=txt_sync, font=(FONTS.family, FONTS.size_xs),
            text_color=COLORS.text_primary, justify="left", anchor="w"
        ).pack(padx=12, pady=(0, 12), anchor="w")

    def _crear_sincronia(self, datos, var_dep):
        fechas = datos["fechas"]
        series = datos["series"]
        n      = len(fechas)
        fig, ax = plt.subplots(figsize=(11, 3.5))
        fig.patch.set_facecolor(COLORS.bg_card)
        ax.set_facecolor("#F8FAF9")
        colores = [COLORS.primary, COLORS.accent, "#E63946", "#F4A261", "#2D6A4F", "#457B9D"]
        for idx, (nombre, valores) in enumerate(series.items()):
            color  = colores[idx % len(colores)]
            estilo = "-" if nombre == var_dep else "--"
            grosor = 2.5 if nombre == var_dep else 1.5
            ax.plot(range(n), valores, color=color, linewidth=grosor, linestyle=estilo, label=nombre, zorder=3)
        paso = max(1, n // 12)
        ax.set_xticks(range(0, n, paso))
        ax.set_xticklabels([fechas[i] for i in range(0, n, paso)], rotation=45, ha="right", fontsize=7, color=COLORS.text_secondary)
        ax.set_ylabel("Valor normalizado (0–1)", fontsize=9, color=COLORS.text_secondary)
        ax.set_title("Comparativa de Comportamientos Temporales (Normalizados)", fontsize=9, color=COLORS.primary, fontweight="bold")
        ax.legend(fontsize=8, loc="upper right", framealpha=0.9, edgecolor=COLORS.border)
        ax.tick_params(colors=COLORS.text_secondary, labelsize=8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_color(COLORS.border)
        ax.grid(True, alpha=0.3, color=COLORS.border)
        fig.tight_layout()
        return fig

    # ── Botones ───────────────────────────────────────────────────────────────
    def _build_botones(self, parent, fila):
        frame = ctk.CTkFrame(parent, fg_color=COLORS.bg_card, corner_radius=0, height=70)
        frame.grid(row=fila, column=0, sticky="ew", padx=0, pady=(8, 0))
        frame.grid_propagate(False)
        frame.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(frame, text="📊  Actualizar informe en Excel", font=(FONTS.family, FONTS.size_sm, "bold"), fg_color=COLORS.accent, text_color=COLORS.primary, hover_color="#D4E800", corner_radius=DIMS.button_radius, height=40, command=self._actualizar_excel).grid(row=0, column=0, padx=24, pady=15, sticky="w")
        ctk.CTkButton(frame, text="Continuar a selección de modelo →", font=(FONTS.family, FONTS.size_sm, "bold"), fg_color=COLORS.primary, text_color=COLORS.text_white, hover_color=COLORS.primary_dark, corner_radius=DIMS.button_radius, height=40, command=lambda: self.app.navegar("seleccion_modelo")).grid(row=0, column=2, padx=24, pady=15, sticky="e")

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _actualizar_excel(self):
        from core.io_excel import escribir_resultados_exploratorios
        sesion = self.app.session
        if self._resultados is None: return
        path = sesion.get("excel_path")
        if not path:
            from tkinter import filedialog
            path = filedialog.askopenfilename(title="Seleccionar Excel", filetypes=[("Excel", "*.xlsx")])
        if not path: return
        ok = escribir_resultados_exploratorios(path=path, recomendacion=self._recomendacion["titulo"], justificacion=self._recomendacion["justificacion"], tabla_resultados=self._resultados)
        if ok: messagebox.showinfo("Éxito", f"Excel actualizado en:\n{path}")

    def _card(self, parent, fila, titulo):
        card = ctk.CTkFrame(parent, fg_color=COLORS.bg_card, corner_radius=DIMS.card_radius, border_width=1, border_color=COLORS.border)
        card.grid(row=fila, column=0, padx=48, pady=8, sticky="ew")
        card.grid_columnconfigure(0, weight=1)
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(14, 10))
        ctk.CTkFrame(header, fg_color=COLORS.accent, width=4, corner_radius=2).pack(side="left", fill="y", padx=(0, 10))
        ctk.CTkLabel(header, text=titulo, font=(FONTS.family, FONTS.size_sm, "bold"), text_color=COLORS.primary, anchor="w").pack(side="left")
        return card

    def _color_r(self, r):
        if r is None: return COLORS.text_secondary
        r_abs = abs(r)
        if r_abs >= 0.70: return COLORS.success
        elif r_abs >= 0.50: return COLORS.warning
        return COLORS.danger
```

### home.py

```python
"""
ui/pages/home.py
================
Pantalla de bienvenida — Hub principal de navegación.
"""

import customtkinter as ctk
from PIL import Image
import os
from ui.theme import COLORS, FONTS, DIMS


class HomePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=0)  # sidebar
        self.grid_columnconfigure(1, weight=1)  # contenido
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_contenido()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(
            self,
            fg_color=COLORS.bg_sidebar,
            width=DIMS.sidebar_width,
            corner_radius=0
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        
        # Espaciador superior para centrar verticalmente
        ctk.CTkFrame(sidebar, fg_color="transparent", height=1).pack(expand=True)

        # Contenedor de contenido
        cnt = ctk.CTkFrame(sidebar, fg_color="transparent")
        cnt.pack(fill="x")

        # Logo
        logo_path = os.path.join("assets", "logo_lben.png")
        if os.path.exists(logo_path):
            img = ctk.CTkImage(light_image=Image.open(logo_path),
                               dark_image=Image.open(logo_path),
                               size=(130, 130))
            ctk.CTkLabel(cnt, image=img, text="").pack(pady=(0, 20))
        else:
            ctk.CTkLabel(cnt, text="⚡", font=(FONTS.family, 42), text_color=COLORS.accent).pack(pady=(0, 20))

        # Textos
        ctk.CTkLabel(
            cnt, text="Línea Base\nEnergética",
            font=(FONTS.family, FONTS.size_lg, "bold"),
            text_color=COLORS.text_white, justify="center"
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            cnt, text="Resolución UPME\n016 de 2024",
            font=(FONTS.family, FONTS.size_xs),
            text_color="#7A9B8E", justify="center"
        ).pack(pady=(0, 24))

        # Separador
        ctk.CTkFrame(cnt, fg_color="#2D4F45", height=1, width=160).pack(pady=8)

        # Subtítulo
        ctk.CTkLabel(
            cnt, text="Modelos de referencia para\nmonitoreo del\nDesempeño Energético",
            font=(FONTS.family, FONTS.size_xs),
            text_color="#7A9B8E", justify="center", wraplength=180
        ).pack(pady=(16, 0))

        # Espaciador inferior para empujar la versión al fondo
        ctk.CTkFrame(sidebar, fg_color="transparent", height=1).pack(expand=True)

        # Versión
        ctk.CTkLabel(
            sidebar, text="v1.0.0",
            font=(FONTS.family, FONTS.size_xs),
            text_color="#4A6B5E"
        ).pack(side="bottom", pady=16)

    # ── Contenido principal ───────────────────────────────────────────────────
    def _build_contenido(self):
        contenido = ctk.CTkFrame(
            self, fg_color=COLORS.bg_main, corner_radius=0
        )
        contenido.grid(row=0, column=1, sticky="nsew")
        contenido.grid_columnconfigure(0, weight=1)
        contenido.grid_rowconfigure(3, weight=1)

        # ── Header ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(
            contenido, fg_color=COLORS.bg_main, corner_radius=0
        )
        header.grid(row=0, column=0, sticky="ew", padx=48, pady=(40, 0))

        ctk.CTkLabel(
            header,
            text="Bienvenido",
            font=(FONTS.family, FONTS.size_title, "bold"),
            text_color=COLORS.primary
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Esta herramienta permite establecer la línea base y monitorear el desempeño energético en Edificios,\n"
                 "de acuerdo con la Resolución 016 de 2024.",
            font=(FONTS.family, FONTS.size_md),
            text_color=COLORS.text_secondary,
            justify="left"
        ).pack(anchor="w", pady=(6, 0))

        # ── Cards de features ─────────────────────────────────────────────────
        features = ctk.CTkFrame(
            contenido, fg_color=COLORS.bg_main, corner_radius=0
        )
        features.grid(row=1, column=0, sticky="ew", padx=48, pady=(28, 0))

        self._feature_card(features, "📊", "3 Modelos",
                           "Absoluto · Cociente · Métodos Estadísticos", 0)
        self._feature_card(features, "📥", "Hojas de Cálculo",
                           "Descarga y Edita tus Datos", 1)
        self._feature_card(features, "📈", "Gráficos",
                           "Línea base · Desempeño Acum.", 2)

        # ── Rutas principales ─────────────────────────────────────────────────
        rutas = ctk.CTkFrame(
            contenido, fg_color=COLORS.bg_main, corner_radius=0
        )
        rutas.grid(row=2, column=0, sticky="ew", padx=48, pady=(28, 0))
        rutas.grid_columnconfigure((0, 1), weight=1)

        # Card Análisis Exploratorio
        self._ruta_card(
            rutas,
            icono="🔍",
            titulo="Análisis Exploratorio",
            descripcion="No sé qué modelo usar.\nIdentificar variables y recibir\nrecomendación del sistema.",
            boton_texto="Empezar",
            boton_cmd=lambda: self.app.navegar("exploratorio_config"),
            destacado=True,
            col=0
        )

        # Card Modelado Directo
        self._ruta_card(
            rutas,
            icono="📋",
            titulo="Modelado Directo",
            descripcion="Ya sé qué modelo usar.\nIr directo a la configuración\nde un modelo específico.",
            boton_texto="Empezar",
            boton_cmd=lambda: self.app.navegar("seleccion_modelo"),
            destacado=False,
            col=1
        )

        # ── Botón abrir proyecto ──────────────────────────────────────────────
        footer = ctk.CTkFrame(
            contenido, fg_color=COLORS.bg_main, corner_radius=0
        )
        footer.grid(row=3, column=0, sticky="sew", padx=48, pady=(20, 32))
        footer.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            footer,
            text="📂  Abrir Proyecto o Seguimiento Existente",
            font=(FONTS.family, FONTS.size_md),
            fg_color=COLORS.bg_card,
            text_color=COLORS.primary,
            hover_color=COLORS.border,
            border_width=1,
            border_color=COLORS.border,
            corner_radius=DIMS.button_radius,
            height=44,
            command=lambda: self.app.navegar("exploratorio_carga")
        ).grid(row=0, column=0, sticky="ew")

        # Copyright
        ctk.CTkLabel(
            footer,
            text="© 2026 — Herramienta de análisis energético  |  UPME 016/2024",
            font=(FONTS.family, FONTS.size_xs),
            text_color=COLORS.text_secondary
        ).grid(row=1, column=0, pady=(8, 0))

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _feature_card(self, parent, icono, titulo, subtitulo, col):
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS.bg_card,
            corner_radius=DIMS.card_radius,
            border_width=1,
            border_color=COLORS.border
        )
        card.grid(row=0, column=col, padx=(0, 12) if col < 2 else 0,
                  sticky="ew")
        parent.grid_columnconfigure(col, weight=1)

        ctk.CTkLabel(
            card, text=icono,
            font=(FONTS.family, 24)
        ).pack(pady=(16, 4))

        ctk.CTkLabel(
            card, text=titulo,
            font=(FONTS.family, FONTS.size_sm, "bold"),
            text_color=COLORS.primary
        ).pack()

        ctk.CTkLabel(
            card, text=subtitulo,
            font=(FONTS.family, FONTS.size_xs),
            text_color=COLORS.text_secondary
        ).pack(pady=(2, 16))

    def _ruta_card(self, parent, icono, titulo, descripcion,
                   boton_texto, boton_cmd, destacado, col):
        fg = COLORS.primary if destacado else COLORS.bg_card
        txt = COLORS.text_white if destacado else COLORS.primary
        txt2 = "#A8C4BC" if destacado else COLORS.text_secondary
        btn_fg = COLORS.accent if destacado else COLORS.primary
        btn_txt = COLORS.primary if destacado else COLORS.text_white

        card = ctk.CTkFrame(
            parent,
            fg_color=fg,
            corner_radius=DIMS.card_radius,
            border_width=1,
            border_color=COLORS.border
        )
        card.grid(row=0, column=col,
                  padx=(0, 12) if col == 0 else 0,
                  sticky="nsew", pady=4)

        ctk.CTkLabel(
            card, text=icono,
            font=(FONTS.family, 28),
        ).pack(pady=(20, 6))

        ctk.CTkLabel(
            card, text=titulo,
            font=(FONTS.family, FONTS.size_lg, "bold"),
            text_color=txt
        ).pack()

        ctk.CTkLabel(
            card, text=descripcion,
            font=(FONTS.family, FONTS.size_sm),
            text_color=txt2,
            justify="center"
        ).pack(pady=(8, 16), padx=16)

        ctk.CTkButton(
            card,
            text=boton_texto,
            font=(FONTS.family, FONTS.size_sm, "bold"),
            fg_color=btn_fg,
            text_color=btn_txt,
            hover_color=COLORS.accent if not destacado else "#D4E800",
            corner_radius=DIMS.button_radius,
            height=38,
            command=boton_cmd
        ).pack(pady=(0, 20), padx=24, fill="x")
```

### m1.py

```python

```

### m1_carga.py

```python
"""
ui/pages/m1_carga.py
====================
Pantalla de carga y validación de datos para el Modelo M1.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from ui.theme import COLORS, FONTS, DIMS
import pandas as pd

class M1CargaPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        self.df_base = None
        self.df_monitoreo = None
        self.meta = {}
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_topbar()
        self._build_cuerpo()

    def _build_topbar(self):
        topbar = ctk.CTkFrame(self, fg_color=COLORS.bg_card, corner_radius=0, height=DIMS.topbar_height)
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)

        ctk.CTkFrame(topbar, fg_color=COLORS.accent, height=2).place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        ctk.CTkButton(
            topbar, text="← Configuración", font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent", text_color=COLORS.primary, hover_color=COLORS.bg_main,
            width=120, height=32, command=lambda: self.app.navegar("m1_config")
        ).grid(row=0, column=0, padx=16, pady=8, sticky="w")

        ctk.CTkLabel(
            topbar, text="Modelo M1: Carga de Datos",
            font=(FONTS.family, FONTS.size_md, "bold"), text_color=COLORS.primary
        ).grid(row=0, column=1, sticky="w", padx=8)

    def _build_cuerpo(self):
        self.cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        self.cuerpo.grid(row=1, column=0, sticky="nsew", padx=48, pady=24)
        self.cuerpo.grid_columnconfigure(0, weight=1)

        # ── Zona de Carga ─────────────────────────────────────────────────────
        self.zona_carga = ctk.CTkFrame(self.cuerpo, fg_color=COLORS.bg_card, corner_radius=DIMS.card_radius, border_width=1, border_color=COLORS.border)
        self.zona_carga.grid(row=0, column=0, sticky="ew", pady=(0, 24))
        self.zona_carga.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.zona_carga, text="Selecciona el archivo Excel M1 con tus datos",
            font=(FONTS.family, FONTS.size_sm), text_color=COLORS.text_secondary
        ).pack(pady=(20, 10))

        self.btn_seleccionar = ctk.CTkButton(
            self.zona_carga, text="📂 Seleccionar Archivo",
            font=(FONTS.family, FONTS.size_md, "bold"), fg_color=COLORS.primary,
            height=40, command=self._seleccionar_archivo
        )
        self.btn_seleccionar.pack(pady=(0, 20))

        # ── Zona de Resumen (oculta inicialmente) ─────────────────────────────
        self.zona_resumen = ctk.CTkFrame(self.cuerpo, fg_color="transparent")
        self.zona_resumen.grid_columnconfigure((0, 1), weight=1)

    def _seleccionar_archivo(self):
        path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if not path: return

        from core.io_excel import leer_excel_m1
        df_b, df_m, meta, errores = leer_excel_m1(path)

        if errores:
            messagebox.showerror("Errores en el archivo", "\n".join(errores))
            return

        self.df_base = df_b
        self.df_monitoreo = df_m
        self.meta = meta
        self.app.session["excel_path"] = path
        
        self._mostrar_resumen()

    def _mostrar_resumen(self):
        # Limpiar zona resumen
        for widget in self.zona_resumen.winfo_children(): widget.destroy()
        self.zona_resumen.grid(row=1, column=0, sticky="nsew")

        # Card Info Proyecto
        card_info = ctk.CTkFrame(self.zona_resumen, fg_color=COLORS.bg_card, corner_radius=DIMS.card_radius, border_width=1, border_color=COLORS.border)
        card_info.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        
        ctk.CTkLabel(card_info, text="Información del Proyecto", font=(FONTS.family, FONTS.size_sm, "bold"), text_color=COLORS.primary).pack(pady=10)
        
        info_text = (
            f"📍 Entidad: {self.meta.get('entidad', 'N/A')}\n"
            f"⚡ Fuente: {self.meta.get('fuente', 'N/A')}\n"
            f"📏 Unidad: {self.meta.get('unidad', 'N/A')}\n"
            f"📅 Periodo Base: {self.meta.get('periodo_base_text', 'N/A')}"
        )
        ctk.CTkLabel(card_info, text=info_text, justify="left", font=(FONTS.family, FONTS.size_xs), text_color=COLORS.text_primary).pack(padx=20, pady=(0, 20))

        # Card Estadísticas Datos
        card_stats = ctk.CTkFrame(self.zona_resumen, fg_color=COLORS.bg_card, corner_radius=DIMS.card_radius, border_width=1, border_color=COLORS.border)
        card_stats.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        
        ctk.CTkLabel(card_stats, text="Resumen de Datos", font=(FONTS.family, FONTS.size_sm, "bold"), text_color=COLORS.primary).pack(pady=10)
        
        stats_text = (
            f"📊 Registros Periodo Base: {len(self.df_base)}\n"
            f"📈 Registros Monitoreo: {len(self.df_monitoreo)}\n"
            f"✅ Columnas encontradas: {len(self.df_base.columns)}"
        )
        ctk.CTkLabel(card_stats, text=stats_text, justify="left", font=(FONTS.family, FONTS.size_xs), text_color=COLORS.text_primary).pack(padx=20, pady=(0, 20))

        # Botón Procesar
        ctk.CTkButton(
            self.cuerpo, text="⚙️ Calcular Línea Base y Desempeño",
            font=(FONTS.family, FONTS.size_md, "bold"), fg_color=COLORS.accent,
            text_color=COLORS.primary, height=48, command=self._procesar_m1
        ).grid(row=2, column=0, pady=32)

    def _procesar_m1(self):
        # Guardar en sesión para el siguiente paso
        self.app.session["df_base"] = self.df_base
        self.app.session["df_monitoreo"] = self.df_monitoreo
        self.app.session["meta_m1"] = self.meta
        
        # Navegar a resultados (pendiente crear en Paso 5)
        self.app.navegar("m1_resultados")

```

### m1_config.py

```python
"""
ui/pages/m1_config.py
======================
Pantalla de configuración para el Modelo M1: Consumo Absoluto.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from ui.theme import COLORS, FONTS, DIMS
from ui.components import SelectorFecha

class M1ConfigPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_topbar()
        self._build_cuerpo()

    def _build_topbar(self):
        topbar = ctk.CTkFrame(
            self, fg_color=COLORS.bg_card,
            corner_radius=0, height=DIMS.topbar_height
        )
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)

        # Línea de acento
        ctk.CTkFrame(topbar, fg_color=COLORS.accent, height=2).place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        ctk.CTkButton(
            topbar, text="← Inicio", font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent", text_color=COLORS.primary,
            hover_color=COLORS.bg_main, width=90, height=32,
            command=lambda: self.app.navegar("home")
        ).grid(row=0, column=0, padx=16, pady=8, sticky="w")

        ctk.CTkLabel(
            topbar, text="Modelo M1: Consumo Absoluto — Configuración",
            font=(FONTS.family, FONTS.size_md, "bold"), text_color=COLORS.primary
        ).grid(row=0, column=1, sticky="w", padx=8)

        ctk.CTkButton(
            topbar, text="🚀 Cargar datos existentes",
            font=(FONTS.family, FONTS.size_sm), fg_color=COLORS.primary,
            text_color=COLORS.text_white, height=32,
            command=lambda: self.app.navegar("m1_carga")
        ).grid(row=0, column=2, padx=16, pady=8, sticky="e")

    def _build_cuerpo(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS.bg_main, corner_radius=0)
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            scroll, fg_color=COLORS.bg_card, corner_radius=DIMS.card_radius,
            border_width=1, border_color=COLORS.border
        )
        card.grid(row=0, column=0, padx=48, pady=24, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        pad = {"padx": DIMS.padding_card, "pady": (0, 16)}

        # 1. Identificación
        self._seccion_label(card, "Identificación del Proyecto")
        self.entry_nombre = self._entry(card, "Nombre de la Entidad / Edificio / Proceso", row=1)
        
        # Fuente y Unidad en la misma fila
        fuente_frame = ctk.CTkFrame(card, fg_color="transparent")
        fuente_frame.grid(row=2, column=0, sticky="ew", **pad)
        fuente_frame.grid_columnconfigure((0, 1), weight=1)

        self.entry_fuente = self._entry_with_label(fuente_frame, "Fuente de Energía", "Ej: Electricidad", 0, 0)
        self.entry_unidad = self._entry_with_label(fuente_frame, "Unidad de Medida", "Ej: kWh", 0, 1)

        # 2. Periodo Base
        self._seccion_label(card, "Periodo Base (Histórico)", row=3)
        # _date_range_picker usa row y row+1 (4 y 5)
        self.sel_pb_ini, self.sel_pb_fin, self.lbl_resumen_pb = self._date_range_picker(card, 4)

        # 3. Periodo de Reporte
        self._seccion_label(card, "Periodo de Reporte (Seguimiento)", row=6)
        # _date_range_picker usa row y row+1 (7 y 8)
        self.sel_pr_ini, self.sel_pr_fin, self.lbl_resumen_pr = self._date_range_picker(card, 7)

        # Inicializar resúmenes
        self._actualizar_todos_los_resumenes()

        # Botón Acción
        self._build_botones(scroll)

    def _build_botones(self, parent):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="ew", padx=48, pady=(0, 32))

        ctk.CTkButton(
            btn_frame, text="📥  Confirmar y descargar plantilla M1",
            font=(FONTS.family, FONTS.size_md, "bold"),
            fg_color=COLORS.accent, text_color=COLORS.primary,
            height=44, command=self._confirmar_y_descargar
        ).pack(side="left")

    # --- Helpers ---
    def _seccion_label(self, parent, texto, row=0):
        ctk.CTkLabel(
            parent, text=texto, font=(FONTS.family, FONTS.size_sm, "bold"),
            text_color=COLORS.primary, anchor="w"
        ).grid(row=row, column=0, sticky="w", padx=DIMS.padding_card, pady=(16, 4))

    def _entry(self, parent, placeholder, row):
        e = ctk.CTkEntry(parent, placeholder_text=placeholder, font=(FONTS.family, FONTS.size_sm),
                         fg_color=COLORS.bg_main, border_color=COLORS.border, height=38, corner_radius=8)
        e.grid(row=row, column=0, sticky="ew", padx=DIMS.padding_card, pady=(0, 16))
        return e

    def _entry_with_label(self, parent, label, placeholder, row, col):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=col, sticky="ew", padx=4 if col==0 else (4,0))
        f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(f, text=label, font=(FONTS.family, FONTS.size_xs), text_color=COLORS.text_secondary).grid(row=0, column=0, sticky="w")
        e = ctk.CTkEntry(f, placeholder_text=placeholder, height=38, corner_radius=8, fg_color=COLORS.bg_main, border_color=COLORS.border)
        e.grid(row=1, column=0, sticky="ew")
        return e

    def _date_range_picker(self, parent, row):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=0, sticky="ew", padx=DIMS.padding_card, pady=(0, 4))
        f.grid_columnconfigure((0, 1), weight=1)
        
        sel_ini = SelectorFecha(f, label_text="Fecha Inicio", command=self._actualizar_todos_los_resumenes)
        sel_ini.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        
        sel_fin = SelectorFecha(f, label_text="Fecha Fin", command=self._actualizar_todos_los_resumenes)
        sel_fin.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        lbl = ctk.CTkLabel(parent, text="", font=(FONTS.family, FONTS.size_xs, "italic"),
                           text_color=COLORS.success, anchor="w")
        lbl.grid(row=row+1, column=0, sticky="w", padx=DIMS.padding_card, pady=(0, 16))
        
        return sel_ini, sel_fin, lbl

    def _confirmar_y_descargar(self):
        # Lógica de guardado en sesión y llamada a io_excel
        data = {
            "nombre": self.entry_nombre.get().strip(),
            "fuente": self.entry_fuente.get().strip(),
            "unidad": self.entry_unidad.get().strip(),
            "pb_ini": self.sel_pb_ini.get_value(),
            "pb_fin": self.sel_pb_fin.get_value(),
            "pr_ini": self.sel_pr_ini.get_value(),
            "pr_fin": self.sel_pr_fin.get_value(),
        }

        if not data["nombre"] or not data["fuente"] or not data["unidad"]:
            messagebox.showwarning("Campos faltantes", "Por favor completa la identificación del proyecto.")
            return

        # Validar lógica de rangos
        if not self._validar_rango(data["pb_ini"], data["pb_fin"]):
            messagebox.showerror("Rango inválido", "En Periodo Base, la fecha fin debe ser posterior a inicio.")
            return
        if not self._validar_rango(data["pr_ini"], data["pr_fin"]):
            messagebox.showerror("Rango inválido", "En Periodo Reporte, la fecha fin debe ser posterior a inicio.")
            return

        # Guardar en sesión
        self.app.session.update(data)
        
        from core.io_excel import generar_plantilla_m1
        if generar_plantilla_m1(data):
            pass

    def _actualizar_todos_los_resumenes(self):
        self._actualizar_etiqueta_rango(self.sel_pb_ini, self.sel_pb_fin, self.lbl_resumen_pb)
        self._actualizar_etiqueta_rango(self.sel_pr_ini, self.sel_pr_fin, self.lbl_resumen_pr)

    def _actualizar_etiqueta_rango(self, sel_ini, sel_fin, lbl):
        f1 = sel_ini.get_value()
        f2 = sel_fin.get_value()
        try:
            d1 = datetime.strptime(f1, "%m/%Y")
            d2 = datetime.strptime(f2, "%m/%Y")
            meses = (d2.year - d1.year) * 12 + (d2.month - d1.month) + 1
            meses_abr = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
            f1_txt = f"{meses_abr[d1.month-1]}-{d1.year}"
            f2_txt = f"{meses_abr[d2.month-1]}-{d2.year}"
            
            if meses > 0:
                lbl.configure(text=f"✓ {f1_txt} → {f2_txt} ({meses} meses)", text_color=COLORS.success)
            else:
                lbl.configure(text="✕ Rango inválido", text_color=COLORS.danger)
        except: pass

    def _validar_rango(self, f1_str, f2_str):
        try:
            d1 = datetime.strptime(f1_str, "%m/%Y")
            d2 = datetime.strptime(f2_str, "%m/%Y")
            return d2 >= d1
        except: return False

```

### m1_resultados.py

```python
"""
ui/pages/m1_resultados.py
=========================
Visualización de resultados del Modelo M1: Consumo Absoluto.
"""

import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ui.theme import COLORS, FONTS, DIMS
from core.io_excel import escribir_resultados_m1

class M1ResultadosPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        
        # Recuperar datos de sesión
        self.df_lben = self.app.session.get("df_lben")
        self.df_mon  = self.app.session.get("df_monitoreo")
        self.meta    = self.app.session.get("meta_m1")

        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_topbar()
        self._build_tabs()

    def _build_topbar(self):
        topbar = ctk.CTkFrame(self, fg_color=COLORS.bg_card, corner_radius=0, height=DIMS.topbar_height)
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)

        ctk.CTkFrame(topbar, fg_color=COLORS.accent, height=2).place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        ctk.CTkButton(
            topbar, text="← Volver a Carga", font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent", text_color=COLORS.primary, hover_color=COLORS.bg_main,
            width=120, height=32, command=lambda: self.app.navegar("m1_carga")
        ).grid(row=0, column=0, padx=16, pady=8, sticky="w")

        ctk.CTkLabel(
            topbar, text="M1: Resultados y Seguimiento",
            font=(FONTS.family, FONTS.size_md, "bold"), text_color=COLORS.primary
        ).grid(row=0, column=1, sticky="w", padx=8)

        ctk.CTkButton(
            topbar, text="💾 Actualizar Informe en Excel",
            font=(FONTS.family, FONTS.size_sm, "bold"), fg_color=COLORS.primary,
            text_color="white", height=32, command=self._guardar_excel
        ).grid(row=0, column=2, padx=16, pady=8, sticky="e")

    def _build_tabs(self):
        self.tabs = ctk.CTkTabview(
            self, fg_color=COLORS.bg_main, segmented_button_fg_color=COLORS.bg_card,
            segmented_button_selected_color=COLORS.primary,
            segmented_button_selected_hover_color=COLORS.primary_dark,
            segmented_button_unselected_hover_color=COLORS.border,
            text_color=COLORS.primary
        )
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        self.tabs.add("Línea Base")
        self.tabs.add("Desempeño")
        self.tabs.add("Seguimiento")
        self.tabs.add("Ajuste NR")

        self._render_lben_tab()
        self._render_desempeno_tab()
        self._render_seguimiento_tab()
        self._render_ajuste_tab()

    def _render_lben_tab(self):
        tab = self.tabs.tab("Línea Base")
        
        fig, ax = plt.subplots(figsize=(8, 4), facecolor=COLORS.bg_main)
        ax.set_facecolor(COLORS.bg_main)
        
        meses = self.df_lben['mes']
        valores = self.df_lben['lben']
        
        ax.bar(meses, valores, color=COLORS.primary, alpha=0.7, label="LBEn Mensual")
        ax.plot(meses, valores, marker='o', color=COLORS.accent, linewidth=2)
        
        ax.set_title("Línea Base Energética por Mes", color=COLORS.primary, fontsize=12, fontweight='bold')
        ax.tick_params(axis='x', rotation=45, labelcolor=COLORS.text_secondary)
        ax.tick_params(axis='y', labelcolor=COLORS.text_secondary)
        ax.grid(True, axis='y', linestyle='--', alpha=0.3)
        
        rect = fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def _render_desempeno_tab(self):
        tab = self.tabs.tab("Desempeño")
        if self.df_mon is None or self.df_mon.empty:
            ctk.CTkLabel(tab, text="No hay datos de monitoreo cargados para mostrar desempeño.", text_color=COLORS.text_secondary).pack(pady=40)
            return

        fig, ax = plt.subplots(figsize=(8, 4), facecolor=COLORS.bg_main)
        ax.set_facecolor(COLORS.bg_main)
        
        ax.plot(self.df_mon['Fecha'], self.df_mon['LBEn_Mes'], label="Línea Base (Meta)", color=COLORS.primary, linestyle='--', marker='s')
        ax.plot(self.df_mon['Fecha'], self.df_mon['Normalizado'], label="Consumo Real", color=COLORS.accent, marker='o', linewidth=2)
        
        ax.set_title("Consumo Real vs Línea Base", color=COLORS.primary, fontsize=12, fontweight='bold')
        ax.legend()
        ax.tick_params(axis='x', rotation=45, labelcolor=COLORS.text_secondary)
        ax.tick_params(axis='y', labelcolor=COLORS.text_secondary)
        ax.grid(True, linestyle='--', alpha=0.3)
        
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def _render_seguimiento_tab(self):
        tab = self.tabs.tab("Seguimiento")
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        if self.df_mon is None or self.df_mon.empty:
            ctk.CTkLabel(scroll, text="Cargue datos de monitoreo para ver la tabla de seguimiento.").pack(pady=20)
            return

        # Encabezado simple de tabla
        headers = ["Fecha", "Real (kWh)", "LBEn (kWh)", "Ahorro (kWh)", "Ahorro (%)"]
        h_frame = ctk.CTkFrame(scroll, fg_color=COLORS.primary, height=30)
        h_frame.pack(fill="x", pady=(0, 5))
        for i, h in enumerate(headers):
            ctk.CTkLabel(h_frame, text=h, text_color="white", font=(FONTS.family, 11, "bold"), width=120).grid(row=0, column=i, padx=5)

        # Filas
        for _, row in self.df_mon.iterrows():
            f_frame = ctk.CTkFrame(scroll, fg_color=COLORS.bg_card, height=28)
            f_frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(f_frame, text=row['Fecha'], width=120).grid(row=0, column=0, padx=5)
            ctk.CTkLabel(f_frame, text=f"{row['Normalizado']:,.1f}", width=120).grid(row=0, column=1, padx=5)
            ctk.CTkLabel(f_frame, text=f"{row['LBEn_Mes']:,.1f}", width=120).grid(row=0, column=2, padx=5)
            
            ahorro = row['Ahorro_kWh']
            color = COLORS.primary if ahorro >= 0 else COLORS.danger
            ctk.CTkLabel(f_frame, text=f"{ahorro:,.1f}", text_color=color, width=120, font=(FONTS.family, 11, "bold")).grid(row=0, column=3, padx=5)
            ctk.CTkLabel(f_frame, text=f"{row['Ahorro_Pct']:,.1f}%", text_color=color, width=120, font=(FONTS.family, 11, "bold")).grid(row=0, column=4, padx=5)

    def _render_ajuste_tab(self):
        tab = self.tabs.tab("Ajuste NR")
        ctk.CTkLabel(
            tab, text="Ajustes No Rutinarios Detectados",
            font=(FONTS.family, FONTS.size_lg, "bold"), text_color=COLORS.primary
        ).pack(pady=20)
        
        # Aquí se detectarán filas donde 'Ajuste No Rutinario (NR)' == 'Si'
        ajustes = self.df_base[self.df_base.iloc[:, 5].astype(str).str.lower() == 'si'] if self.df_base is not None else []
        
        if len(ajustes) == 0:
            ctk.CTkLabel(tab, text="No se han reportado eventos no rutinarios en el periodo base.", text_color=COLORS.text_secondary).pack()
        else:
            for _, row in ajustes.iterrows():
                msg = f"• {row['Fecha']}: {row.iloc[6]}"
                ctk.CTkLabel(tab, text=msg, anchor="w", justify="left").pack(fill="x", padx=40)

    def _guardar_excel(self):
        path = self.app.session.get("excel_path")
        if not path: return
        
        if escribir_resultados_m1(path, self.df_lben, self.df_mon, self.meta):
            messagebox.showinfo("Éxito", "El archivo Excel ha sido actualizado con los resultados.")
        else:
            messagebox.showerror("Error", "No se pudo actualizar el archivo.")

```

### m2.py

```python

```

### m3.py

```python

```

### monitoreo.py

```python

```

### seleccion_modelo.py

```python
"""
ui/pages/seleccion_modelo.py
=============================
Pantalla de selección de modelo.
Muestra los 3 modelos disponibles con la recomendación destacada.
"""

import customtkinter as ctk
from ui.theme import COLORS, FONTS, DIMS


class SeleccionModeloPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        self._recomendacion = self._obtener_recomendacion()
        self._build()

    def _obtener_recomendacion(self) -> str:
        """Obtiene el código del modelo recomendado desde la sesión."""
        res = self.app.session.get("resultados_exploratorio")
        if res and "recomendacion" in res:
            return res["recomendacion"].get("codigo", "")
        return ""

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_topbar()
        self._build_cuerpo()

    # ── Topbar ────────────────────────────────────────────────────────────────
    def _build_topbar(self):
        topbar = ctk.CTkFrame(
            self, fg_color=COLORS.bg_card,
            corner_radius=0, height=DIMS.topbar_height
        )
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)

        ctk.CTkFrame(
            topbar, fg_color=COLORS.accent,
            height=2, corner_radius=0
        ).place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        ctk.CTkButton(
            topbar,
            text="← Exploración",
            font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent",
            text_color=COLORS.primary,
            hover_color=COLORS.bg_main,
            width=110, height=32,
            corner_radius=DIMS.button_radius,
            command=lambda: self.app.navegar("exploratorio_resultados")
        ).grid(row=0, column=0, padx=16, pady=8, sticky="w")

        ctk.CTkLabel(
            topbar,
            text="Selecciona el modelo de LBEn",
            font=(FONTS.family, FONTS.size_md, "bold"),
            text_color=COLORS.primary
        ).grid(row=0, column=1, sticky="w", padx=8)

        ctk.CTkButton(
            topbar,
            text="🏠 Inicio",
            font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent",
            text_color=COLORS.primary,
            hover_color=COLORS.bg_main,
            width=80, height=32,
            corner_radius=DIMS.button_radius,
            command=lambda: self.app.navegar("home")
        ).grid(row=0, column=2, padx=16, pady=8, sticky="e")

    # ── Cuerpo ────────────────────────────────────────────────────────────────
    def _build_cuerpo(self):
        cuerpo = ctk.CTkFrame(
            self, fg_color=COLORS.bg_main, corner_radius=0
        )
        cuerpo.grid(row=1, column=0, sticky="nsew")
        cuerpo.grid_columnconfigure(0, weight=1)
        cuerpo.grid_rowconfigure(1, weight=1)

        # Subtítulo
        ctk.CTkLabel(
            cuerpo,
            text="Elige el modelo que mejor se adapte a tus datos y objetivos."
                 " Aparecerá resaltado el modelo recomendado en el ultimo análisis exploratorio",
            font=(FONTS.family, FONTS.size_sm),
            text_color=COLORS.text_secondary,
            justify="left"
        ).grid(row=0, column=0, sticky="w", padx=48, pady=(24, 16))

        # Grid de 3 cards
        cards_frame = ctk.CTkFrame(cuerpo, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="nsew", padx=48, pady=(0, 32))
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
        cards_frame.grid_rowconfigure(0, weight=1)

        modelos = [
            {
                "codigo":    "M1",
                "titulo":    "Consumo Absoluto",
                "subtitulo": "Promedios Mensuales",
                "descripcion": (
                    "Estima la línea base como el promedio del "
                    "consumo histórico mensual.\n\n"
                    "Ideal cuando el consumo es relativamente "
                    "constante y no depende o no se dispone de variables externas."
                ),
                "variables": "Solo consumo energético",
                "recomendado_para": "Edificios con consumo estable",
                "destino": "m1_config"
            },
            {
                "codigo":    "M2",
                "titulo":    "Modelo de Cociente",
                "subtitulo": "Consumo Normalizado",
                "descripcion": (
                    "Calcula un índice de consumo energético "
                    "normalizado por una variable (Ej: kWh/visitantes).\n\n"
                    "Útil cuando el consumo escala proporcionalmente con una sola "
                    "variable como usuarios o área."
                ),
                "variables": "Consumo + 1 variable",
                "recomendado_para": "Edificios con ocupación variable",
                "destino": "m2_config"
            },
            {
                "codigo":    "M3",
                "titulo":    "Modelos Estadísticos",
                "subtitulo": "Regresión Lineal",
                "descripcion": (
                    "Calcula el consumo en función de una o más "
                    "variables independientes estadísticamente "
                    "significativas.\n\n"
                    "Puede detectar relaciones complejas entre variables"
                ),
                "variables": "Consumo + 1 o más variables significativas",
                "recomendado_para": "Edificios con múltiples variables disponibles",
                "destino": "m3_config"
            }
        ]

        for col, modelo in enumerate(modelos):
            es_rec = modelo["codigo"] == self._recomendacion
            self._build_card_modelo(cards_frame, modelo, col, es_rec)

    # ── Card modelo ───────────────────────────────────────────────────────────
    def _build_card_modelo(self, parent, modelo, col, es_recomendado):
        # Estilo según si es recomendado
        if es_recomendado:
            fg_card    = COLORS.primary
            fg_icono   = COLORS.accent
            fg_titulo  = COLORS.text_white
            fg_sub     = COLORS.accent
            fg_desc    = "#A8C4BC"
            fg_label   = "#7A9B8E"
            fg_val     = "#C8DDD8"
            btn_fg     = COLORS.accent
            btn_txt    = COLORS.primary
            btn_hover  = "#D4E800"
            border_c   = COLORS.accent
        else:
            fg_card    = COLORS.bg_card
            fg_icono   = COLORS.primary
            fg_titulo  = COLORS.primary
            fg_sub     = COLORS.text_secondary
            fg_desc    = COLORS.text_secondary
            fg_label   = COLORS.text_secondary
            fg_val     = COLORS.text_primary
            btn_fg     = COLORS.primary
            btn_txt    = COLORS.text_white
            btn_hover  = COLORS.primary_dark
            border_c   = COLORS.border

        card = ctk.CTkFrame(
            parent,
            fg_color=fg_card,
            corner_radius=DIMS.card_radius,
            border_width=2 if es_recomendado else 1,
            border_color=border_c
        )
        card.grid(
            row=0, column=col,
            padx=(0, 12) if col < 2 else 0,
            sticky="nsew", pady=4
        )
        card.grid_columnconfigure(0, weight=1)

        # Badge recomendado
        if es_recomendado:
            badge = ctk.CTkFrame(card, fg_color=COLORS.success, corner_radius=10, height=24)
            badge.place(relx=1.0, x=-10, y=10, anchor="ne")
            ctk.CTkLabel(
                badge, text="RECOMENDADO", 
                font=(FONTS.family, 10, "bold"),
                text_color="white", padx=10
            ).pack()
        else:
            ctk.CTkFrame(
                card, fg_color="transparent", height=24
            ).grid(row=0, column=0, padx=16, pady=(16, 0), sticky="w")

        # Ícono / Ilustración
        from PIL import Image
        import os
        
        modelo_id = modelo["codigo"]
        icon_map = {"M1": "m1_icon.png", "M2": "m2_icon.png", "M3": "m3_icon.png"}
        icon_path = os.path.join("assets", icon_map.get(modelo_id, "m1_icon.png"))
        
        try:
            pil_img = Image.open(icon_path)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(48, 48))
            icon_label = ctk.CTkLabel(card, text="", image=ctk_img)
            icon_label.grid(row=1, column=0, padx=16, pady=(8, 0), sticky="w")
        except:
            ctk.CTkLabel(
                card, text="📊", font=(FONTS.family, 32),
                text_color=fg_icono
            ).grid(row=1, column=0, padx=16, pady=(8, 0), sticky="w")

        # Título
        ctk.CTkLabel(
            card,
            text=modelo["titulo"],
            font=(FONTS.family, FONTS.size_md, "bold"),
            text_color=fg_titulo
        ).grid(row=2, column=0, padx=16, pady=(16, 0), sticky="w")

        # Subtítulo
        ctk.CTkLabel(
            card,
            text=modelo["subtitulo"],
            font=(FONTS.family, FONTS.size_xs),
            text_color=fg_sub
        ).grid(row=3, column=0, padx=16, pady=(0, 12), sticky="w")

        # Separador
        ctk.CTkFrame(
            card,
            fg_color=COLORS.accent if es_recomendado else COLORS.border,
            height=1, corner_radius=0
        ).grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 12))

        # Descripción
        ctk.CTkLabel(
            card,
            text=modelo["descripcion"],
            font=(FONTS.family, FONTS.size_xs),
            text_color=fg_desc,
            wraplength=240,
            justify="center"
        ).grid(row=5, column=0, padx=16, pady=(0, 16))

        # --- FILA ELÁSTICA (ESPACIADOR) ---
        # Fila 6 absorbe espacio y empuja lo demás al fondo
        card.grid_rowconfigure(6, weight=1)
        ctk.CTkFrame(card, fg_color="transparent", height=1).grid(row=6, column=0)

        # Variables (Cuadro Gris)
        info_frame = ctk.CTkFrame(
            card,
            fg_color=COLORS.primary_dark if es_recomendado else COLORS.bg_main,
            corner_radius=8
        )
        info_frame.grid(row=7, column=0, sticky="ew",
                        padx=16, pady=(0, 12))

        ctk.CTkLabel(
            info_frame,
            text="Variables:",
            font=(FONTS.family, FONTS.size_xs, "bold"),
            text_color=fg_label, anchor="w"
        ).pack(anchor="w", padx=12, pady=(8, 2))

        ctk.CTkLabel(
            info_frame,
            text=modelo["variables"],
            font=(FONTS.family, FONTS.size_xs),
            text_color=fg_val, anchor="w",
            wraplength=220, justify="left"
        ).pack(anchor="w", padx=12, pady=(0, 4))

        ctk.CTkLabel(
            info_frame,
            text="Recomendado para:",
            font=(FONTS.family, FONTS.size_xs, "bold"),
            text_color=fg_label, anchor="w"
        ).pack(anchor="w", padx=12, pady=(4, 2))

        ctk.CTkLabel(
            info_frame,
            text=modelo["recomendado_para"],
            font=(FONTS.family, FONTS.size_xs),
            text_color=fg_val, anchor="w",
            wraplength=220, justify="left"
        ).pack(anchor="w", padx=12, pady=(0, 8))

        # Botón configurar
        ctk.CTkButton(
            card,
            text="Configurar →",
            font=(FONTS.family, FONTS.size_sm, "bold"),
            fg_color=btn_fg,
            text_color=btn_txt,
            hover_color=btn_hover,
            corner_radius=DIMS.button_radius,
            height=40,
            command=lambda d=modelo["destino"]: self.app.navegar(d)
        ).grid(row=8, column=0, padx=16, pady=(0, 20), sticky="ew")
```

## State

### session.py

```python

```

