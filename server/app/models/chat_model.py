from sqlalchemy import Column, DateTime, ForeignKey , String, func
from database import Base

class roomSchema(Base):
    __tablename__ = "room"
    id = Column(String , primary_key= True , index= True)
    room_name =  Column(String )
    create_time = Column(DateTime(timezone=True), server_default=func.now())

class messageSchema(Base):
    __tablename__ = "message"
    id = Column(String , primary_key= True , index= True)
    room_id = Column(String , ForeignKey("room.id"))
    message =  Column(String )
    sender_id = Column(String, ForeignKey("users.id"))
    create_time = Column(DateTime(timezone=True), server_default=func.now())
