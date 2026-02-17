from fastapi import FastAPI, HTTPException ,Request,UploadFile, File, Cookie,Response
from pydantic import BaseModel,Field
from backend.vector_store import store_embeddings,search_embeddings
 
from backend.llm_explainer import explain_legal_question,reason_about_scenario
from backend.text_splitter import text_splitter
from backend.pdf_reader import py_reader
 
from backend.embeddings import get_embeddings
import shutil, os, uuid, json
from typing import Optional

app=FastAPI()
 
active_chain={}
UPLOAD_DIR   = "uploads"
SESSIONS_FILE = "sessions.json"     # sessions saved here so they survive restart

os.makedirs(UPLOAD_DIR, exist_ok=True)


def load_session()->dict:
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "r") as f:
            return json.load(f)
    return {}
def save_session(sessions:dict):
    with open(SESSIONS_FILE,'w') as f:
        json.dump(sessions,f)
active_chain=load_session()
class Askquestion(BaseModel):
    session_id:str
    question:str
    
class getresponse(BaseModel):
    session:str
    answer:str="answer"
    mode:str
     
@app.get("/health")
async def health():
    return {"status":"ok"}

@app.post("/session/create")
async def create_session(response:Response):

    
    session_id=str(uuid.uuid4())
    active_chain[session_id]={"document_ready":False}
    save_session(active_chain)
    response.set_cookie(key="session_id", value=session_id, httponly=True,samesite="lax")
    return{"message":"Session created","session_id":session_id}
@app.post("/upload")
async def upload_pdf(
    file:UploadFile=File(...),
    session_id: Optional[str] = Cookie(None)):
    if session_id is None or session_id not in active_chain:
        raise HTTPException(status_code=401, detail="No session found. Call/session/create first")
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    file_path=os.path.join(UPLOAD_DIR,f"{session_id}.pdf")
    with open(file_path,"wb") as f:
        shutil.copyfileobj(file.file,f)
    try:
        pdf_text=py_reader(file_path)
        chunks=text_splitter(pdf_text)
        get_embeddings(chunks,session_id=session_id)
        active_chain[session_id]["document_ready"]=True
        save_session(active_chain)   
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Failed to process PDF:{str(e)}")
    return{"message":"PDF uploaded and processed.",'session_id':session_id}
@app.post("/ask_question",response_model=getresponse)
async def ask_question(request:Askquestion,session_id:Optional[str]=Cookie(default=None)):
    if session_id is None or session_id not in active_chain:
        raise HTTPException(status_code=401,detail=' No session found . call/session/create first.')
    if not active_chain[session_id]['document_ready']:
        raise HTTPException(status_code=400,detail="Document not uploaded yet. call/upload first.")
    try:
        context=search_embeddings(request.question,session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Failed to search:{str(e)}")
    try:
        if request.mode="scenario":
            answer=reason_about_scenario(request.question,context)
        else:
            answer=explain_legal_question(request.question,context)
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Failed to generate answer:{str(e)}")
    return getresponse(session=session_id,answer=answer,mode=request.mode)
@app.delete("/session/clear")
async def delete_session(response:Response,session_id:Optional[str]=Cookie(default=None)):
    if session_id is None or session_id not in active_chain:
        raise HTTPException(status_code=401,detail="No session found.  ")
    file_path=os.path.join(UPLOAD_DIR,f'{session_id}.pdf')
    if os.path.exists(file_path):
        os.remove(file_path)
    del active_chain[session_id]
    save_session(active_chain)
    response.delete_cookie("session_id")
    return{"message":"Session cleared."}

