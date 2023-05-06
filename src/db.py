from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import env

engine = create_engine(env.SQLALCHEMY_DATABASE_URL, future=True)
Session = sessionmaker(bind=engine, future=True)


# Dependency
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


GetDb = Annotated[Session, Depends(get_db)]
