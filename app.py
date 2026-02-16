from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,Field
from backend.vector_store import store_embeddings,search_embeddings
from backend.model_loader import embedding_model
from backend.llm_explainer import explain_legal_question,reason_about_scenario
from backend.text_splitter import text_splitter
from backend.pdf_reader import py_reader
from backend.search import get_search_result
from backend.embeddings import get_embeddings
app=FastAPI()
 
active_chain={}
class ask_question(BaseModel):
    session_id="session"
    question:str="question"
    answer:str="answer"
class get_response(BaseModel):
    answer:str="answer"
    session="session"
@app.get("/abc")
async def abc():
    return {"status":"success"}
@app.post("/ask_question")
async def ask_question(request:ask_question):
    question=request.question
    session=request.session_id
    vector=search_embeddings()
    if(session!=session_id):
        pdf=py_reader("pdf")
        chunks=text_splitter(pdf)
        embed=get_embeddings(chunks)
        store=store_embeddings(embed)
        
    vector=search_embeddings(store,question)
    model=explain_legal_question(vector,question)
    active_chain[session]=model
    return get_response({session,model})


