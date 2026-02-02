from sentence_transformers import SentenceTransformer
from backend.text_splitter import text_splitter
from backend.pdf_reader import py_reader
from backend.embeddings import get_embeddings
from sklearn.metrics.pairwise import cosine_similarity


def get_search_result(chunks, embeddings, query):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = model.encode(query)

    best_score = -1
    best_index = -1

    for i in range(len(embeddings)):
        sim = cosine_similarity(
            [query_embedding],
            [embeddings[i]]
        )[0][0]

        #print(f"Similarity with chunk {i+1}: {sim}")

        if sim > best_score:
            best_score = sim
            best_index = i

    #print("\nBest matching chunk:")
    #print(chunks[best_index])
    
    return chunks[best_index]