import ollama
from backend.pdf_reader import py_reader
from backend.text_splitter import text_splitter
from backend.embeddings import get_embeddings
from backend.search import get_search_result


def explain_legal_question(question, best_chunk):
    client = ollama.Client()
    model = "mistral"

    prompt = f"""
You are a legal assistant helping a non-lawyer understand legal text.

Rules:
- Use ONLY the legal text provided.
- Do NOT invent information.
- If the answer is partially present, explain what is available.
- If the text is unrelated, say: "The document does not contain the answer."

Question:
{question}

Legal Text:
{best_chunk}

Task:
Explain the answer in simple, clear language for a normal person.
"""

    response = client.generate(model=model, prompt=prompt)
     
    return response["response"]


def reason_about_scenario(question, best_chunk):
    client = ollama.Client()
    model = "mistral"

    prompt = f"""
You are a legal assistant.

You must reason about the user's scenario
using ONLY the provided legal text.

User Scenario:
{question}

Relevant Legal Text:
{best_chunk}

Instructions:
- Explain what would likely happen
- Use simple language
- Do not invent laws
- If the answer is not in the text, say:
  "I don't know based on the provided document."

Answer:
"""

    response = client.generate(model=model, prompt=prompt)
 
    return response["response"]