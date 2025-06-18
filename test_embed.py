import os
import json
import chromadb
from chromadb.utils.embedding_functions import JinaEmbeddingFunction
from dotenv import load_dotenv

load_dotenv()

# --- Configs ---
DISCOURSE_CHUNKS_FILE = "dis_chunks.jsonl"
MD_CHUNKS_FILE = "md_chunks.jsonl"

DB_PATH = "./chroma_dbV2TEST"
COLLECTION_NAME = "tds_discord_jinaai"

# Setup Chroma client and embedding function using your AIProxy config

jina_ef = JinaEmbeddingFunction(
    api_key=os.getenv("JINAAI_API_KEY"),
    model_name="jina-embeddings-v2-base-en"  # Ensure this is the correct model name
)
#I plan to use JinaAI for embedding, so suggest the pathway for that
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=jina_ef
)
#TypeError: JinaEmbeddingFunction.__init__() got an unexpected keyword argument 'api_base'


    
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
    
    
    
    # If collection is not empty, skip embedding
    # Check if the collection is empty before proceeding
    #if not is_collection_empty():
     #   print(f"Collection already has data, skipping embedding for {source_prefix}.")
      #  return
    li=[]
    for i in range(2340,2360):
        li.append(i)
    batch_size = 20
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

        if len(batch) == batch_size or (i in li):  # Adjust batch size as needed, or use a specific condition
            if (not cached_get(documents=batch, metadatas=metas, ids=ids)) or (i in li): #:
                collection.add(documents=batch, metadatas=metas, ids=ids)
                print(f"✅ Embedded {len(batch)} chunks from {source_prefix} (up to {i + 1})")
            
            # Reset batch, metas, ids for the next batch
            batch, metas, ids = [], [], []
    #httpx.ReadTimeout: The read operation timed out in add.
    
    if batch and (not cached_get(documents=batch, metadatas=metas, ids=ids)):
        collection.add(documents=batch, metadatas=metas, ids=ids)
        cached_get(documents=batch,metadatas=metas,ids=ids)  # Example usage of cached_get
        print(f"✅ Embedded final batch of {len(batch)} chunks from {source_prefix}")

def is_collection_empty():
    # Returns True if collection is empty (no documents)
    return len(collection.get()['ids']) == 0





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

#Write a cached_get() function to store chunk embeddings intermittently in a cache file that are retreived from embed_chunks
def cached_get(documents, metadatas, ids):
    cache_file = "cached_embeddings.json"
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            cached_data = json.load(f)
    else:
        cached_data = {}
    # Check if the documents are already cached
    for id_ in ids:
        if id_ in cached_data:
            print(f"Document with ID {id_} is already cached.")
            return True

    # Store the new embeddings in the cache
    for doc, meta, id_ in zip(documents, metadatas, ids):
        cached_data[id_] = {
            "document": doc,
            "metadata": meta
        }

    # Write back to the cache file
    with open(cache_file, "w") as f:
        json.dump(cached_data, f)

    print("Cached embeddings saved.")
    return False


if __name__ == "__main__":
    main()
