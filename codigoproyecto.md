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

    wb.save(path)
    return True


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
```

## Core / Models

### m1_absoluto.py

```python

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
            card, placeholder="Ej: Edificio Central — 2024"
        )
        self.entry_nombre.grid(row=2, column=0, sticky="ew", **pad)

        # ── Periodo de análisis ───────────────────────────────────────────────
        self._seccion_label(card, "Periodo de análisis", row=3)

        fechas_frame = ctk.CTkFrame(card, fg_color="transparent")
        fechas_frame.grid(row=4, column=0, sticky="ew", **pad)
        fechas_frame.grid_columnconfigure((0, 1), weight=1)

        # Fecha inicio
        fi_frame = ctk.CTkFrame(fechas_frame, fg_color="transparent")
        fi_frame.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        fi_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            fi_frame, text="Fecha inicio (MM/AAAA)",
            font=(FONTS.family, FONTS.size_xs),
            text_color=COLORS.text_secondary, anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.entry_fecha_ini = self._entry(
            fi_frame, placeholder="Ej: 01/2022"
        )
        self.entry_fecha_ini.grid(row=1, column=0, sticky="ew")

        # Fecha fin
        ff_frame = ctk.CTkFrame(fechas_frame, fg_color="transparent")
        ff_frame.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        ff_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            ff_frame, text="Fecha fin (MM/AAAA)",
            font=(FONTS.family, FONTS.size_xs),
            text_color=COLORS.text_secondary, anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.entry_fecha_fin = self._entry(
            ff_frame, placeholder="Ej: 12/2024"
        )
        self.entry_fecha_fin.grid(row=1, column=0, sticky="ew")

        # ── Variable dependiente ──────────────────────────────────────────────
        self._seccion_label(card, "Variable dependiente (consumo)", row=5)

        ctk.CTkLabel(
            card,
            text="Debe coincidir exactamente con el encabezado en la factura.",
            font=(FONTS.family, FONTS.size_xs),
            text_color=COLORS.text_secondary, anchor="w"
        ).grid(row=6, column=0, sticky="w", padx=DIMS.padding_card, pady=(0, 4))

        self.entry_var_dep = self._entry(
            card, placeholder="Ej: Consumo_kWh"
        )
        self.entry_var_dep.grid(row=7, column=0, sticky="ew", **pad)

        # ── Variables independientes ──────────────────────────────────────────
        self._seccion_label(card, "Variables independientes", row=8)

        ctk.CTkLabel(
            card,
            text="Agrega todas las variables que creas que pueden influir "
                 "en el consumo (Ej: Temperatura, Producción).",
            font=(FONTS.family, FONTS.size_xs),
            text_color=COLORS.text_secondary, anchor="w",
            wraplength=700, justify="left"
        ).grid(row=9, column=0, sticky="w",
               padx=DIMS.padding_card, pady=(0, 8))

        # Frame dinámico para variables
        self.vars_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.vars_frame.grid(row=10, column=0, sticky="ew",
                             padx=DIMS.padding_card, pady=(0, 8))
        self.vars_frame.grid_columnconfigure(0, weight=1)

        # Primera variable por defecto
        self._agregar_variable()

        # Botón agregar variable
        ctk.CTkButton(
            card,
            text="+ Agregar variable candidata",
            font=(FONTS.family, FONTS.size_sm),
            fg_color="transparent",
            text_color=COLORS.primary,
            hover_color=COLORS.bg_main,
            border_width=1,
            border_color=COLORS.primary,
            corner_radius=DIMS.button_radius,
            height=32,
            command=self._agregar_variable
        ).grid(row=11, column=0, sticky="w",
               padx=DIMS.padding_card, pady=(0, 20))

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

        # Botón eliminar (solo si no es la primera)
        if idx > 1:
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
        fecha_ini = self.entry_fecha_ini.get().strip()
        fecha_fin = self.entry_fecha_fin.get().strip()
        var_dep   = self.entry_var_dep.get().strip()
        vars_ind  = [e.get().strip() for e in self.vars_independientes
                     if e.get().strip()]

        # Validaciones
        if not nombre:
            messagebox.showwarning("Campo requerido",
                                   "Ingresa el nombre del proyecto.")
            return
        if not fecha_ini or not fecha_fin:
            messagebox.showwarning("Campo requerido",
                                   "Ingresa las fechas de inicio y fin.")
            return
        if not self._validar_fecha(fecha_ini) or \
           not self._validar_fecha(fecha_fin):
            messagebox.showerror("Formato incorrecto",
                                 "Las fechas deben tener formato MM/AAAA.\n"
                                 "Ejemplo: 01/2022")
            return
        if not var_dep:
            messagebox.showwarning("Campo requerido",
                                   "Ingresa el nombre de la variable dependiente.")
            return
        if not vars_ind:
            messagebox.showwarning("Campo requerido",
                                   "Agrega al menos una variable independiente.")
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

    def _validar_fecha(self, fecha_str: str) -> bool:
        try:
            datetime.strptime(fecha_str, "%m/%Y")
            return True
        except ValueError:
            return False
