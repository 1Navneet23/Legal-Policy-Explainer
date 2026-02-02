from backend.text_splitter import text_splitter
from backend.pdf_reader import py_reader
from sentence_transformers import SentenceTransformer
def get_embeddings(chunks):
    model=SentenceTransformer('all-MiniLM-L6-v2')
    embeddings=model.encode(chunks)
    return embeddings
 