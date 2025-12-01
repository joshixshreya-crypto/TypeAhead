from fastapi import FastAPI
from pydantic import BaseModel
from app.trie import Trie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
trie = Trie()

class SearchPayload(BaseModel):
    word: str

@app.post("/insert-trie")
def insert_words(payload:SearchPayload):  
    print("============>",payload) 
    trie.insert(payload.word)
    return {"message": "word inserted into trie"}

@app.get("/search-trie/{payload}")
def search_word_in_trie(payload: str):
    exists = trie.search(payload)
    return {"word ": payload , "exists": exists  }

@app.get("/starts-with/{payload}")
def starts_with_in_trie(payload:str):
    result = trie.starts_with(payload)
    return {"response": result}


   



