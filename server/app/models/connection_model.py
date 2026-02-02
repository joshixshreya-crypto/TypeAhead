from sqlalchemy import Column, ForeignKey, String, Enum ,UniqueConstraint
from database import Base
from enum import Enum as PyEnum

class ConnectionStatusEnum(PyEnum):
    PENDING= "PENDING"
    ACCEPTED= "ACCEPTED"
    REJECTED= "REJECTED"
class ConnectionModel(Base):
    __tablename__ = 'connection'
    
    id = Column(String, primary_key=True, index=True)   
    initiator_id =  Column(String , ForeignKey("users.id"))
    reciever_id  = Column(String , ForeignKey("users.id"))
    status = Column(String, nullable=False)
    created_at = Column(String)

    __table_args__ = (
        UniqueConstraint('initiator_id', 'reciever_id', name='unique_connection'),
    )
    

class NotificationModel(Base):
    __tablename__ = 'notifications'
   
    id = Column(String , primary_key = True , index = True)
    user_id = Column(String, ForeignKey("users.id")) # the person who will recieve / fetch the notifications
    initiator_id = Column(String , ForeignKey("users.id"))
    request_id = Column(String , ForeignKey("connection.id"))
    notification_type = Column(String)
    initiator_username=Column(String)
    created_at = Column(String)

    __table_args__ = (
        UniqueConstraint('user_id' , 'request_id' , name = 'unique_user_notification'),
    )
    

