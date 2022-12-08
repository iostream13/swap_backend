import imp
from lib2to3.pgen2.token import OP
from statistics import mode
from time import time
from sqlalchemy import Interval, and_, asc, false, or_, not_, desc, asc, func, true
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pathlib import Path
import sys
import math
import json
import random


from . import models, schemas
from .models import Gender, UserBalance


def get_user_by_name(db: Session, user_name: str):
    return db.query(models.User).filter(models.User.username == user_name).first()


def get_user_balance_by_name(db: Session, user_name: str):
    return db.query(models.UserBalance).filter(models.UserBalance.username == user_name).all()


def get_user_balance_by_name_and_token(db: Session, user_name: str, token_name: str):
    return db.query(models.UserBalance).filter(and_(models.UserBalance.username == user_name, models.UserBalance.tokenname == token_name)).first()


def get_tokens(db: Session):
    return db.query(models.Token).all()


def get_pools(db: Session):
    return db.query(models.Pool).all()


def create_balance(db: Session, username: str, tokenname: str, amount: float):
    db_balance: models.UserBalance = db.query(models.UserBalance).filter(and_(
        models.UserBalance.username == username, models.UserBalance.tokenname == tokenname)).first()
    if db_balance is None:
        db_userbalance = models.UserBalance(
            username=username, tokenname=tokenname, amount=amount)
        db.add(db_userbalance)
        db.commit()
        db.refresh(db_userbalance)
        return db_userbalance
    return db_balance

def add_balance(db: Session, username: str, tokenname: str, amount: float):
    db_balance: models.UserBalance = db.query(models.UserBalance).filter(and_(
        models.UserBalance.username == username, models.UserBalance.tokenname == tokenname)).first()
    if db_balance is None:
        if amount < 0:
            return None
        db_userbalance = models.UserBalance(
            username=username, tokenname=tokenname, amount=amount)
        db.add(db_userbalance)
        db.commit()
        db.refresh(db_userbalance)
        return db_userbalance
    if db_balance.amount + amount < 0:
        return None
    db.query(models.UserBalance).filter(and_(
        models.UserBalance.username == username, models.UserBalance.tokenname == tokenname)).update({"amount": db_balance.amount + amount})
    db.commit()
    return db_balance

def create_user(db: Session, user: schemas.UserCreate):
    bio = ""
    if user.bio is not None:
        bio = user.bio
    birthday = ""
    if user.birthday is not None:
        birthday = user.birthday
    email = ""
    if user.email is not None:
        email = user.email
    phone = ""
    if user.phone is not None:
        phone = user.phone
    db_user = models.User(username=user.username,
                          password=user.password, gender=user.gender, birthday=birthday, email=email, phone=phone, bio=bio)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    add_balance(db, user.username, tokenname="Bitcoin", amount=50)
    return db_user

def update_user(db: Session, user: schemas.UserCreate):
    password = ""
    if user.password is not None:
        password = user.password
    gender = ""
    if user.gender is not None:
        gender = user.gender
    bio = ""
    if user.bio is not None:
        bio = user.bio
    birthday = ""
    if user.birthday is not None:
        birthday = user.birthday
    email = ""
    if user.email is not None:
        email = user.email
    phone = ""
    if user.phone is not None:
        phone = user.phone
    db_user = models.User(username=user.username,
                          password=password, gender=gender, birthday=birthday, email=email, phone=phone, bio=bio)
    db.query(models.User).filter(models.User.username == user.username).update({"password": password, "gender": gender, 
                                                                                "birthday": birthday, "email": email, "phone": phone, "bio": bio})
    db.commit()
    return db_user

def find_token(db: Session, token: str):
    data_token = db.query(models.Token).filter(
        models.Token.tokenname == token).first()
    return data_token


def sort_tokens(token1: str, token2: str):
    if token1 > token2:
        token1, token2 = token2, token1
    return token1, token2


def check_balance(db: Session, username: str, token: str, amount: float):
    user: models.UserBalance = db.query(models.UserBalance).filter(and_(
        models.UserBalance.username == username, models.UserBalance.tokenname == token)).first()
    if user is None or user.amount < amount:
        return "NO"
    return "OK"

def increase_user_token_balance(db: Session, username: str, token: str, delta: float):
    balance: models.UserBalance = db.query(models.UserBalance).filter(and_(
        models.UserBalance.username == username, models.UserBalance.tokenname == token)).first()
    if balance is None:
        if delta < 0:
            return "NO"
        balance = add_balance(db, username, token, delta)
    else:
        if balance.amount + delta < 0:
            return "NO"
        db.query(models.UserBalance).filter(and_(
            models.UserBalance.username == username, models.UserBalance.tokenname == token)).update({"amount": balance.amount + delta})
        db.commit()
    return "OK"

# pool: none
def get_pool(db: Session, token0: str, token1: str):
    pool: models.Pool = db.query(models.Pool).filter(and_(
        models.Pool.token0 == token0, models.Pool.token1 == token1)).first()
    if pool is None:
        pool = db.query(models.Pool).filter(and_(
            models.Pool.token0 == token1, models.Pool.token1 == token0)).first()
    return pool 

def calculate(db: Session, token0: str, token1: str, amount: float):
    pool: models.Pool = get_pool(db, token0, token1)
    if token0 == pool.token0:
       new_reserve0 =  pool.reserve0 + amount 
       new_reserve1 = (pool.reserve0 * pool.reserve1) / new_reserve0
       user_get = pool.reserve1 - new_reserve1
       return [user_get, 0]
    new_reserve1 =  pool.reserve1 + amount
    new_reserve0 = (pool.reserve0 * pool.reserve1) / new_reserve1
    user_get = pool.reserve0 - new_reserve0
    return [user_get, 1]

def swap(db: Session, token0: str, token1: str, amount: float, user_name: str):
    pool: models.Pool = get_pool(db, token0, token1)
    if check_balance(db, user_name, token0, amount) == "NO":
        return "Balance is not enough"
    return_state = calculate(db, token0, token1, amount)
    increase_user_token_balance(db, user_name, token0, -amount)
    increase_user_token_balance(db, user_name, token1, return_state[0])
    new_reserve0 = 0
    new_reserve1 = 0
    new_tvl = 0
    if return_state[1] == 0:
        new_reserve0 = pool.reserve0 + amount
        new_reserve1 = pool.reserve1 - return_state[0]
        new_tvl = new_reserve0 * pool.token0price + new_reserve1 * pool.token1price
    else:
        new_reserve1 = pool.reserve1 + amount
        new_reserve0 = pool.reserve0 - return_state[0]
        new_tvl = new_reserve0 * pool.token0price + new_reserve1 * pool.token1price
    db.query(models.Pool).filter(models.Pool.poolid == pool.poolid).update({"reserve0": new_reserve0, "reserve1": new_reserve1, "tvl": new_tvl})
    db.commit()
    return "OK"
    

