import pandas as pd

def inspect_m1_simple(path):
    print(f"--- Inspeccionando Plantilla M1: {path} ---")
    try:
        # Leer Periodo_Base
        df_base = pd.read_excel(path, sheet_name='Periodo_Base', header=None, nrows=10)
        print("\nHoja: Periodo_Base (Primeras 10 filas)")
        for idx, row in df_base.iterrows():
            print(f"Fila {idx}: {list(row[1:13])}") # Columnas B a M

        # Leer Modelo_LBEn
        df_model = pd.read_excel(path, sheet_name='Modelo_LBEn', header=None, nrows=10)
        print("\nHoja: Modelo_LBEn (Celdas D5-D7)")
        print(f"D5: {df_model.iloc[4, 3]}")
        print(f"D6: {df_model.iloc[5, 3]}")
        print(f"D7: {df_model.iloc[6, 3]}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_m1_simple("k:/gdrive_luisflorez/Mi unidad/PROYECTOS_LF/ProyectosE2/LBEn_EDIF_app/LBEn_APP_Resol016/contexto/consumo/Plantilla_LBEn_M1_modelo.xlsx")
