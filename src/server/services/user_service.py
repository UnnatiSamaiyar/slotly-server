from sqlalchemy.orm import Session
from ..models.user import User
from ..utils.crypto import encrypt_token

def get_user_by_sub(db: Session, sub: str):
    return db.query(User).filter(User.google_sub == sub).first()

def create_user(db: Session, name: str, email: str, picture: str, sub: str):
    user = User(
        name=name,
        email=email,
        picture=picture,
        google_sub=sub
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def store_refresh_token(db: Session, user_id: int, refresh_token: str):
    enc = encrypt_token(refresh_token)
    user = db.query(User).filter(User.id == user_id).first()
    user.refresh_token_enc = enc
    db.commit()
from sqlalchemy.orm import Session
from ..models.user import User
from ..utils.crypto import encrypt_token, decrypt_token


def get_user_by_sub(db: Session, sub: str):
    return db.query(User).filter(User.google_sub == sub).first()


def get_user_by_id(db: Session, user_id: int):
    """Needed for bookings & host access"""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, name: str, email: str, picture: str, sub: str):
    user = User(
        name=name,
        email=email,
        picture=picture,
        google_sub=sub
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def store_refresh_token(db: Session, user_id: int, refresh_token: str):
    enc = encrypt_token(refresh_token)
    user = db.query(User).filter(User.id == user_id).first()
    user.refresh_token_enc = enc
    db.commit()
