import pandas as pd
from pathlib import Path

BASE = Path(r"c:\YERBO\Desktop\CODING\POPULATION DATA")
excel_file = BASE / "data" / "gha_admpop_2021.xlsx"

xl = pd.ExcelFile(excel_file)
for sheet in ['gha_admpop_adm2_2021', 'gha_admpop_adm2PS_2021']:
    df = xl.parse(sheet)
    print(f"\nSheet: {sheet}")
    print(f"  Shape: {df.shape}")
    print(f"  Null count for ADM2_PCODE: {df['ADM2_PCODE'].isnull().sum()}")
    print(f"  Unique ADM2_PCODE count: {df['ADM2_PCODE'].nunique()}")
    print(f"  Unique ADM2_EN count: {df['ADM2_EN'].nunique()}")
    print(f"  First 5 rows:")
    print(df[['ADM1_EN', 'ADM2_EN', 'ADM2_PCODE', 'T_TL']].head(5).to_string())
