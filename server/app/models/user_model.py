from sqlalchemy import Column, DateTime, String, func
from database import Base

class UserModel(Base):
    __tablename__ = "users"
    id = Column(String , primary_key = True , index = True)
    email = Column(String )
    username = Column(String)
    password = Column(String)
    created_by = Column(DateTime(timezone=True), server_default=func.now())



