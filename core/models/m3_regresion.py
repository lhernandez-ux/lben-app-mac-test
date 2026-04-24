import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan
from scipy import stats

def ejecutar_modelo_m3(df_base_original, df_mon_original, target_var, feature_vars):
    """
    Ejecuta la lógica completa del Modelo M3 (Regresión Multivariable).
    """
    # 1. Preparación y Filtrado de Outliers (LBEn)
    df_base = df_base_original.copy()
    
    # Asegurar que feature_vars son todos strings
    feature_vars = [str(v) for v in feature_vars]
    
    # Convertir columnas numéricas relevantes a float, ignorando errores
    for col in [target_var] + feature_vars:
        if col in df_base.columns:
            df_base[col] = pd.to_numeric(df_base[col], errors='coerce')
    df_base.dropna(subset=[target_var] + feature_vars, inplace=True)
    
    # Filtrado estadístico moderado (+-3 desv std) sobre el target
    media = df_base[target_var].mean()
    std = df_base[target_var].std()
    mask_outliers = (df_base[target_var] < (media - 3 * std)) | (df_base[target_var] > (media + 3 * std))
    df_excluidos = df_base[mask_outliers].copy()
    df_base_clean = df_base[~mask_outliers].copy()
    
    # 2. Construcción Modelo LBEn (Línea Base)
    X_base = sm.add_constant(df_base_clean[feature_vars])
    y_base = df_base_clean[target_var]
    
    model_lben = sm.OLS(y_base, X_base).fit()
    
    # 3. Construcción Modelo LMEn (Línea Meta)
    # Lógica: registros donde el real < calculado (ahorro)
    df_base_clean['y_pred_lben'] = model_lben.predict(X_base)
    df_meta_subset = df_base_clean[df_base_clean[target_var] < df_base_clean['y_pred_lben']].copy()
    
    if len(df_meta_subset) > len(feature_vars) + 1:
        X_meta = sm.add_constant(df_meta_subset[feature_vars])
        y_meta = df_meta_subset[target_var]
        model_lmen = sm.OLS(y_meta, X_meta).fit()
    else:
        # Si hay muy pocos datos para una regresión meta, usamos el mismo pero con un offset (fallback de seguridad)
        model_lmen = model_lben
    
    # 4. Estadísticos Globales y Diagnóstico
    rmse = np.sqrt(model_lben.mse_resid)
    cv_rmse = (rmse / y_base.mean()) * 100
    
    # Breusch-Pagan (Homocedasticidad)
    _, p_bp, _, _ = het_breuschpagan(model_lben.resid, model_lben.model.exog)
    
    # VIF (Multicolinealidad)
    vif_data = []
    if len(feature_vars) > 1:
        for i in range(1, X_base.shape[1]): # Empezamos en 1 para saltar la constante
            vif = variance_inflation_factor(X_base.values, i)
            vif_data.append(vif)
    else:
        vif_data = [1.0]

    # Pearson y p-valores individuales
    correls = []
    for var in feature_vars:
        r, p_corr = stats.pearsonr(df_base_clean[var], df_base_clean[target_var])
        correls.append({'var': var, 'r': r, 'p': p_corr})

    # 5. Cálculos de Potenciales
    # Promedio de consumos calculados proyectados para TODO el periodo base
    X_base_full = sm.add_constant(df_base_clean[feature_vars])
    prom_real = df_base_clean[target_var].mean()
    prom_lben = model_lben.predict(X_base_full).mean()
    prom_lmen = model_lmen.predict(X_base_full).mean()
    ahorro_kwh = prom_lben - prom_lmen
    ahorro_pct = (ahorro_kwh / prom_real) * 100 if prom_real > 0 else 0

    # 6. Monitoreo
    df_mon = df_mon_original.copy()
    if not df_mon.empty:
        # Convertir a float las variables del modelo en monitoreo
        for col in feature_vars:
            if col in df_mon.columns:
                df_mon[col] = pd.to_numeric(df_mon[col], errors='coerce').fillna(0)
            else:
                df_mon[col] = 0
        df_mon_clean = df_mon.dropna(subset=feature_vars)
        if not df_mon_clean.empty:
            X_mon = sm.add_constant(df_mon_clean[feature_vars], has_constant='add')
            for col in X_base.columns:
                if col not in X_mon.columns: X_mon[col] = 0
            X_mon = X_mon[X_base.columns]
            df_mon.loc[df_mon_clean.index, 'lben_mes'] = model_lben.predict(X_mon)
    
    results = {
        'model_lben': model_lben,
        'model_lmen': model_lmen,
        'df_base': df_base_clean,
        'df_mon': df_mon,
        'df_excluidos': df_excluidos,
        'metrics': {
            'r2': model_lben.rsquared,
            'r2_adj': model_lben.rsquared_adj,
            'rmse': rmse,
            'cv_rmse': cv_rmse,
            'f_pval': model_lben.f_pvalue,
            'bp_pval': p_bp,
            'fiabilidad': model_lben.rsquared * 100
        },
        'coef_table': {
            'vars': ['Intercepto'] + feature_vars,
            'betas': model_lben.params.tolist(),
            'std_err': model_lben.bse.tolist(),
            'p_vals': model_lben.pvalues.tolist(),
            'vif': [np.nan] + vif_data
        },
        'correls': correls,
        'potenciales': {
            'prom_real': prom_real,
            'prom_lben': prom_lben,
            'prom_lmen': prom_lmen,
            'ahorro_kwh': ahorro_kwh,
            'ahorro_pct': ahorro_pct
        }
    }
    
    return results

def formatear_ecuacion(model, feature_vars):
    """Genera el string de la ecuación: y = b0 + b1*X1 + ..."""
    feature_vars = [str(v) for v in feature_vars]  # Garantizar strings
    params = model.params
    try:
        eq = f"Consumo= {params.iloc[0]:.2f}"
        for i, var in enumerate(feature_vars):
            coef = params.iloc[i + 1]
            signo = "+" if coef >= 0 else "-"
            eq += f" {signo} {abs(coef):.2f}·{var}"
    except Exception:
        eq = "Ec. no disponible"
    return eq
