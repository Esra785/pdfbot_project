# pdfbot_15.py
import json
import matplotlib.pyplot as plt

# JSON dosyasını yükle
with open("emsal_stats.json", "r", encoding="utf-8") as f:
    stats = json.load(f)

# Sadece sayfa bazlı verileri filtrele
page_data = {k: v for k, v in stats.items() if k.startswith("Sayfa")}

# Grafik çizimi
plt.figure(figsize=(6,4))
plt.bar(page_data.keys(), page_data.values()) # type: ignore

plt.title("Sayfa Bazlı Özet Uzunlukları")
plt.xlabel("Sayfalar")
plt.ylabel("Özet Uzunluğu (karakter sayısı)")
plt.tight_layout()

# Kaydet
plt.savefig("emsal_summary_lengths.png")
plt.show()

print("✅ Grafik oluşturuldu: emsal_summary_lengths.png")
