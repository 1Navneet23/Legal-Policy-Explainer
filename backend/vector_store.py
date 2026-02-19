import chromadb
from chromadb.config import Settings
from backend.model_loader import embedding_model

client = chromadb.Client(Settings(persist_directory="chroma_db"))

 
def _get_collection(session_id: str):
    """Return (or create) the ChromaDB collection dedicated to this session."""
    return client.get_or_create_collection(f"session_{session_id}")


def store_embeddings(chunks, session_id: str):
    collection = _get_collection(session_id)      # ← scoped to this user

    embeddings = embedding_model.encode(chunks).tolist()
    ids = [f"id_{i}" for i in range(len(chunks))]
    collection.add(ids=ids, embeddings=embeddings, documents=chunks)

 
def search_embeddings(query, session_id: str, top_k: int = 3):
    collection = _get_collection(session_id)      # ← correct session only

    query_embedding = embedding_model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=top_k)

     
    top_chunks = results["documents"][0]
    return "\n\n---\n\n".join(top_chunks)


def delete_session_collection(session_id: str):
    """Clean up storage when a session is deleted."""
    try:
        client.delete_collection(f"session_{session_id}")
    except Exception:
        pass

 