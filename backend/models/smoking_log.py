from sqlalchemy import Column, Integer,String,DateTime
from  backend.database import Base
class SmokingLog(Base):
    __tablename__="smoking_logs"
    id=Column(Integer,primary_key=True,index=True)
    cigarettes=Column(Integer)
    mood=Column(String)
    stress_level=Column(Integer)
    location=Column(String)
    reason=Column(String)
    smoked_at=Column(DateTime)

