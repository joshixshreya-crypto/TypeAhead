from sqlalchemy import Column, ForeignKey, String
from database import Base

class RoomUserModel(Base):
    __tablename__ = 'roomuser'
    user_id =  Column(String , ForeignKey("users.id") , primary_key= True)
    room_id = Column(String , ForeignKey("room.id") , primary_key=True)
