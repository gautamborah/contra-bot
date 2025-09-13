import os
import pickle
import json
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
import faiss

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Paths
# INDEX_DIR = Path("./contra-costa-knowledge-bot/backend/app/data/index")
# FAISS_INDEX_PATH = "./app/data/processed/faiss.index"

FAISS_INDEX_PATH = "./contra-costa-knowledge-bot/backend/app/data/index/daily_index.faiss"
METADATA_PATH = "./contra-costa-knowledge-bot/backend/app/data/index/daily_index.jsonl"

def query_bot_old(question: str, k: int = 3):
    # Load FAISS index
    index = faiss.read_index(FAISS_INDEX_PATH)

    # Load metadata
    metadata = []
    with open(METADATA_PATH, "r") as f:
        for line in f:
            metadata.append(json.loads(line))

    # Embed the question
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    )
    query_vector = np.array(response.data[0].embedding).astype("float32").reshape(1, -1)

    # Search FAISS
    distances, indices = index.search(query_vector, k)

    # Retrieve context
    results = [metadata[i] for i in indices[0]]
    context = "\n".join([r["text"] for r in results])

    # Ask GPT with context
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant answering questions about Contra Costa County COVID-19 data."},
            {"role": "user", "content": f"Question: {question}\n\nContext:\n{context}"}
        ]
    )

    return completion.choices[0].message.content

def embed_query(query: str):
    """Embed the user query into a vector using OpenAI."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[query]
    )
    return np.array(response.data[0].embedding, dtype="float32")


def query_bot(query, k=5):
    # Load FAISS index
    index = faiss.read_index(str(FAISS_INDEX_PATH))

    # Load metadata
    metadata = []
    with open(METADATA_PATH, "r") as f:
        for line in f:
            metadata.append(json.loads(line))

    # Embed query
    query_embedding = embed_query(query)

    # Search
    D, I = index.search(np.array([query_embedding], dtype="float32"), k)

    # Retrieve texts + metadata
    results = [metadata[idx] for idx in I[0] if idx < len(metadata)]

    # Build context
    context = "\n".join([r["text"] for r in results])

    # Ask LLM
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant answering questions about vaccination data."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ],
    )

    return response.choices[0].message.content

def ask_question_loop():
    """Interactive loop for asking the bot questions until user exits."""
    print("🤖 Contra Costa Knowledge Bot (type 'exit', 'quit', or 'Shift+X' to stop)\n")
    while True:
        question = input("You: ").strip()
        if question.lower() in {"exit", "quit"} or question == "X":
            print("👋 Goodbye!")
            break
        try:
            answer = query_bot(question)
            print("🤖 Bot:", answer, "\n")
        except Exception as e:
            print(f"⚠️ Error: {e}\n")


# if __name__ == "__main__":
#     answer = query_bot("What is the vaccination trend in Alameda County?")
#     print("🤖 Bot:", answer)

if __name__ == "__main__":
    ask_question_loop()
