import os
import json
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv

load_dotenv()

# --- Configs ---
DISCOURSE_CHUNKS_FILE = "dis_chunks.jsonl"
MD_CHUNKS_FILE = "md_chunks.jsonl"

DB_PATH = "./chroma_db"
COLLECTION_NAME = "tds_discord_openai"

# Setup Chroma client and embedding function using your AIProxy config
openai_ef = OpenAIEmbeddingFunction(
    api_key=os.getenv("AIPROXY_TOKEN"),
    api_base="https://aiproxy.sanand.workers.dev/openai/v1",
    model_name="text-embedding-3-small"
)

client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=openai_ef
)

def load_chunks(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)
def sanitize_metadata(meta: dict):
    sanitized = {}
    for k, v in meta.items():
        if isinstance(v, (str, int, float, bool)) or v is None:
            sanitized[k] = v
        else:
            # Convert complex types like list/dict to JSON string
            sanitized[k] = json.dumps(v)
    return sanitized

def embed_chunks(file_path, source_prefix):
    if not is_collection_empty():
        print(f"Collection already has data, skipping embedding for {source_prefix}.")
        return
    
    batch_size = 50
    batch, metas, ids = [], [], []
    for i, chunk in enumerate(load_chunks(file_path)):
        batch.append(chunk["text"])
        flat_metadata = chunk["metadata"].copy()
        
        if "tags" in flat_metadata and isinstance(flat_metadata["tags"], list):
            flat_metadata["tags"] = ", ".join(flat_metadata["tags"])
        
        # Add source info
        flat_metadata["source"] = source_prefix
        
        # Sanitize metadata before appending
        flat_metadata = sanitize_metadata(flat_metadata)

        metas.append(flat_metadata)
        ids.append(f"{source_prefix}_{i}")

        if len(batch) == batch_size:
            collection.add(documents=batch, metadatas=metas, ids=ids)
            print(f"✅ Embedded {len(batch)} chunks from {source_prefix} (up to {i + 1})")
            batch, metas, ids = [], [], []

    if batch:
        collection.add(documents=batch, metadatas=metas, ids=ids)
        print(f"✅ Embedded final batch of {len(batch)} chunks from {source_prefix}")

def is_collection_empty():
    # Returns True if collection is empty (no documents)
    return len(collection.get(include=["ids"])["ids"]) == 0

def search_collection(query_text, top_k=7):
    results = collection.query(query_texts=[query_text], n_results=top_k)
    # results is a dict with keys: 'ids', 'documents', 'metadatas'
    return results

def helper(query,top_k):
    res=search_collection(query, top_k)
    return res
def main():
    print("Starting embedding for discourse chunks...")
    embed_chunks(DISCOURSE_CHUNKS_FILE, source_prefix="discourse")

    print("Starting embedding for markdown chunks...")
    embed_chunks(MD_CHUNKS_FILE, source_prefix="markdown")

    print("\nEmbedding done. You can now query.")

    

    print("Done")

if __name__ == "__main__":
    main()
