import openpyxl
import os
import sys

print("Iniciando script...")
path = 'data/Plantilla_LBEn_M3_modelo.xlsx'
if not os.path.exists(path):
    print(f"ERROR: No existe {os.path.abspath(path)}")
    sys.exit(1)

print(f"Cargando {path}...")
try:
    wb = openpyxl.load_workbook(path)
    print("Cargado exitosamente.")
    for name in wb.sheetnames:
        print(f"Hoja: {name}")
        ws = wb[name]
        ranges = list(ws.merged_cells.ranges)
        print(f"Encontrados {len(ranges)} rangos combinados.")
        for r in ranges:
            print(f" - {r}")
except Exception as e:
    print(f"EXCEPCIÓN: {e}")
    sys.exit(1)
print("Fin del script.")
