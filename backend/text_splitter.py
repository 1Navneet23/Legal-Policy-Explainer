import re
from backend.pdf_reader import py_reader
def text_splitter(text, chunk_size=500, overlap=50):
    
    # Split into sentences using regex
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for sentence in sentences:
        sentence_words = sentence.split()
        sentence_word_count = len(sentence_words)
        
        # If adding this sentence exceeds chunk size, save current chunk
        if current_word_count + sentence_word_count > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            
            # Keep last 'overlap' words for context
            overlap_words = []
            temp_count = 0
            for sent in reversed(current_chunk):
                words = sent.split()
                if temp_count + len(words) <= overlap:
                    overlap_words.insert(0, sent)
                    temp_count += len(words)
                else:
                    break
            
            current_chunk = overlap_words
            current_word_count = temp_count
        
        current_chunk.append(sentence)
        current_word_count += sentence_word_count
    
    # Add the last chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    #print(f"Created {len(chunks)} chunks with ~{chunk_size} words each")
    return chunks