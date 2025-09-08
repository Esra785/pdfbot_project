📘 PDFBot – Hukuk PDF Analiz ve Chatbot Projesi

Bu proje, hukuk PDF dosyalarının okunması, sınıflandırılması, özetlenmesi ve raporlanmasını sağlayan bir sistemdir.
Ayrıca kullanıcılar, yüklenen PDF içeriği üzerinde chatbot aracılığıyla soru-cevap yapabilir.

🚀 Özellikler

📄 PDF okuma ve JSON formatında ayrıştırma

🏷️ LLM (Ollama) ile içerik sınıflandırma ve özet çıkarma

📊 İstatistiksel analiz (sayfa bazlı özet uzunlukları)

📈 Grafiksel raporlama (matplotlib)

📑 PDF ve PowerPoint rapor üretimi

💬 Chatbot entegrasyonu (LangGraph + Ollama)

⚙️ Kurulum

Depoyu klonlayın:

git clone https://github.com/Esra785/pdfbot_project.git
cd pdfbot_project


Sanal ortam oluşturun:

python -m venv venv
.\venv\Scripts\activate


Gerekli bağımlılıkları yükleyin:

pip install -r requirements.txt


Ollama üzerinde modeli indirin:

ollama pull gemma3:4b

▶️ Kullanım

Proje tek bir dosyadan yönetilir:

python pdfbot_final.py <komut>

Desteklenen komutlar:

chat → PDF chatbot’u başlatır

report → PDF raporu üretir (PDF formatında)

stats → JSON istatistiklerini çıkarır

graph → Özet uzunluklarını grafikle gösterir

presentation → PowerPoint sunumu üretir

Örnek:

python pdfbot_final.py chat

📂 Çıktılar

parsed.json → Ayrıştırılmış PDF metni

summarized.json → LLM özetleri

emsal_report.pdf → PDF raporu

emsal_presentation.pptx → PowerPoint sunumu

emsal_stats.json → İstatistikler

emsal_summary_lengths.png → Grafik

🛠️ Teknolojiler

Python 3.11+

PyMuPDF / pdfplumber → PDF işleme

Pandas / Matplotlib → Veri analizi ve görselleştirme

ReportLab / Python-pptx → Raporlama ve sunum

LangChain / LangGraph / Ollama → LLM entegrasyonu