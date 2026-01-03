import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
import json
import os
import uuid
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from async_queue import AsyncQueue
from trie import Trie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base , engine ,get_db ,SessionLocal
from models.typeahead_model import searchWord
from models.chat_model import roomSchema , messageSchema
from models.user_model import UserModel
from redis_stream import create_consumer_group , redis_client
from start_worker import start_worker
trie = Trie()
queue = AsyncQueue()

@asynccontextmanager
async def load_trie_from_db(app: FastAPI ):
    print("loading trie on server start ...")
    db = SessionLocal()
    try:
        words = db.query(roomSchema).all()
        for a in words:      
            trie.insert(a.room_name)
        
    finally:
        db.close()
    print("stream name printedddddddddddd========>",os.getenv('STREAM_NAME'))
    # await start_worker()
    yield

app = FastAPI(lifespan= load_trie_from_db)

Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STREAM = os.getenv('STREAM_NAME')
GROUP = os.getenv('GROUP_NAME')
CONSUMER = os.getenv('CONSUMER_NAME')

class SearchPayload(BaseModel):
    word: str

class UserPayload(BaseModel):
    email: str
    username: str
    password: str


@app.post("/insert-trie")
def insert_words(payload:SearchPayload , db: Session = Depends(get_db)):  
    trie.insert(payload.word)
    new_record = roomSchema(
        id=str(uuid.uuid4()),
        room_name=payload.word
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"message": "Inserted into trie & DB", "data": new_record.room_name}

@app.get("/search-trie/{payload}")
def search_word_in_trie(payload: str):
    exists = trie.search(payload)
    return {"word ": payload , "exists": exists  }

@app.get("/starts-with/{payload}")
def starts_with_in_trie(payload:str):
    result = trie.starts_with(payload)
    return {"response": result}

#user login and register

@app.post("/user-creds")
def add_user(user: UserPayload , db: Session = Depends(get_db) ):
    print("=======================>" , user)
    user_id = str(uuid.uuid4())
    sql_query = 'insert into users (id , email , username , password) values (:id , :email , :username , :password)'
    db.execute(text(sql_query), {
        "id": user_id ,
        "email": user.email,
        "username": user.username,
        "password": user.password
    })

    db.commit()
    return{"message": "user added" , "response":  {"username":user.username , "email":user.email , "user_id": user_id}}


# chat feature apis

@app.get("/fetch-chats/{room_name}")
def fetch_chat_history(room_name: str , db: Session = Depends(get_db)):
    sql_query = 'select r.id from room as r where r.room_name = :room_name'
    response = db.execute(text(sql_query) , {
        "room_name": room_name
    }).fetchone()

    if(not response):
        raise HTTPException(404 , "room name not found")
    room_id = response[0]

    sql_query = """select u.username , m.message  , m.create_time  from message as m 
                    inner join
                    users as u
                    on m.sender_id = u.id where m.room_id = :room_id order by create_time asc
    """
    response = db.execute(text(sql_query), {
        'room_id': room_id 
    }).mappings().all()
    print("======>response", response )
    return {"result": response , "message": "chats fetched"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        db = SessionLocal()
        while True:
            data = await websocket.receive_text()
            if(data):
                json_data = json.loads(data)
                message = json_data['message']
                sender_id  = json_data['userId']
                room_name = json_data['room_name']
                user = db.query(UserModel).filter(UserModel.id == sender_id).first()
                # payload for sending data back from server to client 
                send_payload = {
                    "message": message,
                    "create_time": datetime.utcnow().isoformat()
                }
                if(user):
                    send_payload["username"] = user.username
                else:
                    send_payload["username"] = "unknown"
                json_payload_to_send = json.dumps(send_payload)
                
                await websocket.send_text(json_payload_to_send)

                # adding message to queue
                queue_payload = {
                    "message": message,
                    "create_time": datetime.utcnow().isoformat(),
                    "sender_id": sender_id,    
                    "room_name": room_name
                }
                redis_client.xadd(
                    STREAM,
                    {
                        queue_payload
                })
                # await queue.put(queue_payload)

    except WebSocketDisconnect:
            print("Client disconnected")
    finally:
        db.close()

