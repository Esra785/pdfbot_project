# pdfbot_4.py
# 4. Gün : Markdown raporunu PDF formatına dönüştürme
# Türkçe karakterler için Arial fontu eklendi 

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path

# Türkçe karakter destekli fontu kaydet (Arial kullanıyoruz)
pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))

# Girdi / çıktı dosyaları
INPUT_MD = Path("emsal_report.md")
OUTPUT_PDF = Path("emsal_report.pdf")

# PDF stil ayarları
styles = getSampleStyleSheet()
style_normal = styles["Normal"]
style_heading = styles["Heading2"]

# Fontu Türkçe destekli font olarak ayarla
style_normal.fontName = "Arial"
style_heading.fontName = "Arial"

# PDF belgesi
doc = SimpleDocTemplate(str(OUTPUT_PDF))
elements = []

# Markdown dosyasını oku ve PDF'e dönüştür
with open(INPUT_MD, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line.startswith("# "):  # ana başlık
            elements.append(Paragraph(line[2:], styles["Heading1"]))
            elements.append(Spacer(1, 12))
        elif line.startswith("## "):  # alt başlık
            elements.append(Paragraph(line[3:], style_heading))
            elements.append(Spacer(1, 8))
        elif line.startswith("- "):  # liste öğesi
            elements.append(Paragraph(line, style_normal))
            elements.append(Spacer(1, 4))
        elif line:
            elements.append(Paragraph(line, style_normal))
            elements.append(Spacer(1, 6))

# PDF oluştur
doc.build(elements)
print("✅ PDF raporu oluşturuldu:", OUTPUT_PDF)
