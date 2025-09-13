import os
import json
import faiss
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Paths
DATA_DIR = Path("./contra-costa-knowledge-bot/backend/app/data/processed")
INDEX_DIR = Path("./contra-costa-knowledge-bot/backend/app/data/index")

DAILY_FILE = DATA_DIR / "daily_chunks_by_county.jsonl"
WEEKLY_FILE = DATA_DIR / "weekly_chunks_by_county.jsonl"

INDEX_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use a Gemini embedding model
EMBED_MODEL = "models/text-embedding-004" 

def load_chunks(file_path):
    """Load JSONL chunks into memory."""
    chunks = []
    with open(file_path, "r") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks

def embed_texts(texts):
    """Generate embeddings for a list of texts using Gemini."""
    embeddings = []
    
    # Clean and filter texts
    clean_texts = [str(t).strip() for t in texts if t and str(t).strip()]
    
    # Gemini's embedding API can handle a batch of texts at once
    response = genai.embed_content(
        model=EMBED_MODEL,
        content=clean_texts,
        task_type="retrieval_document"
    )
    embeddings = [e for e in response['embedding']]
    
    return embeddings

def build_faiss_index(chunks, index_file):
    """Build FAISS index and save metadata alongside."""
    texts = [c["text"] for c in chunks]

    print(f"Number of texts: {len(texts)}")
    if not texts:
        print("NO TEXTS found. Skipping index build.")
        return

    print("Sample text:", texts[0][:200])
    
    embeddings = embed_texts(texts)
    
    if not embeddings:
        print("No embeddings generated. Skipping index build.")
        return

    # FAISS index (L2 distance)
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    
    # Add embeddings
    index.add(np.array(embeddings).astype('float32'))
    
    # Save index
    faiss.write_index(index, str(index_file) + ".faiss")
    
    # Save metadata mapping
    metadata_file = str(index_file) + ".jsonl"
    with open(metadata_file, "w") as f:
        for i, c in enumerate(chunks):
            # The original code's metadata was a bit odd, preserving it but be aware
            f.write(json.dumps({"id": i, **c.get("metadata", {})}) + "\n")

    print(f"✅ Built FAISS index with {len(chunks)} chunks → {index_file}.faiss")

def main():
    # Daily chunks
    if DAILY_FILE.exists():
        daily_chunks = load_chunks(DAILY_FILE)
        build_faiss_index(daily_chunks, INDEX_DIR / "daily_index")
    else:
        print(f"Daily file not found: {DAILY_FILE}")

    # # Weekly chunks (uncomment to enable)
    # if WEEKLY_FILE.exists():
    #     weekly_chunks = load_chunks(WEEKLY_FILE)
    #     build_faiss_index(weekly_chunks, INDEX_DIR / "weekly_index")
    # else:
    #     print(f"Weekly file not found: {WEEKLY_FILE}")

if __name__ == "__main__":
    main()
