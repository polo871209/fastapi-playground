from typing import Type

from fastapi import APIRouter, Body, status, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

import app.schemas as schema
from app.database import model
from app.database.database import get_db
from app.utils.hash import get_password_hash

router = APIRouter(
    prefix='/user',
    tags=['user']
)


def check_user_exist(query: Query, user_id: int) -> None:
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'user with id {user_id} does not exist')


@router.post('/', response_model=schema.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: schema.UseCreate = Body(), db: Session = Depends(get_db)) -> schema.UserOut:
    payload.password = get_password_hash(payload.password)  # hash password
    new_user = model.User(**payload.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get('/{user_id}', response_model=schema.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)) -> Type[schema.UserOut]:
    user = db.query(model.User).filter(model.User.id == user_id)
    check_user_exist(user, user_id)

    return user.first()
