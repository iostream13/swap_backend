import email
import hashlib
import imp
from lib2to3.pgen2 import token
from telnetlib import STATUS
from typing import List

from fastapi import Depends, FastAPI, Query, Body, status, Form, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Set
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session

from sql_app import crud, models, schemas
from sql_app.database import SessionLocal, engine 
from sql_app.models import Gender

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@app.get("/")
def show():
    return "hello"

@app.post("/usercreate/", response_model=schemas.UserCreate)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, user_name=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="username already registered")
    return crud.create_user(db, user)

@app.get("/user/{user_name}")
def read_user(user_name: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_name(db, user_name)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return user

@app.get("/userbalance/{user_name}")
def get_balance_of_user(user_name: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_name(db, user_name)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    balance = crud.get_user_balance_by_name(db, user_name)
    return balance

@app.post("/user/addbalance/")
def add_balance(user: str, token: str, amount: float, db: Session = Depends(get_db)):
    user_db = crud.get_user_by_name(db, user)
    if user_db is None:
        raise HTTPException(status_code=404, detail="user not found")
        return None
    token_db = crud.get_token_by_name(db, token)
    if token_db is None:
        raise HTTPException(status_code=404, detail="token not found")
        return None
    return crud.add_balance(db, user, token, amount)   #return None if balance < 0

@app.post("/update_user/", status_code = status.HTTP_201_CREATED)
def update_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_name(db, user.username) is None:
        raise HTTPException(status_code=404, detail="user not found")
        return None
    p = user.username + user.password
    hash_object = hashlib.sha256(p.encode())
    user.password = hash_object.hexdigest()
    user_update = crud.update_user(db, user)
    return user_update

@app.get("/check/")
def check_password(username: str, password: str, db: Session = Depends(get_db)):
    return crud.compare_password(db, username, password)
    
@app.get("/swap/cal")
def calculate_swap(token0: str, token1: str, amount: float, db: Session = Depends(get_db)):
    if crud.get_pool_by_token(db, token0, token1) is None:
        raise HTTPException(status_code=404, detail="pool not found")
        return None
    return crud.calculate(db, token0, token1, amount)
    
@app.post("/swap/")
def swap(token0: str, token1: str, amount: float, user: str, db: Session = Depends(get_db)):
    if crud.get_pool_by_token(db, token0, token1) is None:
        raise HTTPException(status_code=404, detail="pool not found")
        return None
    if crud.get_user_by_name(db, user) is None:
        raise HTTPException(status_code=404, detail="user not found")
        return None
    return crud.swap(db, token0, token1, amount, user)

@app.get("/pools/")
def get_list_pools(db: Session = Depends(get_db)):
    return crud.get_pools(db)

@app.get("/pools/id/{id}")
def get_pools_by_id(id: int, db: Session = Depends(get_db)):
    pool = crud.get_pool_by_id(db, id)
    if pool is None:
        return "Pool not found!"
    return pool

@app.get("/pools/token/")
def get_pools_by_token(token0: str, token1: str, db: Session = Depends(get_db)):
    pool = crud.get_pool_by_token(db, token0, token1)
    if pool is None:
        return "Pool not found!"
    return pool

@app.get("/tokens/")
def get_list_tokens(db: Session = Depends(get_db)):
    return crud.get_tokens(db)

@app.get("/logs/")
def get_all_logs(db: Session = Depends(get_db)):
    return crud.get_logs(db)

@app.get("/logs/pool/{id}")
def get_log_by_poolid(id: int, db: Session = Depends(get_db)):
    return crud.get_log_by_pool(db, id)

@app.get("/logs/user/{username}")
def get_log_by_username(username: str, db: Session = Depends(get_db)):
    return crud.get_log_by_username(db, username)

