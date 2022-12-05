from enum import Enum
from typing import List
from pydantic import BaseModel
from datetime import datetime

from .models import Gender

class UserCreate(BaseModel):
    username: str
    gender: Gender
    password: str
    birthday: datetime
    email: str 
    phone: str
    bio: str

    class Config:
        orm_mode = True
        
class Token(BaseModel):
    tokenname: str
    tokensymbol: str
    tokenimage: str
    price: float
    
    class Config:
        orm_mode = True
        
class UserBalance(BaseModel):
    username: str
    tokenname: str
    amount: float
    
    class Config:
        orm_mode = True
    
class Pool(BaseModel):
    poolid: int
    token0: str
    token1: str 
    reserve0: float
    reserve1: float 
    token0price: float
    token1price: float
    tvl: float
    
    class Config:
        orm_mode = True
    
class Transaction(BaseModel):
    txid: int
    username: str 
    poolid: int 
    amount0: float 
    amount1: float
    
    class Config:
        orm_mode = True
