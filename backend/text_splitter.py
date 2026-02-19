import re
from backend.pdf_reader import py_reader
 
def text_splitter(text, chunk_size=500, overlap=50):
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = []
    current_word_count = 0

    for sentence in sentences:
        sentence_words = sentence.split()
        sentence_word_count = len(sentence_words)

        if current_word_count + sentence_word_count > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
 
            overlap_words = []
            temp_count = 0
            for sent in reversed(current_chunk):          # walk backward
                words = sent.split()
                if temp_count + len(words) <= overlap:
                    overlap_words.append(sent)            # append, not insert(0)
                    temp_count += len(words)
                else:
                    break

            overlap_words.reverse()                       # restore correct order
            current_chunk = overlap_words
            current_word_count = temp_count

        current_chunk.append(sentence)
        current_word_count += sentence_word_count

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks