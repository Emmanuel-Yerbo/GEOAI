import pandas as pd
from pathlib import Path

BASE = Path(r"c:\YERBO\Desktop\CODING\POPULATION DATA")
data_dir = BASE / "data"

for excel_file in data_dir.glob("*.xlsx"):
    print(f"\nFile: {excel_file.name}")
    try:
        xl = pd.ExcelFile(excel_file)
        print(f"  Sheets: {xl.sheet_names}")
        for sheet in xl.sheet_names:
            df = xl.parse(sheet, nrows=5)
            print(f"    Sheet '{sheet}': columns={df.columns.tolist()[:10]}")
    except Exception as e:
        print(f"  Error reading: {e}")
