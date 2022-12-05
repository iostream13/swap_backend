from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

sqlalchemy_database_url = "mysql+mysqlconnector://root:hien1308@localhost:3306/bakaswap"

engine = create_engine(
    sqlalchemy_database_url,
    pool_size=15, 
    max_overflow=20
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()