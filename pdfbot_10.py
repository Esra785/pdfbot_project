# pdfbot_10.py
# LangGraph + Ollama Q&A (fallback içeren sürüm)

import json
from typing import Any, Dict, List

# LLM importu: güncel paketleri deneniyor (hangisi kuruluysa onu kullan)
try:
    from langchain_ollama import ChatOllama  # type: ignore
except Exception:
    try:
        from langchain_community.chat_models import ChatOllama  # type: ignore
    except Exception:
        try:
            from langchain.chat_models import ChatOllama  # type: ignore
        except Exception:
            ChatOllama = None  # type: ignore

# LangGraph importu: yoksa fallback yapacağız
try:
    from langgraph.graph import StateGraph  # type: ignore
    # MemorySaver genelde tip bilgisi olmuyor; try/except ile al
    try:
        from langgraph.checkpoint import MemorySaver  # type: ignore
    except Exception:
        MemorySaver = None  # type: ignore
except Exception:
    StateGraph = None  # type: ignore
    MemorySaver = None  # type: ignore

# Hangi modeli kullanacağımızı belirle 
LLM_MODEL_NAME = "gemma3:4b"

# LLM başlat (varsa)
if ChatOllama is None:
    raise RuntimeError("ChatOllama bulunamadı. lütfen 'langchain-ollama' veya 'langchain_community' paketlerini kurun.")
llm = ChatOllama(model=LLM_MODEL_NAME)  # type: ignore

# Veri kaynağı (güvenli JSON)
DATA_FILE = "emsal_safe.json"
with open(DATA_FILE, "r", encoding="utf-8") as f:
    data: List[Dict[str, Any]] = json.load(f)

# ---------- Basit retrieval fonksiyonu ----------
def retrieve_context_simple(question: str, max_chars: int = 4000) -> str:
    """Basit kelime eşleşmesiyle ilgili özet parçalarını birleştirir."""
    q = question.lower().strip()
    if not q:
        # hepsini döndür
        parts = [item.get("summary", "") for item in data]
        return "\n\n".join(parts)[:max_chars]

    # basit token eşleşme: soru kelimelerinden ilk 6'sını kullan
    tokens = [t for t in q.split() if t]
    tokens = tokens[:6]

    hits: List[str] = []
    for item in data:
        txt = (item.get("summary") or "").lower()
        # Eğer herhangi bir token summary içinde geçiyorsa al
        if any(tok in txt for tok in tokens):
            hits.append(item.get("summary", ""))

    if not hits:
        hits = [item.get("summary", "") for item in data]

    ctx = "\n\n".join(hits)
    if len(ctx) > max_chars:
        return ctx[:max_chars] + "..."
    return ctx

# ---------- LangGraph düğüm fonksiyonları ----------
# Tipleri basit dict kullanan yapı ile yazıyoruz (Pylance daha az şikayet)
def retrieve_context_node(state: Dict[str, Any]) -> Dict[str, Any]:
    question = state.get("question", "") or ""
    state["context"] = retrieve_context_simple(question)
    return state

def generate_answer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    question = state.get("question", "") or ""
    context = state.get("context", "") or ""
    prompt = f"Soru: {question}\n\nBağlam:\n{context}\n\nKısa, net ve Türkçe cevap ver:"
    # llm.invoke / llm() farklı versiyonlarda değişebilir; denemelerle uyumlu hale getiriyoruz
    try:
        # öncelikle invoke'ı dene 
        resp = llm.invoke(prompt)  # type: ignore
        answer = getattr(resp, "content", resp)
        if isinstance(answer, dict):
            # bazı implementasyonlarda dict gelebiliyor
            answer = answer.get("content") or str(answer)
    except Exception:
        try:
            # fallback: çağırma gibi davran
            resp = llm(prompt)  # type: ignore
            if isinstance(resp, str):
                answer = resp
            elif hasattr(resp, "content"):
                answer = getattr(resp, "content")
            else:
                answer = str(resp)
        except Exception as e:
            answer = f"LLM çağrısında hata: {e}"

    state["answer"] = str(answer)
    return state

# ---------- Graph oluşturma (varsa LangGraph ile) ----------
if StateGraph is not None:
    # StateGraph tipleri Pylance ile çakıştığı için # type: ignore kullanıyoruz burada
    graph = StateGraph(dict)  # type: ignore
    graph.add_node("retriever", retrieve_context_node)  # type: ignore
    graph.add_node("llm", generate_answer_node)  # type: ignore
    graph.set_entry_point("retriever")  # type: ignore
    if MemorySaver is not None:
        try:
            memory = MemorySaver()  # type: ignore
            app = graph.compile(checkpointer=memory)  # type: ignore
        except Exception:
            app = graph.compile()  # type: ignore
    else:
        app = graph.compile()  # type: ignore

    def run_query(question: str) -> str:
        state = {"question": question}
        result = app.invoke(state)  # type: ignore
        return str(result.get("answer", "") or result.get("context", "").splitlines()[0] or "")
else:
    # LangGraph yüklü değilse basit pipeline
    def run_query(question: str) -> str:
        ctx = retrieve_context_simple(question)
        state = {"question": question, "context": ctx}
        state = generate_answer_node(state)
        return str(state.get("answer", ""))

# ---------- Basit CLI ----------
if __name__ == "__main__":
    print("📖 PDF Chatbot hazır! Çıkmak için 'q' yaz.\n")
    while True:
        q = input("Sorunuzu yazın: ")
        if q.strip().lower() == "q":
            break
        ans = run_query(q)
        print("\n🤖 Cevap:", ans, "\n")
