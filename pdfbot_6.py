# pdfbot_6.py
# 2. Hafta - 2. Gün 
# emsal_focused.json (list[dict]) -> CSV + Markdown tablo

import json
import pandas as pd
from pathlib import Path

INPUT_JSON = Path("emsal_focused.json")
OUTPUT_MD = Path("emsal_focused_table.md")
OUTPUT_CSV = Path("emsal_focused_table.csv")

with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

if not isinstance(data, list):
    raise ValueError("emsal_focused.json beklenen formatta değil (list[dict] olmalı).")

rows = []
for idx, item in enumerate(data, start=1):
    page = item.get("page") or idx
    label = (item.get("label") or "Bilinmiyor").strip()
    summary = (item.get("summary") or "Özet yok").strip()
    rows.append({"Sayfa": page, "Kategori": label, "Odaklı Özet": summary})

df = pd.DataFrame(rows).fillna({"Kategori": "Bilinmiyor", "Odaklı Özet": "Özet yok"})

# CSV
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

# Markdown (tabulate gerekir)
try:
    md_table = df.to_markdown(index=False)
except Exception:
    # tabulate yoksa basit Markdown
    headers = "| " + " | ".join(df.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(df.columns)) + " |"
    body = "\n".join("| " + " | ".join(map(str, r)) + " |" for r in df.values)
    md_table = "\n".join([headers, sep, body])

with open(OUTPUT_MD, "w", encoding="utf-8") as f:
    f.write("# Emsal Karar Odaklı Özet Tablosu\n\n")
    f.write(md_table + "\n")

print("✅ Tablo oluşturuldu.")
print("Markdown:", OUTPUT_MD)
print("CSV:", OUTPUT_CSV)
