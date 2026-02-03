import chromadb
from chromadb.config import Settings
from backend.model_loader import embedding_model

# persistent database on disk
client = chromadb.Client(Settings(
    persist_directory="chroma_db"
))

collection = client.get_or_create_collection("legal_docs")


def store_embeddings(chunks):
    embeddings = embedding_model.encode(chunks).tolist()

    ids = [f"id_{i}" for i in range(len(chunks))]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks
    )

    client.persist()


def search_embeddings(query, top_k=1):
    query_embedding = embedding_model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    return results["documents"][0]
