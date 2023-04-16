from fastapi import APIRouter, Body, status, HTTPException
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm.query import Query

from app import schemas
from app.database import models
from app.database.database import GetDb
from app.oauth2 import UserLogin
from app.utils.hash import get_password_hash

router = APIRouter(
    prefix='/user',
    tags=['User']
)


def check_user_exist(query: Query, user_id: int) -> None:
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'user with id {user_id} does not exist')


@router.post('/', response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(db: GetDb, payload: schemas.UserCreate = Body()):
    try:
        payload.password = get_password_hash(payload.password)
        new_user = models.User(**payload.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except DBAPIError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='email already exist')

    return new_user


@router.get('/', response_model=schemas.UserOut)
def get_current_user(user: UserLogin, db: GetDb):
    return db.query(models.User).filter(models.User.id == user.id).first()


@router.put('/', response_model=schemas.UserOut, status_code=status.HTTP_202_ACCEPTED)
def update_current_user(user: UserLogin, db: GetDb, payload: schemas.UserCreate = Body()):
    updated_user = db.query(models.User).where(models.User.id == user.id)
    payload.password = get_password_hash(payload.password)
    updated_user.update(payload.dict(), synchronize_session=False)
    db.commit()

    return updated_user.first()


# @router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
# def delete_current_user(user: UserLogin, db: GetDb) -> None:
#     current_user = db.query(models.User).where(models.User.id == user.id)
#     if not current_user.first():
#         return None
#     current_user.delete(synchronize_session=False)
#     db.commit()
