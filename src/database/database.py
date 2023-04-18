from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, registry

from ..config import env

engine = create_engine(env.SQLALCHEMY_DATABASE_URL, future=True)
Session = sessionmaker(bind=engine, future=True)

mapper_registry = registry()


# Dependency
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


GetDb = Annotated[Session, Depends(get_db)]
