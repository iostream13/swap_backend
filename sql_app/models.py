from datetime import date
from operator import index
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, column, true, Enum, DateTime, Date
from sqlalchemy.orm import relationship
import enum

from .database import Base

class Gender(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    
class User(Base):
    __tablename__ = "user"
    
    username = Column(String(50), primary_key = True, index = True)
    password = Column(String(100))
    gender = Column(Enum(Gender))
    birthday = Column(Date)
    email = Column(String(100))
    phone = Column(String(15))
    bio = Column(String(500))
    
class Token(Base):
    __tablename__ = "token"
    
    tokenname = Column(String(50), primary_key = True, index = True)
    tokensymbol = Column(String(10))
    tokenimage = Column(String(1000))
    price = Column(Float)
    
class UserBalance(Base):
    __tablename__ = "userbalance"
    
    username = Column(String(50), ForeignKey("user.username"), primary_key = True)
    tokenname = Column(String(50), ForeignKey("token.tokenname"), primary_key = True)
    amount = Column(Float)
    
class Pool(Base):
    __tablename__ = "pool"
    
    poolid = Column(Integer, primary_key = True, index = True)
    token0 = Column(String(50), ForeignKey("token.tokenname"))
    token1 = Column(String(50), ForeignKey("token.tokenname"))
    reserve0 = Column(Float)
    reserve1 = Column(Float)
    token0price = Column(Float)
    token1price = Column(Float)
    tvl = Column(Float)
    
    
    