```

### exploratorio_resultados.py

```python
"""
ui/pages/exploratorio_resultados.py
=====================================
Pantalla de resultados del análisis exploratorio.
Muestra: recomendación, tabla Pearson, scatters, sincronía temporal.
"""

import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from ui.theme import COLORS, FONTS, DIMS


class ExploratorioResultadosPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS.bg_main)
        self.app = master
        self._resultados    = None
        self._recomendacion = None
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
        from core.exploratorio import calcular_correlaciones, recomendar_modelo
        sesion   = self.app.session
        df       = sesion.get("df_datos")
        var_dep  = sesion.get("var_dependiente", "")
        vars_ind = sesion.get("vars_independientes", [])

        if df is None or not var_dep:
            return

        self._resultados    = calcular_correlaciones(df, var_dep, vars_ind)
        self._recomendacion = recomendar_modelo(self._resultados)

        # Guardar recomendación en sesión
        sesion["resultados_exploratorio"] = {
            "correlaciones":  self._resultados,
            "recomendacion":  self._recomendacion
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

        # 2 — Card tabla Pearson
        self._build_card_tabla(self.scroll, fila)
        fila += 1

        # 3 — Scatters por variable
        self._build_scatters(self.scroll, fila)
        fila += 1

        # 4 — Sincronía temporal
        self._build_sincronia(self.scroll, fila)
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

        # Ícono modelo
        iconos = {"M1": "≡", "M2": "÷", "M3": "∿"}
        icono  = iconos.get(rec["codigo"], "📊")

        ctk.CTkLabel(
            card,
            text=icono,
            font=(FONTS.family, 36),
            text_color=COLORS.accent
        ).grid(row=0, column=0, rowspan=2, padx=20, pady=20)

        ctk.CTkLabel(
            card,
            text=rec["titulo"],
            font=(FONTS.family, FONTS.size_xl, "bold"),
            text_color=COLORS.text_white,
            anchor="w"
        ).grid(row=0, column=1, sticky="w", padx=(0, 20), pady=(20, 4))

        ctk.CTkLabel(
            card,
            text="✦ Recomendación del Sistema",
            font=(FONTS.family, FONTS.size_xs),
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

            # Variable
            ctk.CTkLabel(
                fila_frame,
                text=res["variable"],
                font=(FONTS.family, FONTS.size_xs, "bold"),
                text_color=COLORS.primary, anchor="center"
            ).grid(row=0, column=0, sticky="ew", padx=6, pady=6)

            # r Pearson
            r_val = res["r_pearson"]
            r_txt = f"{r_val:+.4f}" if r_val is not None else "—"
            r_color = self._color_r(r_val)
            ctk.CTkLabel(
                fila_frame, text=r_txt,
                font=(FONTS.family_mono, FONTS.size_xs, "bold"),
                text_color=r_color, anchor="center"
            ).grid(row=0, column=1, sticky="ew", padx=6, pady=6)

            # p-valor
            p_val = res["p_valor"]
            p_txt = f"{p_val:.4f}" if p_val is not None else "—"
            p_color = COLORS.success if res["significativa"] else COLORS.danger
            ctk.CTkLabel(
                fila_frame, text=p_txt,
                font=(FONTS.family_mono, FONTS.size_xs),
                text_color=p_color, anchor="center"
            ).grid(row=0, column=2, sticky="ew", padx=6, pady=6)

            # Significativa
            sig_txt   = "✅ Sí" if res["significativa"] else "❌ No"
            sig_color = COLORS.success if res["significativa"] else COLORS.danger
            ctk.CTkLabel(
                fila_frame, text=sig_txt,
                font=(FONTS.family, FONTS.size_xs, "bold"),
                text_color=sig_color, anchor="center"
            ).grid(row=0, column=3, sticky="ew", padx=6, pady=6)

            # Grado
            ctk.CTkLabel(
                fila_frame, text=res["grado"],
                font=(FONTS.family, FONTS.size_xs),
                text_color=COLORS.text_secondary, anchor="center"
            ).grid(row=0, column=4, sticky="ew", padx=6, pady=6)

            # Interpretación
            ctk.CTkLabel(
                fila_frame, text=res["interpretacion"],
                font=(FONTS.family, FONTS.size_xs),
                text_color=COLORS.text_primary,
                anchor="w", wraplength=300, justify="left"
            ).grid(row=0, column=5, sticky="ew", padx=6, pady=6)

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

        card = self._card(
            parent, fila,
            "📊  Análisis de Dispersión y Proporcionalidad"
        )

        # Grid de scatters: 2 columnas
        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=16, pady=(0, 16))
        grid.grid_columnconfigure((0, 1), weight=1)

        for idx, var in enumerate(vars_ind):
            datos = preparar_datos_scatter(df, var_dep, var)
            col   = idx % 2
            row   = idx // 2

            fig = self._crear_scatter(datos, var_dep, var)
            canvas_frame = ctk.CTkFrame(
                grid, fg_color=COLORS.bg_card,
                corner_radius=8,
                border_width=1, border_color=COLORS.border
            )
            canvas_frame.grid(
                row=row, column=col,
                padx=(0, 8) if col == 0 else 0,
                pady=8, sticky="nsew"
            )
            canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
            plt.close(fig)

    def _crear_scatter(self, datos, var_dep, var_ind):
        fig, ax = plt.subplots(figsize=(5, 3.5))
        fig.patch.set_facecolor(COLORS.bg_card)
        ax.set_facecolor("#F8FAF9")

        x, y = datos["x"], datos["y"]
        r    = datos["r"]
        p    = datos["p_valor"]

        # Puntos
        ax.scatter(x, y, color=COLORS.primary, alpha=0.7,
                   s=50, zorder=3, edgecolors="white", linewidths=0.5)

        # Línea tendencia
        if len(datos["x_trend"]) > 0:
            ax.plot(datos["x_trend"], datos["y_trend"],
                    color=COLORS.accent, linewidth=2,
                    linestyle="--", zorder=2)

        # Etiquetas
        ax.set_xlabel(var_ind, fontsize=9,
                      color=COLORS.text_secondary, fontfamily="sans-serif")
        ax.set_ylabel(var_dep, fontsize=9,
                      color=COLORS.text_secondary, fontfamily="sans-serif")

        titulo = f"Dispersión: {var_dep} vs {var_ind}"
        if r is not None:
            sig = "✓ sig." if (p is not None and p < 0.05) else "✗ no sig."
            titulo += f"\nr = {r:+.3f}  |  p = {p:.4f}  |  {sig}"

        ax.set_title(titulo, fontsize=8.5, color=COLORS.primary,
                     fontweight="bold", pad=10)

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

        if df is None:
            return

        from core.exploratorio import preparar_datos_sincronia
        datos = preparar_datos_sincronia(df, var_dep, vars_ind)

        card = self._card(
            parent, fila,
            "📈  Sincronía Temporal (Consumo vs Variables)"
        )

        fig = self._crear_sincronia(datos, var_dep)
        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(
            fill="both", expand=True, padx=16, pady=(0, 16)
        )
        plt.close(fig)

    def _crear_sincronia(self, datos, var_dep):
        fechas = datos["fechas"]
        series = datos["series"]
        n      = len(fechas)

        fig, ax = plt.subplots(figsize=(11, 3.5))
        fig.patch.set_facecolor(COLORS.bg_card)
        ax.set_facecolor("#F8FAF9")

        colores = [COLORS.primary, COLORS.accent,
                   "#E63946", "#F4A261", "#2D6A4F", "#457B9D"]

        for idx, (nombre, valores) in enumerate(series.items()):
            color  = colores[idx % len(colores)]
            estilo = "-" if nombre == var_dep else "--"
            grosor = 2.5 if nombre == var_dep else 1.5
            ax.plot(range(n), valores,
                    color=color, linewidth=grosor,
                    linestyle=estilo, label=nombre, zorder=3)

        # Eje X con etiquetas de fecha
        paso = max(1, n // 12)
        ax.set_xticks(range(0, n, paso))
        ax.set_xticklabels(
            [fechas[i] for i in range(0, n, paso)],
            rotation=45, ha="right", fontsize=7,
            color=COLORS.text_secondary
        )

        ax.set_ylabel("Valor normalizado (0–1)", fontsize=9,
                      color=COLORS.text_secondary)
        ax.set_title(
            "Comparativa de Patrones Temporales (Variables vs Consumo)",
            fontsize=9, color=COLORS.primary, fontweight="bold"
        )

        ax.legend(fontsize=8, loc="upper right",
                  framealpha=0.9, edgecolor=COLORS.border)
        ax.tick_params(colors=COLORS.text_secondary, labelsize=8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_color(COLORS.border)
        ax.grid(True, alpha=0.3, color=COLORS.border)
        ax.set_ylim(-0.05, 1.05)

        fig.tight_layout()
        return fig

    # ── Botones de acción ─────────────────────────────────────────────────────
    def _build_botones(self, parent, fila):
        frame = ctk.CTkFrame(parent, fg_color=COLORS.bg_card,
                             corner_radius=0, height=70)
        frame.grid(row=fila, column=0, sticky="ew", padx=0, pady=(8, 0))
        frame.grid_propagate(False)
        frame.grid_columnconfigure(1, weight=1)

        # Botón actualizar Excel
        ctk.CTkButton(
            frame,
            text="📊  Actualizar informe en Excel",
            font=(FONTS.family, FONTS.size_sm, "bold"),
            fg_color=COLORS.accent,
            text_color=COLORS.primary,
            hover_color="#D4E800",
            corner_radius=DIMS.button_radius,
            height=40,
            command=self._actualizar_excel
        ).grid(row=0, column=0, padx=24, pady=15, sticky="w")

        # Botón continuar
        ctk.CTkButton(
            frame,
            text="Continuar a selección de modelo →",
            font=(FONTS.family, FONTS.size_sm, "bold"),
            fg_color=COLORS.primary,
            text_color=COLORS.text_white,
            hover_color=COLORS.primary_dark,
            corner_radius=DIMS.button_radius,
            height=40,
            command=lambda: self.app.navegar("seleccion_modelo")
        ).grid(row=0, column=2, padx=24, pady=15, sticky="e")

    # ── Actualizar Excel ──────────────────────────────────────────────────────
    def _actualizar_excel(self):
        from tkinter import filedialog
        from core.io_excel import escribir_resultados_exploratorios

        if not self._resultados or not self._recomendacion:
            messagebox.showwarning(
                "Sin resultados",
                "Primero ejecuta el análisis antes de exportar."
            )
            return

        path = filedialog.askopenfilename(
            title="Seleccionar Excel exploratorio para actualizar",
            filetypes=[("Excel", "*.xlsx")]
        )
        if not path:
            return

        tabla = self._resultados
        rec   = self._recomendacion

        ok = escribir_resultados_exploratorios(
            path            = path,
            recomendacion   = rec["titulo"],
            justificacion   = rec["justificacion"],
            tabla_resultados= tabla
        )
        if ok:
            messagebox.showinfo(
                "Excel actualizado",
                "Los resultados fueron escritos correctamente en el Excel."
            )

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _card(self, parent, fila, titulo):
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS.bg_card,
            corner_radius=DIMS.card_radius,
            border_width=1,
            border_color=COLORS.border
        )
        card.grid(row=fila, column=0, padx=48, pady=8, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        # Título con acento izquierdo
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(14, 10))

        ctk.CTkFrame(
            header, fg_color=COLORS.accent,
            width=4, corner_radius=2
        ).pack(side="left", fill="y", padx=(0, 10))

        ctk.CTkLabel(
            header, text=titulo,
            font=(FONTS.family, FONTS.size_sm, "bold"),
            text_color=COLORS.primary, anchor="w"
        ).pack(side="left")

        return card

    def _color_r(self, r):
        if r is None:
            return COLORS.text_secondary
        r_abs = abs(r)
        if r_abs >= 0.70:
            return COLORS.success
        elif r_abs >= 0.50:
            return COLORS.warning
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
        sidebar.grid_rowconfigure(6, weight=1)

        # Línea acento superior
        acento = ctk.CTkFrame(
            sidebar, fg_color=COLORS.accent,
            height=3, corner_radius=0
        )
        acento.pack(fill="x")

        # Logo / ícono
        ctk.CTkLabel(
            sidebar,
            text="⚡",
            font=(FONTS.family, 42),
            text_color=COLORS.accent
        ).pack(pady=(32, 8))

        # Nombre app
        ctk.CTkLabel(
            sidebar,
            text="Línea Base\nEnergética",
            font=(FONTS.family, FONTS.size_lg, "bold"),
            text_color=COLORS.text_white,
            justify="center"
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            sidebar,
            text="Resolución UPME\n016 de 2024",
            font=(FONTS.family, FONTS.size_xs),
            text_color="#7A9B8E",
            justify="center"
        ).pack(pady=(0, 24))

        # Separador
        ctk.CTkFrame(
            sidebar, fg_color="#2D4F45",
            height=1, corner_radius=0
        ).pack(fill="x", padx=20, pady=8)

        # Subtítulo
        ctk.CTkLabel(
            sidebar,
            text="Modelos de referencia para\neficiencia energética",
            font=(FONTS.family, FONTS.size_xs),
            text_color="#7A9B8E",
            justify="center",
            wraplength=180
        ).pack(pady=(16, 0), padx=16)

        # Versión al fondo
        ctk.CTkLabel(
            sidebar,
            text="v1.0.0",
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
            text="Esta herramienta te permite establecer la línea base de consumo\n"
                 "energético usando modelos estadísticos validados.",
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
                           "Promedio · Cociente · Regresión", 0)
        self._feature_card(features, "📥", "Plantilla Excel",
                           "Descarga y llena tus datos", 1)
        self._feature_card(features, "📈", "Gráficos",
                           "Línea base · Dispersión", 2)

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
            text="Selecciona el modelo estadístico",
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
            text="Los modelos están ordenados de menor a mayor complejidad. "
                 "Elige el que mejor se adapte a tus datos y objetivos.",
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
                "icono":     "≡",
                "titulo":    "Modelo de Promedio",
                "subtitulo": "Consumo Absoluto",
                "descripcion": (
                    "Estima la línea base como el promedio del "
                    "consumo histórico mensual.\n\n"
                    "Ideal cuando el consumo es relativamente "
                    "constante y no depende de variables externas."
                ),
                "variables": "Solo consumo energético",
                "recomendado_para": "Procesos continuos, clima estable",
                "destino": "m1"
            },
            {
                "codigo":    "M2",
                "icono":     "÷",
                "titulo":    "Modelo de Cociente",
                "subtitulo": "Consumo Normalizado",
                "descripcion": (
                    "Calcula un índice de consumo energético "
                    "normalizado por una variable (Ej: kWh/persona).\n\n"
                    "Útil cuando el consumo escala con una sola "
                    "variable como producción o área."
                ),
                "variables": "Consumo + 1 variable de producción",
                "recomendado_para": "Edificios con ocupación variable",
                "destino": "m2"
            },
            {
                "codigo":    "M3",
                "icono":     "∿",
                "titulo":    "Regresión Lineal",
                "subtitulo": "Modelo Estadístico",
                "descripcion": (
                    "Predice el consumo en función de una o más "
                    "variables independientes estadísticamente "
                    "significativas.\n\n"
                    "Puede detectar relaciones complejas entre "
                    "variables y permite detectar ahorros "
                    "estadísticamente precisos."
                ),
                "variables": "Consumo + 1 o más variables significativas",
                "recomendado_para": "Edificios con múltiples factores",
                "destino": "m3"
            }
        ]

        for col, modelo in enumerate(modelos):
            es_rec = modelo["codigo"] == self._recomendacion
            self._build_card_modelo(
                cards_frame, modelo, col, es_rec
            )

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
        card.grid_rowconfigure(2, weight=1)

        # Badge recomendado
        if es_recomendado:
            badge = ctk.CTkFrame(
                card, fg_color=COLORS.accent,
                corner_radius=12, height=24
            )
            badge.grid(row=0, column=0, padx=16, pady=(16, 0), sticky="w")
            ctk.CTkLabel(
                badge,
                text="  ✦ Recomendado  ",
                font=(FONTS.family, FONTS.size_xs, "bold"),
                text_color=COLORS.primary
            ).pack(padx=4, pady=2)
        else:
            ctk.CTkFrame(
                card, fg_color="transparent", height=24
            ).grid(row=0, column=0, pady=(16, 0))

        # Ícono
        ctk.CTkLabel(
            card,
            text=modelo["icono"],
            font=(FONTS.family, 42),
            text_color=fg_icono
        ).grid(row=1, column=0, pady=(12, 4))

        # Título
        ctk.CTkLabel(
            card,
            text=modelo["titulo"],
            font=(FONTS.family, FONTS.size_lg, "bold"),
            text_color=fg_titulo
        ).grid(row=2, column=0, pady=(0, 2))

        # Subtítulo
        ctk.CTkLabel(
            card,
            text=modelo["subtitulo"],
            font=(FONTS.family, FONTS.size_xs),
            text_color=fg_sub
        ).grid(row=3, column=0, pady=(0, 12))

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

        # Variables
        info_frame = ctk.CTkFrame(
            card,
            fg_color=COLORS.primary_dark if es_recomendado else COLORS.bg_main,
            corner_radius=8
        )
        info_frame.grid(row=6, column=0, sticky="ew",
                        padx=16, pady=(0, 8))

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
        ).grid(row=7, column=0, padx=16, pady=(8, 20), sticky="ew")
```

## State

### session.py

```python

```

