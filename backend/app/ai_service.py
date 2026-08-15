from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="qwen3:1.7b",
    temperature=0
)


def ask_ai(question: str):
    response = llm.invoke(question)
    return response.content