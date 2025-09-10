import os, glob, math
from typing import TypedDict, List, Dict, Any
import numpy as np
import pdfplumber

# LangGraph / LangChain
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage

# ==== AYARLAR ====
BASE_URL = "http://localhost:11434"
CHAT_MODEL = "gemma3:4b"            # <-- istenen LLM
EMBED_MODEL = "nomic-embed-text:latest"    # <-- Ollama embedding modeli
PDF_GLOBS = ["Emsal-Karar.pdf", "*.pdf"]  # önce Emsal-Karar, yoksa klasördeki tüm pdf’ler
CHUNK_SIZE = 900
CHUNK_OVERLAP = 120
TOP_K = 5
MIN_SCORE = 0.22  # alaka eşiği (0-1)

# ==== BASIT PARÇALAYICI ====
def split_text(text: str, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP) -> List[str]:
    text = " ".join(text.split())
    if not text:
        return []
    chunks, start = [], 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        # cümle sonuna doğru kırpmaya çalış:
        cut = end
        for i in range(end, start, -1):
            if text[i-1] in ".!?\n" and (i - start) >= chunk_size * 0.7:
                cut = i
                break
        chunk = text[start:cut]
        chunks.append(chunk.strip())
        if cut >= len(text):
            break
        start = max(0, cut - overlap)
    return [c for c in chunks if c]

# ==== PDF OKUMA ====
def load_pdfs() -> List[Dict[str, Any]]:
    paths = []
    for pat in PDF_GLOBS:
        paths.extend([p for p in glob.glob(pat) if os.path.isfile(p)])
    # Emsal-Karar varsa yalnız onu kullan
    paths = list(dict.fromkeys(paths))  # unique & order
    if "Emsal-Karar.pdf" in paths:
        paths = ["Emsal-Karar.pdf"]

    docs = []
    for path in paths:
        try:
            with pdfplumber.open(path) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    txt = page.extract_text() or ""
                    if txt.strip():
                        docs.append({"path": path, "page": i, "text": txt})
        except Exception as e:
            print(f"[uyarı] {path} okunamadı: {e}")
    return docs

# ==== İNDEKS (embedding + cosine) ====
class SimpleIndex:
    def __init__(self, chunks: List[Dict[str, Any]], embed):
        self.chunks = chunks
        self.embed = embed
        texts = [c["text"] for c in self.chunks]
        vecs = self.embed.embed_documents(texts) if texts else []
        self.mat = np.array(vecs, dtype=np.float32) if vecs else np.zeros((0, 768), dtype=np.float32)
        self.norm = np.linalg.norm(self.mat, axis=1, keepdims=True) + 1e-8
        self.unit = self.mat / self.norm

    def search(self, query: str, k: int = TOP_K, min_score: float = MIN_SCORE):
        if self.unit.shape[0] == 0:
            return []
        q = np.array(self.embed.embed_query(query), dtype=np.float32)
        q = q / (np.linalg.norm(q) + 1e-8)
        sims = self.unit @ q
        idx = np.argsort(-sims)[:k]
        results = []
        for i in idx:
            score = float(sims[i])
            if score < min_score:
                continue
            item = dict(self.chunks[i])
            item["score"] = score
            results.append(item)
        return results

def build_index():
    raw = load_pdfs()
    # sayfa bazlı parçaları CHUNK’a böl
    chunks = []
    for r in raw:
        for part in split_text(r["text"]):
            chunks.append({"path": r["path"], "page": r["page"], "text": part})
    embed = OllamaEmbeddings(model=EMBED_MODEL, base_url=BASE_URL)
    return SimpleIndex(chunks, embed)

# Global index ve LLM
INDEX = build_index()
LLM = ChatOllama(model=CHAT_MODEL, base_url=BASE_URL, temperature=0)

# ==== LANGGRAPH STATE ====
class State(TypedDict, total=False):
    question: str
    context: List[Dict[str, Any]]
    answer: str
    done: bool

SYS_PROMPT = (
    "Aşağıdaki PDF alıntılarını KAYNAK olarak kullan. "
    "Yalnız bu alıntılara dayalı, TÜRKÇE ve kısa bir yanıt ver. "
    "Kaynaklarda yoksa 'Bu soruya ilişkin bilgi, elimdeki emsal kararda yer almıyor.' de. "
    "Uydurma yapma. Mümkünse sayfa numarası belirt."
)

def format_context(ctx: List[Dict[str, Any]]) -> str:
    lines = []
    for c in ctx:
        src = os.path.basename(c["path"])
        lines.append(f"(s:{src} p:{c['page']} sk:{c['score']:.2f}) {c['text']}")
    return "\n\n".join(lines) if lines else "—"

# ==== NODLAR ====
def retrieve_node(state: State) -> State:
    q = (state.get("question") or "").strip()
    ctx = INDEX.search(q) if q else []
    return {"context": ctx}  # <- State’e yazıyor

def generate_node(state: State) -> State:
    q = (state.get("question") or "").strip()
    ctx = state.get("context") or []
    if not q:
        return {"answer": "Soru boş olamaz.", "done": True}

    # bağlam boşsa direkt negatif cevap ver
    if not ctx:
        return {"answer": "Bu soruya ilişkin bilgi, elimdeki emsal kararda yer almıyor.", "done": True}

    context_str = format_context(ctx)
    prompt = (
        f"Kaynak alıntılar:\n{context_str}\n\n"
        f"Kullanıcı Sorusu: {q}\n\n"
        "Yalnız yukarıdaki alıntılardan yararlanarak kısa yanıt ver; "
        "varsa ilgili sayfa numarasını da belirt."
    )
    msg = LLM.invoke([SystemMessage(content=SYS_PROMPT), HumanMessage(content=prompt)])
    return {"answer": msg.content.strip(), "done": True} # type: ignore

# ==== GRAF ====
graph = StateGraph(State)
graph.add_node("retrieve", retrieve_node)
graph.add_node("generate", generate_node)
graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", END)
app = graph.compile()

# ==== CLI ====
if __name__ == "__main__":
    if len(INDEX.chunks) == 0:
        print("⚠️ Hiç PDF bulunamadı veya metin çıkarılamadı. Emsal-Karar.pdf aynı klasörde mi?")
    else:
        print(f"✅ İndeks hazır: {len(INDEX.chunks)} parça")
    while True:
        q = input("❓ Soru yazın (çıkış için q): ").strip()
        if q.lower() in {"q", "quit", "exit"}:
            break
        out = app.invoke({"question": q})
        print("🤖:", out.get("answer", "").strip())
