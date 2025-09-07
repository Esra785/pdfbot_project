# pdfbot_8.py
# 2. Hafta - 4. Gün
# Güvenlik testi: XSS ve injection girişimlerini temizleme

import json
import re

INPUT_JSON = "emsal_focused.json"
OUTPUT_JSON = "emsal_safe.json"

def clean_text(text: str) -> str:
    if not text:
        return "Boş içerik"
    
    # XSS / HTML script temizleme
    text = re.sub(r"<script.*?>.*?</script>", "[XSS temizlendi]", text, flags=re.IGNORECASE|re.DOTALL)
    text = re.sub(r"<.*?on\w+=.*?>", "[Zararlı etiket temizlendi]", text, flags=re.IGNORECASE)

    # SQL injection benzeri girişimler
    sql_keywords = ["DROP TABLE", "INSERT INTO", "DELETE FROM", "--", ";--", "/*", "*/", "@@", "@", "CHAR(", "CAST(", "UNION", "SELECT", "UPDATE", "EXEC"]
    for kw in sql_keywords:
        if kw.lower() in text.lower():
            text = text.replace(kw, "[SQL_TESPIT]")

    return text.strip()

with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

cleaned = []
for item in data:
    page = item.get("page", "Bilinmiyor")
    label = clean_text(item.get("label", ""))
    summary = clean_text(item.get("summary", ""))
    cleaned.append({
        "page": page,
        "label": label,
        "summary": summary
    })

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)

print("✅ Güvenlik testi tamamlandı.")
print("Temizlenmiş dosya kaydedildi:", OUTPUT_JSON)
