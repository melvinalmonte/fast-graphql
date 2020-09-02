from logging import log, CRITICAL

import bcrypt
import graphene
import uvicorn
from fastapi import FastAPI
from graphql import GraphQLError
from jwt import PyJWTError
from starlette.graphql import GraphQLApp

import actions
from utils import decode_access_token, create_access_token
from db import db_session
from schema import NoteSchema, UserInformationSchema, CreateUser, AuthenticateUser, Token, NoteBase
from datetime import timedelta

db = db_session.session_factory()


class UserCreate(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        firstname = graphene.String(required=True)
        lastname = graphene.String(required=True)

    ok = graphene.Boolean()
    user = graphene.Field(lambda: UserInformationSchema)

    @staticmethod
    def mutate(root, info, username, password, firstname, lastname):
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())
        user = UserInformationSchema(
            username=username, password=hashed_password, firstname=firstname, lastname=lastname)
        ok = True

        db_user = actions.get_user_by_username(db, username=username)

        if db_user:
            raise GraphQLError("This username is already registered.")
        user_info = CreateUser(
            username=username, password=password, firstname=firstname, lastname=lastname)
        actions.create_user(db, user_info)
        return UserCreate(user=user, ok=ok)


class UserAuthenticate(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
    token = graphene.String()

    @staticmethod
    def mutate(root, info, username, password):
        db_user = actions.get_user_by_username(
            username=username, password=password)
        user_authenticate = AuthenticateUser(
            username=username, password=password)
        if db_user is None:
            raise GraphQLError("Username does not exist.")
        else:
            is_password_correct = actions.check_user_password(
                db, user_authenticate)
            if is_password_correct is False:
                raise GraphQLError("Password is incorrect.")
            else:
                access_token_expires = timedelta(
                    minutes=30)
                access_token = create_access_token(
                    data={"sub": username}, expires_delta=access_token_expires)
                return UserAuthenticate(token=access_token)


class CreateNewNote(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        token = graphene.String(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, title, content, token):
        try:
            decoded_token = decode_access_token(data=token)
            username: str = decoded_token.get("sub")
            if username is None:
                GraphQLError("Invalid credentials.")
            token_data = Token(username=username)
        except PyJWTError:
            raise GraphQLError("Invalid credentials.")
        user = actions.get_user_by_username(db, username=token_data.username)
        if user is None:
            raise GraphQLError("Invalid credentials.")
        note = NoteBase(title=title, content=content)
        actions.create_note(db=db, note=note)
        ok = True
        return CreateNewNote(ok=ok)


class Query(graphene.ObjectType):
    all_notes = graphene.List(NoteSchema)

    def resolve_all_notes(self, info):
        query = NoteSchema.get_query(info)
        return query.all()


class Mutations(graphene.ObjectType):
    user = UserCreate.Field()
    authenticate_user = UserAuthenticate.Field()
    create_new_note = CreateNewNote.Field()


app = FastAPI()

app.add_route(
    "/graphql", GraphQLApp(schema=graphene.Schema(query=Query, mutation=Mutations)))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
