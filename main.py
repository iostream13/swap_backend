import email
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

@app.get("/pools/")
def get_markets(db: Session = Depends(get_db)):
    return crud.get_pools(db)


@app.get("/tokens/")
def get_tokens(db: Session = Depends(get_db)):
    return crud.get_tokens(db)

@app.post("/usercreate/", response_model=schemas.UserCreate)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, user_name=user.username)
    if db_user:
        raise HTTPException(
            status_code=400, detail="username already registered")
    return crud.create_user(db, user)


@app.get("/user/{user_name}")
def read_user(user_name: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_name(db, user_name)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return user


@app.get("/userbalance/{user_name}")
def read_user(user_name: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_name(db, user_name)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    balance = crud.get_user_balance_by_name(db, user_name)
    return balance


@app.post("/user/addbalance/{user}")
def add_balance(user: str, token: str, amount: float, db: Session = Depends(get_db)):
    user_db = crud.get_user_by_name(db, user)
    if user_db is None:
        raise HTTPException(status_code=404, detail="user not found")
        return None
    token_db = crud.find_token(db, token)
    if token_db is None:
        raise HTTPException(status_code=404, detail="token not found")
        return None
    # return None if balance < 0
    return crud.add_balance(db, user, token, amount)


@app.post("/update_user/", status_code=status.HTTP_201_CREATED)
def update(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_name(db, user.username) is None:
        raise HTTPException(status_code=404, detail="user not found")
        return None
    user_update = crud.update_user(db, user)
    return user_update


@app.get("/swap/cal")
def cal_swap(token0: str, token1: str, amount: float, db: Session = Depends(get_db)):
    if crud.get_pool(db, token0, token1) is None:
        raise HTTPException(status_code=404, detail="pool not found")
        return None
    return crud.calculate(db, token0, token1, amount)


@app.post("/swap/")
def cal_swap(token0: str, token1: str, amount: float, user: str, db: Session = Depends(get_db)):
    if crud.get_pool(db, token0, token1) is None:
        raise HTTPException(status_code=404, detail="pool not found")
        return None
    if crud.get_user_by_name(db, user) is None:
        raise HTTPException(status_code=404, detail="user not found")
        return None
    return crud.swap(db, token0, token1, amount, user)

