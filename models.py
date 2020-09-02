from sqlalchemy import Column, Integer, String
from db import Base


class UserInfo(Base):
    __tablename__ = "user_information"
    id = Column(Integer,  primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    firstname = Column(String)
    lastname = Column(String)


class Notes(Base):
    __tablename__ = "user_notes"
    id = Column(Integer,  primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
