from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, registry

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://user:password@localhost/fastapi"

engine = create_engine(SQLALCHEMY_DATABASE_URL, future=True)
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
