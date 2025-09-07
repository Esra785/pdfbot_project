# pdfbot_1.py
# 1. Gün: PDF okuma ve JSON çıktısı oluşturma
# Bu kod, Emsal-Karar.pdf dosyasını okuyup sayfa bazında metin çıkarır,
# başlıkları font büyüklüğüne veya BÜYÜK HARF yazımına göre tespit etmeye çalışır,
# ve sonuçları emsal_parsed.json dosyasına kaydeder.

import json
from pathlib import Path

# PDF giriş ve JSON çıkış dosyalarının yolu
INPUT_PDF = Path("Emsal-Karar.pdf")       
OUTPUT_JSON = Path("emsal_parsed.json")    

# Çıktı için temel yapı
result = {"source": str(INPUT_PDF), "parser_used": None, "pages": []}

# Önce PyMuPDF (fitz) deneyelim
try:
    import fitz  # PyMuPDF
    result["parser_used"] = "pymupdf"
except Exception:
    fitz = None

if fitz:
    # PyMuPDF ile PDF'i aç
    doc = fitz.open(str(INPUT_PDF))
    for i, page in enumerate(doc): # type: ignore
        page_text = page.get_text("text") or ""
        page_dict = {"page_number": i+1, "text": page_text, "blocks": []}

        # Blok bazlı detayları al
        page_dict_raw = page.get_text("dict")
        for block in page_dict_raw.get("blocks", []):
            if block.get("type") == 0:  # metin bloğu
                block_text = ""
                max_font_size = 0
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        block_text += span.get("text", "")
                        if span.get("size", 0) > max_font_size:
                            max_font_size = span.get("size", 0)
                page_dict["blocks"].append({
                    "text": block_text.strip(),
                    "max_font_size": max_font_size,
                    "bbox": block.get("bbox")
                })
        result["pages"].append(page_dict)
    doc.close()

else:
    # Eğer PyMuPDF yoksa pdfplumber deneyelim
    try:
        import pdfplumber
        result["parser_used"] = "pdfplumber"
    except Exception:
        pdfplumber = None

    if pdfplumber:
        with pdfplumber.open(str(INPUT_PDF)) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                result["pages"].append({"page_number": i+1, "text": text})
    else:
        # Son çare olarak pypdf (PyPDF2)
        try:
            from pypdf import PdfReader # type: ignore
        except Exception:
            try:
                from PyPDF2 import PdfReader # type: ignore
            except Exception:
                PdfReader = None

        if PdfReader is None:
            raise RuntimeError("Hiçbir PDF parser bulunamadı. Lütfen pymupdf veya pdfplumber kur.")
        
        reader = PdfReader(str(INPUT_PDF))
        for i, page in enumerate(reader.pages):
            txt = page.extract_text() or ""
            result["pages"].append({"page_number": i+1, "text": txt})

# Başlık tespiti (font büyüklüğüne veya büyük harf yazımına göre)
for page in result["pages"]:
    headings = []
    blocks = page.get("blocks", [])
    if blocks:
        sizes = [b.get("max_font_size", 0) for b in blocks if b.get("max_font_size")]
        median = sorted(sizes)[len(sizes)//2] if sizes else 0
        threshold = median * 1.1 if median else 12
        for b in blocks:
            if b.get("max_font_size", 0) >= threshold and len(b.get("text","")) > 3:
                headings.append({
                    "type": "font_size",
                    "text": b.get("text"),
                    "font_size": b.get("max_font_size")
                })
    else:
        lines = page.get("text","").splitlines()
        for ln in lines:
            ln_stripped = ln.strip()
            if len(ln_stripped) > 3 and ln_stripped.isupper():
                headings.append({"type": "uppercase", "text": ln_stripped})
    page["headings"] = headings

# JSON dosyasına yaz
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# Konsola kısa önizleme
print("Parser kullanılan kütüphane:", result.get("parser_used"))
if result["pages"]:
    first = result["pages"][0]
    print(f"Sayfa 1 (ilk 400 karakter):\n{first.get('text','')[:400]}\n")
    print("Sayfa 1 başlıklar:", first.get("headings", []))
else:
    print("PDF'den hiçbir sayfa çıkarılamadı.")

print("JSON dosyası kaydedildi:", OUTPUT_JSON)
