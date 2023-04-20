from enum import Enum
from typing import List
from pydantic import BaseModel
from datetime import datetime, date

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
    marketcap: int
    
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
    tvl: float
    
    class Config:
        orm_mode = True
    
class SwapLog(BaseModel):
    swaplogid: int
    username: str 
    poolid: int 
    timestamp: datetime
    amounttoken0: float 
    amounttoken1: float
    
    class Config:
        orm_mode = True

class BalanceLog(BaseModel):
    balancelogid: int
    username: str 
    tokenname: str
    amount: float
    timestamp: datetime
    
    class Config:
        orm_mode = True