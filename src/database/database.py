import databases
import sqlalchemy
from sqlalchemy.orm import registry

from ..config import env
from typing import Type, Optional, List

from fastapi import APIRouter, Body, status, HTTPException, Path, Query as Parameters
from sqlalchemy.orm.query import Query

from ..database.models import DbPost, DbUser
from ..oauth2 import UserLogin
from ..schemas import PostCreate, PostOut

DATABASE_URL = env.SQLALCHEMY_DATABASE_URL
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False},
    future=True
)

# engine = create_engine(env.SQLALCHEMY_DATABASE_URL, future=True)
# Session = sessionmaker(bind=engine, future=True)
#
mapper_registry = registry()
query = DbPost.select()
print(database.fetch_all(query))
#
#
# # Dependency
# def get_db():
#     db = Session()
#     try:
#         yield db
#     finally:
#         db.close()
#
#
# GetDb = Annotated[Session, Depends(get_db)]
