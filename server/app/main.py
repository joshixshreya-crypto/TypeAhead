from contextlib import asynccontextmanager
import uuid
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session
from trie import Trie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base , engine ,get_db ,SessionLocal
from models.typeahead_model import searchWord

trie = Trie()

@asynccontextmanager
async def load_trie_from_db(app: FastAPI ):
    print("loading trie on server start ...")
    db = SessionLocal()
    try:
        words = db.query(searchWord).all()
        for a in words:      
            trie.insert(a.word)
        
    finally:
        db.close()
    yield

app = FastAPI(lifespan= load_trie_from_db)

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class SearchPayload(BaseModel):
    word: str


@app.post("/insert-trie")
def insert_words(payload:SearchPayload , db: Session = Depends(get_db)):  
    trie.insert(payload.word)
    new_record = searchWord(
        id=str(uuid.uuid4()),
        word=payload.word
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"message": "Inserted into trie & DB", "data": new_record.word}

@app.get("/search-trie/{payload}")
def search_word_in_trie(payload: str):
    exists = trie.search(payload)
    return {"word ": payload , "exists": exists  }

@app.get("/starts-with/{payload}")
def starts_with_in_trie(payload:str):
    result = trie.starts_with(payload)
    return {"response": result}


   



