# 📑 PDFBot – Emsal Karar Analiz ve Chatbot Projesi

## 🔎 Proje Amacı
Bu proje, **hukuki PDF dosyalarının** otomatik olarak:
- Metin çıkarılması 📝
- Özetlenmesi 📋
- Sınıflandırılması 🏷️
- Raporlanması 📊
- Görselleştirilmesi 📈
- Chatbot üzerinden soru-cevap yapılabilmesi 🤖  

işlevlerini bir araya getiren **LLM tabanlı** bir uygulamadır.  
Amaç, hukuk alanındaki metin yoğun belgeleri daha **erişilebilir ve anlaşılır** hale getirmektir.

---

## 📂 Proje Yapısı

- `pdfbot_final.py` → Tek dosyada proje çalıştırma (chatbot dahil)  
- `pdfbot_1.py - pdfbot_17.py` → Haftalık geliştirme aşamalarını içeren modüller  
- `data/` → Örnek PDF dosyaları (örn: `Emsal-Karar.pdf`)  
- `*.json` → Ara çıktı dosyaları (parsed, summarized, classified vb.)  
- `*.md` → Markdown raporları  
- `*.csv` → Tablo çıktıları  
- `*.pptx` → Sunum dosyaları  
- `*.pdf` → Rapor dosyaları  

---

## 🚀 Kurulum

1. Projeyi klonla:
   ```bash
   git clone https://github.com/Esra785/pdfbot_project.git
   cd pdfbot_project
