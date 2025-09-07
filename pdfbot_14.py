import json
import matplotlib.pyplot as plt

# JSON dosyasını oku
with open("emsal_stats.json", "r", encoding="utf-8") as f:
    stats = json.load(f)

# Veri hazırla (Türkçe key'ler kullanıldı)
sizes = [stats["Özeti Olan Sayfa"], stats["Özetsiz Sayfa"]]
labels = ["Özeti Olan", "Özetsiz"]

# Pasta grafiği
plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
plt.title("Özet Durumuna Göre Sayfa Dağılımı")
plt.axis("equal")  # Daire şeklinde olsun
plt.savefig("emsal_pie.png")
plt.show()
