from backend.pdf_reader import py_reader
def text_splitter(text,chunk_size=200):
    txt=text.split()
    chunks=[]
    for i in range(0,len(txt),chunk_size):
        chunk=" ".join(txt[i:i+chunk_size])
        chunks.append(chunk)
    return chunks
 