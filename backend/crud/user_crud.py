# backend/crud/crud_user.py
from sqlalchemy.orm import Session
from models.users import User

def get_user_by_openid(db: Session, openid: str) -> User | None:
    return db.query(User).filter(User.wechat_openid == openid).first()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, openid: str, role: str = "student") -> User:
    db_user = User(wechat_openid=openid, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 20):
    return db.query(User).offset(skip).limit(limit).all()

def update_user(db: Session, db_user: User, update_data: dict) -> User:
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, db_user: User):
    db.delete(db_user)
    db.commit()