from sqlalchemy.orm import Session
import models
import schema
import bcrypt


def create_user(db: Session, user: schema.CreateUser):
    hashed_password = bcrypt.hashpw(
        user.password.encode("utf-8"), bcrypt.gensalt())
    db_user = models.UserInfo(username=user.username, password=hashed_password,
                              firstname=user.firstname, lastname=user.lastname)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_note(db: Session, note: schema.NoteBase):
    db_note = models.Notes(title=note.title, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def get_user_by_username(db: Session, username: str):
    return db.query(models.UserInfo).filter(models.UserInfo.username == username).first()


def get_notes_by_id(db: Session, note_id: int):
    return db.query(models.Notes).filter(models.Notes.id == note_id).first()


def get_all_notes(db: Session):
    return db.query(models.Notes).all()


def check_user_password(db: Session, user: schema.AuthenticateUser):
    db_user_info: models.UserInfo = get_user_by_username(
        db, username=user.username)
    return bcrypt.checkpw(user.password.encode("utf-8"), db_user_info.password.encode("utf-8"))
