# pdfbot_13.py 
import json

# Odaklı özet dosyasını oku
with open("emsal_focused.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Sayfa sayısı
total_pages = len(data)

# Sayfa bazlı uzunluklar
page_summary_lengths = {}

# Özeti olan ve olmayan sayfalar
pages_with_summary = 0
pages_without_summary = 0
summary_lengths = []

for item in data:
    page = item.get("page", "Bilinmiyor")
    summary = item.get("summary", "")
    length = len(summary.strip())

    # Sayfa bazlı uzunluk kaydet
    page_summary_lengths[f"Sayfa {page}"] = length

    if length > 0:
        pages_with_summary += 1
        summary_lengths.append(length)
    else:
        pages_without_summary += 1

# Genel istatistikler
stats = {
    "Toplam Sayfa": total_pages,
    "Özeti Olan Sayfa": pages_with_summary,
    "Özetsiz Sayfa": pages_without_summary,
    "Ortalama Özet Uzunluğu": sum(summary_lengths) / len(summary_lengths) if summary_lengths else 0,
    "En Kısa Özet Uzunluğu": min(summary_lengths) if summary_lengths else 0,
    "En Uzun Özet Uzunluğu": max(summary_lengths) if summary_lengths else 0
}

# İki yapıyı birleştir (hem genel hem sayfa bazlı)
final_stats = {**stats, **page_summary_lengths}

# JSON kaydet
with open("emsal_stats.json", "w", encoding="utf-8") as f:
    json.dump(final_stats, f, ensure_ascii=False, indent=2)

print("📊 PDF İstatistikleri:")
for k, v in stats.items():
    print(f"- {k}: {v}")

print("\n📄 Sayfa Bazlı Uzunluklar:")
for k, v in page_summary_lengths.items():
    print(f"- {k}: {v}")

print("\n✅ İstatistikler kaydedildi: emsal_stats.json")
