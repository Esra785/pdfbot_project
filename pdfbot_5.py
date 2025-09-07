# pdfbot_5.py
# 2. Hafta - 1. Gün 
# - Ollama format: "json" ile JSON çıkışı zorunlu
# - Uzun metinleri kırpma (bağlam aşımı önleme)
# - JSON parse edilemezse regex ile ayıklama ve heuristik yedekleme

import re
import json
import fitz  # PyMuPDF
import requests
from pathlib import Path

PDF_FILE = "Emsal-Karar.pdf"
OUTPUT_JSON = "emsal_focused.json"

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:4b"

# --- Heuristik etiketleme (LLM boş dönerse) ---
def guess_label(text: str) -> str:
    t = text.lower()
    if ("yargıtay" in t and "hukuk dairesi" in t) or "t.c." in t:
        return "Mahkeme bilgisi"
    if ("esas" in t) or ("karar no" in t) or ("dosya" in t):
        return "Dosya bilgisi"
    if ("dava" in t) or ("uyușmazlık" in t) or ("uyuşmazlık" in t) or ("talep" in t) or ("arabulucu" in t):
        return "Dava konusu"
    if ("hüküm" in t) or ("sonuç" in t) or ("karar" in t) or ("redd" in t) or ("kabul" in t):
        return "Karar özeti"
    return "Bilinmiyor"

def naive_summary(text: str, max_len: int = 300) -> str:
    s = " ".join(text.split())
    return s[:max_len] + ("..." if len(s) > max_len else "")

# --- Ollama çağrısı ---
def call_ollama(prompt: str) -> dict | None:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",     # JSON çıkışı ZORLA
        "options": {"num_ctx": 4096}
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        # Ollama genellikle "response" içinde döndürür; yine de alternatif anahtarları deneriz
        raw = data.get("response") or data.get("output") or data.get("message") or ""
        if isinstance(raw, dict):
            return raw
        if isinstance(raw, str) and raw.strip():
            # Direkt JSON parse dene
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                # İçinden JSON gövdesi ayıkla
                m = re.search(r'(\{.*?\}|\[.*?\])', raw, re.DOTALL)
                if m:
                    try:
                        return json.loads(m.group(1))
                    except json.JSONDecodeError:
                        return None
        # Hata döndüyse göster
        if data.get("error"):
            print("⚠️ Ollama hata:", data["error"])
        return None
    except Exception as e:
        print("⚠️ Ollama istisnası:", e)
        return None

# --- PDF oku ve sayfa sayfa işle ---
doc = fitz.open(PDF_FILE)
results: list[dict] = []

for i in range(len(doc)):
    page_no = i + 1
    text = doc[i].get_text("text") or "" # type: ignore
    # Küçük model için metni kısalt (bağlam taşmasın)
    text_for_llm = text.replace("\x00", " ").strip()
    if len(text_for_llm) > 4000:
        text_for_llm = text_for_llm[:4000]

    prompt = f"""
Sen bir hukuk asistanısın. Aşağıdaki sayfa metnini oku ve JSON formatında KESİNLİKLE şu üç alanı doldur:

- "page": tam sayı (örnek: {page_no})
- "label": şu seçeneklerden en uygun olanı SEÇ → ["Mahkeme bilgisi", "Dosya bilgisi", "Dava konusu", "Karar özeti"]
- "summary": kısa ve anlamlı bir özet (en az 1 cümle, asla boş bırakma)

YANITIN: yalnızca GEÇERLİ JSON olsun. Fazladan açıklama yazma.

--- SAYFA {page_no} METİN ---
{text_for_llm}
"""

    parsed = call_ollama(prompt)

    if isinstance(parsed, dict) and {"page", "label", "summary"} <= set(parsed.keys()):
        # LLM düzgün verdi
        try:
            # Tür temizliği
            page_val = int(parsed.get("page", page_no) or page_no)
        except Exception:
            page_val = page_no
        label_val = str(parsed.get("label") or "").strip() or guess_label(text)
        summary_val = str(parsed.get("summary") or "").strip() or naive_summary(text)
        results.append({
            "page": page_val,
            "label": label_val,
            "summary": summary_val
        })
    elif isinstance(parsed, list) and parsed:
        # LLM liste döndürdüyse ilk geçerli öğeyi al
        found = False
        for obj in parsed:
            if isinstance(obj, dict) and {"page", "label", "summary"} <= set(obj.keys()):
                try:
                    p = int(obj.get("page", page_no) or page_no)
                except Exception:
                    p = page_no
                lab = str(obj.get("label") or "").strip() or guess_label(text)
                summ = str(obj.get("summary") or "").strip() or naive_summary(text)
                results.append({"page": p, "label": lab, "summary": summ})
                found = True
                break
        if not found:
            # Heuristik yedek
            results.append({
                "page": page_no,
                "label": guess_label(text),
                "summary": naive_summary(text) if text.strip() else "Özet bulunamadı"
            })
    else:
        # LLM hiçbir şey veremediyse heuristik yedek
        results.append({
            "page": page_no,
            "label": guess_label(text),
            "summary": naive_summary(text) if text.strip() else "Özet bulunamadı"
        })

# Kaydet
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("✅ Odaklı özetleme tamamlandı.")
print("Yeni dosya:", OUTPUT_JSON)
