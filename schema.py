from graphene_sqlalchemy import SQLAlchemyObjectType
from models import UserInfo, Notes
from pydantic import BaseModel


class UserInformationBase(BaseModel):
    username: str


class CreateUser(UserInformationBase):
    firstname: str
    lastname: str
    password: str


class AuthenticateUser(UserInformationBase):
    password: str


class UserInformation(UserInformationBase):
    id = int

    class Config:
        orm_mode = True


class Token(BaseModel):
    username: str = None


class NoteBase(BaseModel):
    title: str
    content: str


class NoteInformation(NoteBase):
    id: int

    class Config:
        orm_mode = True


class UserInformationSchema(SQLAlchemyObjectType):
    class Meta:
        model = UserInfo


class NoteSchema(SQLAlchemyObjectType):
    class Meta:
        model = Notes
