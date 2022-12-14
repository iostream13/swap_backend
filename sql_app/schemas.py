from enum import Enum
from typing import List
from pydantic import BaseModel
from datetime import date

from .models import Gender

class UserCreate(BaseModel):
    username: str
    gender: Gender
    password: str
    birthday: date
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

