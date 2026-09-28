"""Authentication service for user registration and JWT issuance."""

from datetime import timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserResponse
from app.utils.security import create_access_token, get_password_hash, verify_password


class AuthService:
    """Handles user registration, authentication, and JWT lifecycle."""

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email.lower().strip()).first()

    @staticmethod
    def register_user(db: Session, user_in: UserCreate) -> User:
        existing = AuthService.get_by_email(db, user_in.email)
        if existing:
            raise ValueError(f"User with email '{user_in.email}' already exists.")

        user = User(
            email=user_in.email.lower().strip(),
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name.strip(),
            role=user_in.role if user_in.role in ["admin", "user"] else "user",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        user = AuthService.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user

    @staticmethod
    def create_user_token(user: User) -> Token:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }
        access_token = create_access_token(token_data, expires_delta=access_token_expires)
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            user=UserResponse.model_validate(user),
        )
