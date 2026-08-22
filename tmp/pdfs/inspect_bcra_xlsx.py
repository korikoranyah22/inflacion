import pathlib
import re

import pandas as pd


path = pathlib.Path(r"data/fuentes/pendulo_poder_economico/bcra/InfBanc0526.xlsx")
book = pd.ExcelFile(path)
for sheet in book.sheet_names:
    data = pd.read_excel(path, sheet_name=sheet, header=None, dtype=object)
    for index, row in data.iterrows():
        text = " | ".join(str(value) for value in row.tolist() if pd.notna(value))
        if re.search(r"ROA|ROE|Rentabilidad|resultado total", text, re.I):
            print(sheet, index + 1, text[:1600])
