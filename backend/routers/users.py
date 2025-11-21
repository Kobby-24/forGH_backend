from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import User, UserLogin, UserResponse, UserUpdate
from utils.users import create_user, get_user, get_all_users, login as user_login, delete_user, update_user


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", response_model=UserResponse)
def create_new_user(user: User, db: Session = Depends(get_db)):
    return create_user(db, user)

@router.get("/{username}", response_model=UserResponse)
def read_user(username: str, db: Session = Depends(get_db)):
    return get_user(db, username)   

@router.get("/", response_model=list[UserResponse])
def read_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_all_users(db, skip, limit)

@router.post("/login")
def login(request: UserLogin, db: Session = Depends(get_db)):
    return user_login(db, request)

@router.delete("/{user_username}/{logged_in_user_username}")
def delete_user_route(user_username: str, logged_in_user_username: str, db: Session = Depends(get_db)):
    return delete_user(db, logged_in_user_username, user_username)

@router.put("/{user_username}/{logged_in_user_username}")
def update_user_route(user_username: str, logged_in_user_username: str, updated_data: UserUpdate, db: Session = Depends(get_db)):
    return update_user(db, logged_in_user_username, user_username, updated_data)