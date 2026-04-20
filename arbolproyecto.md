# Estructura del Proyecto: LBEn Resol 016/2024

```text
LBEn_APP_Resol016/
├── app.py                      # Punto de entrada principal
├── requirements.txt            # Dependencias del proyecto
├── arbolproyecto.md            # Este archivo
├── codigoproyecto.md           # Resumen de todo el código fuente
├── core/                       # Lógica de negocio y motores estadísticos
│   ├── exploratorio.py         # Motor de análisis exploratorio (VIF, Pearson)
│   ├── io_excel.py             # Lector/Escritor de plantillas Excel
│   ├── session.py              # Gestión de estado de la aplicación
│   ├── utils.py                # Utilidades generales
│   └── models/                 # Modelos de Línea Base
│       ├── promedio.py         # Modelo M1
│       ├── cociente.py         # Modelo M2
│       └── m3_regresion.py     # Modelo M3 (Regresión Multivariable)
├── ui/                         # Interfaz de Usuario (CustomTkinter)
│   ├── main_window.py          # Ventana principal y navegación
│   ├── theme.py                # Definiciones de colores y fuentes
│   └── pages/                  # Pantallas del flujo
│       ├── home.py                 # Inicio
│       ├── seleccion_modelo.py     # Selector de flujo
│       ├── exploratorio_carga.py   # Carga de datos exploratorios
│       ├── exploratorio_resultados.py # Dashboard exploratorio
│       ├── m1_resultados.py        # Dashboard M1
│       ├── m2_resultados.py        # Dashboard M2
│       └── m3_resultados.py        # Dashboard M3 (Con alertas de colinealidad)
└── data/                       # Plantillas y datos de referencia
    └── (Plantillas Excel)
```
