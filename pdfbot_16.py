# pdfbot_16.py
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Bilgisayardaki font dosyasını kaydet
pdfmetrics.registerFont(TTFont("ArialTR", r"C:\Windows\Fonts\arial.ttf"))

# JSON oku
with open("emsal_stats.json", "r", encoding="utf-8") as f:
    stats = json.load(f)

doc = SimpleDocTemplate("emsal_report.pdf", pagesize=A4)
elements = []

styles = getSampleStyleSheet()
styles["Normal"].fontName = "ArialTR"   # ✅ Burada Türkçe fontu kullandırıyoruz
styles["Title"].fontName = "ArialTR"

title = Paragraph("📊 Emsal Karar Analizi – İstatistik Raporu", styles["Title"])
elements.append(title)
elements.append(Spacer(1, 20))

data = [["Özellik", "Değer"]]
for key, value in stats.items():
    data.append([key, str(value)])

table = Table(data, colWidths=[200, 200])
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9ead3")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("FONTNAME", (0, 0), (-1, -1), "ArialTR"),  # ✅ Tabloya da uygula
    ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
    ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
    ("GRID", (0, 0), (-1, -1), 1, colors.black),
]))
elements.append(table)
elements.append(Spacer(1, 30))

desc = Paragraph(
    "Bu rapor, yüklenen PDF dosyası üzerinden çıkarılan istatistikleri içermektedir. "
    "Sayfa bazlı özet uzunlukları analiz edilmiş ve grafik ile görselleştirilmiştir.",
    styles["Normal"]
)
elements.append(desc)
elements.append(Spacer(1, 20))

try:
    img = Image("emsal_summary_lengths.png", width=400, height=250)
    elements.append(img)
except Exception:
    elements.append(Paragraph("⚠️ Grafik bulunamadı.", styles["Normal"]))

doc.build(elements)

print("✅ Rapor oluşturuldu: emsal_report.pdf (Türkçe font: Arial)")
