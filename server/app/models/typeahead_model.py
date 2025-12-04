from sqlalchemy import Column, DateTime , String, func

from database import Base


class searchWord(Base):
    __tablename__ =  "search_word"
    id = Column(String , primary_key= True , index= True)
    word = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
