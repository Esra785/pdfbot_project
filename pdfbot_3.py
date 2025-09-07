# pdfbot_3.py
# 3. Gün: Sınıflandırılmış veriyi rapor formatına dönüştürme (Markdown + CSV)

import json
import pandas as pd
from pathlib import Path

# Girdi ve çıktı dosyaları
INPUT_JSON = Path("emsal_classified.json")
OUTPUT_MD = Path("emsal_report.md")
OUTPUT_CSV = Path("emsal_report.csv")

# JSON'u yükle
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

# Tüm blokları tek listeye topla
records = []
for page in data["pages"]:
    for block in page.get("classified", []):
        records.append({
            "page": page["page_number"],
            "text": block["text"],
            "label": block["label"],
            "summary": block["summary"]
        })

# DataFrame oluştur
df = pd.DataFrame(records)

# CSV çıktısı
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

# Markdown çıktısı
with open(OUTPUT_MD, "w", encoding="utf-8") as f:
    f.write("# Emsal Karar Raporu\n\n")
    f.write("Bu rapor, PDF içeriğinin sınıflandırılmış ve özetlenmiş halidir.\n\n")

    # Kategorilere göre grupla
    for label, group in df.groupby("label"):
        f.write(f"## {label}\n\n")
        for _, row in group.iterrows():
            f.write(f"- **Sayfa {row['page']}** → {row['summary']}\n")
        f.write("\n")

print("✅ Rapor üretildi.")
print("Markdown dosyası:", OUTPUT_MD)
print("CSV dosyası:", OUTPUT_CSV)
