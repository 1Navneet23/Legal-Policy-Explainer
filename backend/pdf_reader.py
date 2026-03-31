from PyPDF2 import PdfReader
import os

def py_reader(file_path="data/legal/PL.pdf"):
    if not file_path:
        raise ValueError(f"""File path cannot be empty.""")

    if not os.path.exists(file_path):
        raise ValueError(f"""File not found at path: {file_path}""")

    all_text = ""

    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        total_pages = len(reader.pages)

        for i in range(total_pages):
            page = reader.pages[i]

            try:
                text = page.extract_text()

                if text is None or text.strip() == "":
                    print(f"No text found on page {i+1}")
                else:
                    print(f"Reading page {i+1}")
                    all_text += text + " "

            except Exception as e:
                print(f"Error extracting text from page {i+1}: {e}")

    return all_text