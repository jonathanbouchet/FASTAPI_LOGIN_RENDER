from sqlalchemy.orm import Session
from models.user_model import User
from typing import Dict, Any
from security import authSecurity

def create_user(db: Session, signup:User) -> bool:
        try:
            db.add(signup)
            db.commit()
        except:
            return False
        return True

def get_user_by_username(db: Session, username:str):
    return db.query(User).filter(User.username==username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db=db, username=username)
    print(f"in authenticate_user: {user}")
    print(f"from input plain password: {password}, username :{username}")
    print(f"from user plain password: {user.password}, hashed_password :{user.hashed_password}")
    if not user:
        return False
    if not authSecurity.verify_password(password, user.hashed_password):
        return False
    return user
