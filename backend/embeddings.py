from backend.text_splitter import text_splitter
from backend.pdf_reader import py_reader
from backend.model_loader import embedding_model
def get_embeddings(chunks):
    
    embeddings=embedding_model.encode(chunks)
    return embeddings
 