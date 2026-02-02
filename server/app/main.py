import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
import json
import os
import uuid
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from async_queue import AsyncQueue
from trie import Trie
from fastapi.middleware.cors import CORSMiddleware
from database import Base , engine ,get_db ,SessionLocal
from models.typeahead_model import searchWord
from models.chat_model import roomSchema 
from models.user_model import UserModel
from models.connection_model import ConnectionModel , ConnectionStatusEnum
from redis_client import redis_client
from start_worker import start_worker
from rate_limiter import rate_limiter
from sliding_win_rate_limiter import sliding_window_rate_limiter
from token_bucket_rate_limiter import token_bucket_rl
from service.notification_service import notification_worker
from sqlalchemy.exc import IntegrityError

# Load environment variables
load_dotenv()

trie = Trie()
user_trie = Trie()
# queue = AsyncQueue()
active_connections = {}


async def pubsub_listener():
    print("🟢 pubsub_listener started, subscribing now")
    pubsub = redis_client.pubsub()
    pubsub.subscribe("websocket_notifications")
    print(" 🔥Started Redis Pub/Sub listener for notifications")
    
    while True:
        message = await asyncio.to_thread(pubsub.get_message, ignore_subscribe_messages=True)
        if not message:
            await asyncio.sleep(0.1)
            continue
        try:               
            print("Received notification message via Pub/Sub:", message)
            notification_data = json.loads(message['data'])
            user_id = notification_data['user_id']
            notification_id = notification_data['request_id']
            await send_notifications_to_user(user_id, notification_data)
        except Exception as e:
            print(f"error processing pubsub message: {e}")


@asynccontextmanager
async def load_trie_from_db(app: FastAPI ):
    print(" Starting application initialization...")
    
    # Wait for database to be ready
    max_retries = 10
    db = None
    for i in range(max_retries):
        try:
            db = SessionLocal()
            # Test database connection
            db.execute(text("SELECT 1"))
            print(f"Database is ready!")
            break
        except Exception as e:
            print(f" Waiting for database... (attempt {i+1}/{max_retries}): {e}")
            if db:
                db.close()
            await asyncio.sleep(2)
    else:
        print("Database not available after retries")
        yield
        return
    
    print("Loading trie from database...")
    try:
        words = db.query(roomSchema).all()
        users = db.query(UserModel).all()
        for a in words:      
            trie.insert(a.room_name)
        for u in users:
            user_trie.insert(u.username , u.id)
        print(f"Loaded {len(words)} words and {len(users)} usersinto trie")
    except Exception as e:
        print(f"⚠️  Error loading trie: {e}")
    finally:
        db.close()
    
    # Start worker in background task (non-blocking)
    asyncio.create_task(start_worker())
    # Start notification worker
    asyncio.create_task(notification_worker())

    # Subscribe to pubsub for sending notifications
    asyncio.create_task(pubsub_listener())
    
    print("Application startup complete - worker running in background")
    
    yield
    
    # Cleanup on shutdown
    print("Application shutting down...")

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
class LoginPayload(BaseModel):
    username: str
    password: str

class ConnectionModel(BaseModel):
    initiator_id: str
    reciever_id: str
class AcceptRequestPayload(BaseModel):
    user_id: str
    initiator_id: str

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
    user_id = str(uuid.uuid4())
    sql_query = "select u.email , u.username from users as u where u.username = :username"
    response = db.execute(text(sql_query),{
        "email": user.email,
        "username": user.username
    })
    response = response.mappings().first()
    if(response and len(response) >0):
        raise HTTPException(400 , "user with given email or username already exists")
    

    sql_query = 'insert into users (id , email , username , password) values (:id , :email , :username , :password)'
    
    db.execute(text(sql_query), {
        "id": user_id ,
        "email": user.email,
        "username": user.username,
        "password": user.password
    })

    db.commit()
    user_trie.insert(user.username ,user_id)
    return{"message": "user added" , "response":  {"username":user.username , "email":user.email , "user_id": user_id}}

