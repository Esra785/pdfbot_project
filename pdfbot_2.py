# pdfbot_2.py
# 2. Gün : PDF metinlerini Ollama (Gemma3:4b) ile sınıflandırma ve özetleme
# Bu sürümde LLM yanıtlarını JSON formatında temizliyoruz.

import json
import re
import requests
from pathlib import Path

# Girdi ve çıktı dosyaları
INPUT_JSON = Path("emsal_parsed.json")
OUTPUT_JSON = Path("emsal_classified.json")

# Ollama API ayarları
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:4b"  

def query_ollama(prompt: str) -> str:
    """
    Ollama'ya prompt gönderir ve yanıtı döner.
    """
    payload = {
        "model": MODEL,
        "prompt": prompt
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, stream=True)
        response.raise_for_status()
        # Ollama yanıtı satır satır döner
        output_text = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:
                    output_text += data["response"]
        return output_text.strip()
    except Exception as e:
        print("Ollama hatası:", e)
        return "LLM yanıtı alınamadı."

def classify_and_summarize(text: str):
    """
    Metni Ollama'ya göndererek sınıflandırma ve özet alır.
    """
    prompt = f"""
    Aşağıdaki metni oku ve JSON formatında yanıt ver:
    {{
      "label": "metnin hangi kategoriye ait olduğunu yaz (örn: Dosya bilgisi, Mahkeme bilgisi, Taraf bilgisi, Dava konusu, Karar sonucu, Genel bilgi)",
      "summary": "metnin en fazla 20 kelimelik özeti"
    }}

    Metin:
    {text}
    """
    response = query_ollama(prompt)

    try:
        # Eğer yanıtın içinde JSON blok varsa onu ayıklar
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            return parsed
        else:
            parsed = json.loads(response)
            return parsed
    except:
        return {"label": "Bilinmiyor", "summary": response[:80] + "..."}

# JSON'u yükle
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

# Her sayfa ve blok üzerinde çalışır
for page in data["pages"]:
    classified_blocks = []
    blocks = page.get("blocks", [])
    if not blocks:
        for line in page.get("text", "").splitlines():
            if len(line.strip()) > 10:
                result = classify_and_summarize(line.strip())
                classified_blocks.append({
                    "text": line.strip(),
                    **result
                })
    else:
        for b in blocks:
            if len(b.get("text","").strip()) > 10:
                result = classify_and_summarize(b["text"].strip())
                classified_blocks.append({
                    "text": b["text"].strip(),
                    **result
                })
    page["classified"] = classified_blocks

# Yeni JSON'a yaz
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Sınıflandırma ve özetleme tamamlandı.")
print("Yeni dosya oluşturuldu:", OUTPUT_JSON)
