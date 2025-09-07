import json
from langgraph.graph import StateGraph
from langchain_ollama import ChatOllama

# --- JSON dosyasını oku ---
with open("emsal_focused.json", "r", encoding="utf-8") as f:
    data = json.load(f)   # ✔️ dict/list geliyor

def generate_answer(state: dict):
    question = state.get("question", "")

    # JSON verisini özet için hazırlar
    context = "\n".join(
        f"- Sayfa {item.get('page')}: {item.get('summary')}"
        for item in data
    )

    prompt = f"""Aşağıdaki içerik, bir dava dosyasından özetlenmiştir:

{context}

Kullanıcının sorusu: {question}

Lütfen kısa ve net bir yanıt ver."""
    
    llm = ChatOllama(model="gemma3:4b")
    response = llm.invoke(prompt)

    return {"answer": response.content}

# --- LangGraph akışı ---
graph = StateGraph(dict)  # type: ignore # ✔️ dict kullanıyoruz
graph.add_node("qa", generate_answer) # type: ignore
graph.set_entry_point("qa")
graph.set_finish_point("qa")
app = graph.compile()

print("📖 PDF Chatbot hazır! Çıkmak için 'q' yaz.\n")

while True:
    q = input("Sorunuzu yazın: ")
    if q.lower() == "q":
        break
    state = {"question": q}   # ✔️ Artık dict
    result = app.invoke(state)
    print("\n🤖 Cevap:", result["answer"], "\n")