@app.post("/login")
def login_user(user: LoginPayload , db:Session = Depends(get_db)):
    sql_query = "select u.id , u.username from users as u where u.username = :username and u.password = :password"
    response = db.execute(text(sql_query),{
        "username": user.username,
        "password": user.password
    })
    response = response.mappings().first()
    print("login response"  ,response)
    if(not response):
        raise HTTPException(404 , "user not found with given credentials")
    return {"message": "login successful" , "response": response}


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
    return {"result": response , "message": "chats fetched"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print("🔥 WebSocket endpoint hit")
    await websocket.accept()
    db = SessionLocal()
    try:
        while True:
            data = await websocket.receive_text()
            json_data = json.loads(data)
            # initializing connection for sending notifications to client
            if(json_data.get('type') == "INIT"):
                user_id = json_data.get('userId')
                print("initializing connection for notfication" , user_id)
                active_connections[user_id] = websocket
                continue
            else:               
                message = json_data['message']
                sender_id  = json_data['userId']
                room_name = json_data['room_name']

                # rate limiting check
                if(token_bucket_rl(sender_id) == False):
                    await websocket.send_text(json.dumps({
                        "error": "too many messages dude slow downnn!"
                    }))
                    continue
                else:
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
                    redis_client.xadd(STREAM, queue_payload)

    except WebSocketDisconnect:
            print("Client disconnected")
    finally:
        db.close()

# news feed apis 

# getting usernames suggestions
@app.get("/starts-with-users/{prefix}")
def get_users_list_suggestion(prefix: str):
    print("Fetching user suggestions for prefix:", prefix)
    result = user_trie.starts_with(prefix)
    print(result)
    return {"response":result}

#request friend api 
# @app.post("/friend-request")
# def add_friend_api(connection: ConnectionModel , db: Session = Depends(get_db)):
    # try: 
    #     created_at = datetime.utcnow().isoformat()
    #     notification_stream = os.getenv("NOTIFICATION_STREAM_NAME")
    #     connection_id = str(uuid.uuid4())
    #     sql_query = sql_query = """
    #             INSERT INTO connection (id, initiator_id, reciever_id, status, created_at)
    #             VALUES (:id, :initiator_id, :reciever_id, :status, :created_at)
    #             ON CONFLICT (initiator_id, reciever_id)
    #             DO NOTHING
    #             RETURNING id
    #             """
    #     result = db.execute(text(sql_query),{
    #         "id": connection_id,
    #         "initiator_id": connection.initiator_id,
    #         "reciever_id": connection.reciever_id,
    #         "status": ConnectionStatusEnum.PENDING.value,
    #         "created_at": created_at
    #     }).fetchone()
    #     db.commit()
    #     # request already exists 
    #     if(result is None):
    #         print("⚠️ request already exists")
    #         sql_query = "SELECT id ,status from connection as c where c.initiator_id = :initiator_id and c.reciever_id = :reciever_id"
    #         existing_connection = db.execute(text(sql_query), {
    #             'initiator_id': connection.initiator_id,
    #             'reciever_id': connection.reciever_id   
    #         })
    #         existing_connection = existing_connection.mappings().first()
    #         request_id = existing_connection['id']
    #         status = existing_connection['status']  

           
    #         print("existing connection id" , request_id)
    #         return {"message": "Friend request already exists" ,"response": {"req_id":request_id ,  "status": status }}
        
    #     # request doesnot exists , created just now and send notification.
    #     else:
    #         sql_query = "SELECT u.username from users as u where u.id = :initiator_id"
    #         response = db.execute(text(sql_query),{
    #             "initiator_id": connection.initiator_id
    #         })
    #         response = response.mappings().first()
    #         print("userrrrrnamee" , response)
    #         # send notificaion to notication stream
    #         notificaionStreamPalyoad = {
    #             "user_id": connection.reciever_id,
    #             "initiator_id": connection.initiator_id,
    #             "initiator_username": response['username'],
    #             "notification_type": "FRIEND_REQUEST",
    #             "request_id": connection_id,
    #             "created_at": created_at           
    #         }
    #         redis_client.xadd(notification_stream , notificaionStreamPalyoad)
    #         return {"message": "Friend request sent successfully"}
    # except Exception as e:
    #     print(f"error in friend request api: {e}")
    #     raise HTTPException(500 , "internal server error , {e}")

@app.post("/friend-request")
def add_friend_api(connection: ConnectionModel , db: Session = Depends(get_db)):
    try: 
        created_at = datetime.utcnow().isoformat()
        notification_stream = os.getenv("NOTIFICATION_STREAM_NAME")
        connection_id = str(uuid.uuid4())
        sql_query = sql_query = """
                INSERT INTO connection (id, initiator_id, reciever_id, status, created_at)
                VALUES (:id, :initiator_id, :reciever_id, :status, :created_at)
                """
        result = db.execute(text(sql_query),{
            "id": connection_id,
            "initiator_id": connection.initiator_id,
            "reciever_id": connection.reciever_id,
            "status": ConnectionStatusEnum.PENDING.value,
            "created_at": created_at
        })
        db.commit()
        # request doesnot exists , created just now and send notification.
        sql_query = "SELECT u.username from users as u where u.id = :initiator_id"
        response = db.execute(text(sql_query),{
            "initiator_id": connection.initiator_id
        })
        response = response.mappings().first()
        print("userrrrrnamee" , response)
        # send notificaion to notication stream
        notificaionStreamPalyoad = {
            "user_id": connection.reciever_id,
            "initiator_id": connection.initiator_id,
            "initiator_username": response['username'],
            "notification_type": "FRIEND_REQUEST",
            "request_id": connection_id,
            "created_at": created_at           
        }
        redis_client.xadd(notification_stream , notificaionStreamPalyoad)
        return {"message": "Friend request sent successfully"}
    except IntegrityError:
        print("⚠️ request already exists")
    except Exception as e:
        print(f"error in friend request api: {e}")
        raise HTTPException(500 , "internal server error , {e}")

# fetch notifications api
@app.get("/fetch-notifications/{user_id}")
def fetch_notifications_api(user_id: str , db:Session = Depends(get_db)):
    sql_query  ="SELECT * from notifications as n where n.user_id = :user_id order by n.created_at desc "
    notifications = db.execute(text(sql_query),{
        "user_id": user_id
    })
    notifications = notifications.mappings().all()
    return {"response": notifications}

async def send_notifications_to_user(user_id: str , notification_data: dict):
    websocket = active_connections.get(user_id)
    if websocket:
        print(f"Sending notification to user {user_id} via WebSocket")
        await websocket.send_text(json.dumps(notification_data))

    else:
        print(f"No active websocket connection for user {user_id}")

@app.post("/friend-request/accept")
def accept_friend_request(payload: AcceptRequestPayload , db: Session = Depends(get_db)):
    NOTIFICATION_STREAM_NAME = os.getenv("NOTIFICATION_STREAM_NAME")
    try:
        sql_query = """ SELECT c.status from connection as c where c.reciever_id = :user_id and c.initiator_id = :initiator_id """
        response = db.execute(text(sql_query), {
            "user_id": payload.user_id,
            "initiator_id": payload.initiator_id
        }).mappings().first()
        
        if(response is None):
            raise HTTPException(404 , "friend request not found")
        status = response['status']
        if(status == ConnectionStatusEnum.ACCEPTED.value):
            return {"message": f"friend request already {status.lower()}"}
        sql_query = """ UPDATE connection set status = :status where reciever_id = :user_id and initiator_id = :initiator_id"""
        db.execute(text(sql_query), {
            "status": ConnectionStatusEnum.ACCEPTED.value,
            "user_id": payload.user_id,
            "initiator_id": payload.initiator_id
        })
        db.commit()
        sql_query = "SELECT u.username from users as u where u.id = :user_id"
        response = db.execute(text(sql_query),{
            "user_id": payload.user_id
        })
        response = response.mappings().first()
        notification_payload = {
            "user_id": payload.initiator_id,
            "initiator_id": payload.user_id,
            "notification_type": "FRIEND_REQUEST_ACCEPTED",
            "request_id": str(uuid.uuid4()),
            "initiator_username": response['username'],
            "created_at": datetime.utcnow().isoformat()          
        }
        redis_client.xadd(NOTIFICATION_STREAM_NAME ,notification_payload)
        return {"message": "friend request accepted successfully"}
    except Exception as e:
        print(f"error in accept friend request api: {e}")
        raise HTTPException(500 , "internal server error , {e}")

@app.get("/friend-request-status/{user_id}/{reciever_id}")
def check_friend_request_status(user_id: str , reciever_id: str , db: Session = Depends(get_db)):
    try:
        sql_query = """ SELECT status, initiator_id, reciever_id 
            FROM connection 
            WHERE (initiator_id = :user_id AND reciever_id = :reciever_id)
            OR (initiator_id = :reciever_id AND reciever_id = :user_id) """
        response = db.execute(text(sql_query), {
            "user_id": user_id,
            "reciever_id": reciever_id
        })
        response = response.mappings().first()
        
        if not response:
            return {"status": "NONE"}
        status = response['status']
        if(status == ConnectionStatusEnum.ACCEPTED.value):
            return {"status": "ACCEPTED"}
        if(response['initiator_id'] == user_id):
            return {"status": "SENT"}
        else:
            return {"status": "RECEIVED"}
    except Exception as e:
        print(f"error in checking friend request status api: {e}")
        raise HTTPException(500 , "internal server error , {e}")
        

        












 

