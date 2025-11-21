from schemas import User, UserLogin, UserResponse, UserUpdate
import models
from hashing import Hash
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from token_utils import create_access_token


def create_user(db: Session, user: User):
    print(user.station)
    existing_user = (
        db.query(models.Users)
        .filter(
            (models.Users.username == user.username)
            | (models.Users.email == user.email)
        )
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )
    station = (
        db.query(models.Stations).filter(models.Stations.id == user.station).first()
        if user.station
        else None
    )
    if not station:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Station not found"
        )

    new_user = models.Users(
        username=user.username,
        email=user.email,
        password=Hash.bcrypt(user.password),
        role=user.role,
        station_id=station.id if station else None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user(db: Session, username: str) -> UserResponse:
    user = db.query(models.Users).filter(models.Users.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserResponse.model_validate(user)


def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> list[UserResponse]:
    users = db.query(models.Users).offset(skip).limit(limit).all()
    return [UserResponse.model_validate(user) for user in users]


def login(db: Session, request: UserLogin):
    user = (
        db.query(models.Users).filter(models.Users.username == request.username).first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials"
        )

    user.last_login = datetime.now()
    db.commit()
    db.refresh(user)
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "station": user.station.id if user.station else None,
    }

def is_admin(user_username: str, db: Session) -> bool:
    user = db.query(models.Users).filter(models.Users.username == user_username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user.role == "admin"

def delete_user(db: Session, logged_user_username: str, user_username: str):
    if is_admin(logged_user_username, db) is False and logged_user_username != user_username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this user",
        )
    user = db.query(models.Users).filter(models.Users.username == user_username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

def update_user(db: Session, logged_user_username: str, user_username: str, updated_data: UserUpdate):
    if is_admin(logged_user_username, db) is False and logged_user_username != user_username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this user",
        )
    user = db.query(models.Users).filter(models.Users.username == user_username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if updated_data.username:
        user.username = updated_data.username
    if updated_data.email:
        user.email = updated_data.email
    if updated_data.password:
        user.password = Hash.bcrypt(updated_data.password)
    if updated_data.role:
        user.role = updated_data.role
    if updated_data.station:
        station = (
            db.query(models.Stations)
            .filter(models.Stations.id == updated_data.station)
            .first()
        )
        if not station:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Station not found"
            )
        user.station_id = station.id

    user.updated_at = datetime.now()
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)