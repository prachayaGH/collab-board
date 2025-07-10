from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate,OAuthUserCreate
from backend.app.core.security import hash_password

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate): # Use UserSignup as the input schema
    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        password=hashed_password,
        oauth_provider=user.oauth_provider,
        oauth_id=user.oauth_id,
        display_name=user.display_name,
        avatar_url=user.avatar_url
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_oauth_id(db: Session, provider: str, oauth_id: str):
    return db.query(User).filter(
        User.oauth_provider == provider,
        User.oauth_id == oauth_id
    ).first()

def create_oauth_user(db: Session, user: OAuthUserCreate):
    db_user = User(
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        oauth_provider=user.oauth_provider,
        oauth_id=user.oauth_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
