import imp
from lib2to3.pgen2.token import OP
from statistics import mode
from time import time
from sqlalchemy import Interval, and_, asc, false, or_, not_, desc, asc, func, true
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
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

def get_token_by_symbol(db: Session, symbol: str):
    return db.query(models.Token).filter(models.Token.tokensymbol == symbol).first()

# pool: none
def get_pool_by_token(db: Session, token0: str, token1: str):
    pool: models.Pool = db.query(models.Pool).filter(and_(
        models.Pool.token0 == token0, models.Pool.token1 == token1)).first()
    if pool is None:
        pool: models.Pool = db.query(models.Pool).filter(and_(
            models.Pool.token0 == token1, models.Pool.token1 == token0)).first()
    return pool 

# pool: none
def get_pool_by_id(db: Session, id: int):
    pool: models.Pool = db.query(models.Pool).filter(models.Pool.poolid == id).first()
    return pool 

def get_token_by_name(db: Session, token: str):
    data_token = db.query(models.Token).filter(
        models.Token.tokenname == token).first()
    return data_token

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
        return "Success"
    return "Fail. Token exist"

def add_balance(db: Session, username: str, tokenname: str, amount: float):
    db_balance: models.UserBalance = db.query(models.UserBalance).filter(and_(
        models.UserBalance.username == username, models.UserBalance.tokenname == tokenname)).first()
    if db_balance is None:
        if amount < 0:
            return "Failed. Negative amount!"
        return create_balance(db, username, tokenname, amount)
    if db_balance.amount + amount < 0:
        return "Failed. Negative amount!"
    db.query(models.UserBalance).filter(and_(
                models.UserBalance.username == username, models.UserBalance.tokenname == tokenname)).update({"amount": db_balance.amount + amount})
    db.commit()
    now = datetime.utcnow()
    db_log = models.BalanceLog(
                username=username, tokenname=tokenname, amount = amount, timestamp = now)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return "Success"

def create_user(db: Session, user: schemas.UserCreate):
    p = user.username + user.password
    hash_object = hashlib.sha256(p.encode())
    password = hash_object.hexdigest()
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
                          password=password, gender=user.gender, birthday=birthday, email=email, phone=phone, bio=bio)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def compare_password(db: Session, username: str, password: str): 
    user: models.User = db.query(models.User).filter(
        models.User.username == username).first()
    p = username + password
    hash_object = hashlib.sha256(p.encode())
    hash_password = hash_object.hexdigest()
    if hash_password == user.password:
        return "match"
    return "not match"

def update_user(db: Session, user: schemas.UserCreate):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    update_data = user.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


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

def calculate(db: Session, token0: str, token1: str, amount: float):
    pool: models.Pool = get_pool_by_token(db, token0, token1)
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
    pool: models.Pool = get_pool_by_token(db, token0, token1)
    t0: models.Token = get_token_by_name(db, token0)
    t1: models.Token = get_token_by_name(db, token1)
    if check_balance(db, user_name, token0, amount) == "NO":
        return "Balance is not enough"
    return_state = calculate(db, token0, token1, amount)
    add_balance(db, user_name, token0, -amount)
    add_balance(db, user_name, token1, return_state[0])
    try:
        db.begin()
        new_reserve0 = 0
        new_reserve1 = 0
        amounttoken0 = 0
        amounttoken1 = 0
        new_tvl = 0
        if return_state[1] == 0:
            new_reserve0 = pool.reserve0 + amount
            new_reserve1 = pool.reserve1 - return_state[0]
            new_tvl = new_reserve0 * t0.price + new_reserve1 * t1.price
            amounttoken0 = -amount
            amounttoken1 = return_state[0]
        else:
            new_reserve0 = pool.reserve1 + amount
            new_reserve1 = pool.reserve0 - return_state[0]
            new_tvl = new_reserve0 * t0.price + new_reserve1 * t1.price
            amounttoken1 = -amount
            amounttoken0 = return_state[0]
        db.query(models.Pool).filter(models.Pool.poolid == pool.poolid).update({"reserve0": new_reserve0, "reserve1": new_reserve1, "tvl": new_tvl})
        now = datetime.utcnow()
        db_log = models.SwapLog(
                username=user_name, poolid=pool.poolid, timestamp = now, amounttoken0 = amounttoken0, amounttoken1 = amounttoken1)
        
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return "Success"
    except:
        db.rollback()
        return "Failed"
    
def get_logs(db: Session):
    logs = db.query(models.SwapLog).order_by(desc(models.SwapLog.timestamp)).all()
    result = []
    for tx in logs:
        pool: models.Pool = get_pool_by_id(db, tx.poolid)
        token0: models.Token = get_token_by_name(db, pool.token0)
        log = {}
        log["swaplogid"] = tx.swaplogid
        log["username"] = tx.username
        log["poolid"] = tx.poolid
        log["timestamp"] = tx.timestamp
        log["amounttoken0"] = tx.amounttoken0
        log["amounttoken1"] = tx.amounttoken1
        log["token0"] = pool.token0
        log["token1"] = pool.token1
        log["volume"] = token0.price * abs(tx.amounttoken0)
        result.append(log)
    return result

def get_log_by_username(db: Session, username: str):
    logs = db.query(models.SwapLog).filter(models.SwapLog.username == username).order_by(desc(models.SwapLog.timestamp)).all()
    result = []
    for tx in logs:
        pool: models.Pool = get_pool_by_id(db, tx.poolid)
        token0: models.Token = get_token_by_name(db, pool.token0)
        log = {}
        log["swaplogid"] = tx.swaplogid
        log["username"] = tx.username
        log["poolid"] = tx.poolid
        log["timestamp"] = tx.timestamp
        log["amounttoken0"] = tx.amounttoken0
        log["amounttoken1"] = tx.amounttoken1
        log["token0"] = pool.token0
        log["token1"] = pool.token1
        log["volume"] = token0.price * abs(tx.amounttoken0)
        result.append(log)
    return result

def get_log_by_pool(db: Session, poolid: int):
    logs = db.query(models.SwapLog).filter(models.SwapLog.poolid == poolid).order_by(desc(models.SwapLog.timestamp)).all()
    pool: models.Pool = get_pool_by_id(db, poolid)
    token0: models.Token = get_token_by_name(db, pool.token0)
    result = []
    for tx in logs:
        log = {}
        log["swaplogid"] = tx.swaplogid
        log["username"] = tx.username
        log["poolid"] = tx.poolid
        log["timestamp"] = tx.timestamp
        log["amounttoken0"] = tx.amounttoken0
        log["amounttoken1"] = tx.amounttoken1
        log["token0"] = pool.token0
        log["token1"] = pool.token1
        log["volume"] = token0.price * abs(tx.amounttoken0)
        result.append(log)
    return result

def get_balance_log_by_username(db: Session, user: int):
    logs = db.query(models.BalanceLog).filter(models.BalanceLog.username == user).order_by(desc(models.BalanceLog.timestamp)).all()
    return logs
