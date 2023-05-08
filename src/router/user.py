from fastapi import APIRouter, Body, status, HTTPException
from sqlalchemy import update, select, cast, Integer
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm.query import Query

from src.db import GetDb
from src.models import DbUser
from ..oauth2 import UserLogin
from ..schemas import UserOut, UserCreate
from ..utils.hash import get_password_hash

router = APIRouter(
    prefix='/user',
    tags=['User']
)


@router.post('/', response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(db: GetDb, payload: UserCreate = Body()):
    try:
        payload.password = get_password_hash(payload.password)
        new_user = DbUser(**payload.dict())
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except DBAPIError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='email already exist')

    return new_user


@router.get('/', response_model=UserOut)
async def get_current_user(user: UserLogin, db: GetDb):
    user_stmt = select(DbUser).where(DbUser.id == user.id)
    result = await db.execute(user_stmt)
    current_user = result.scalar_one()

    return current_user


@router.put('/', response_model=UserOut, status_code=status.HTTP_202_ACCEPTED)
async def update_current_user(user: UserLogin, db: GetDb, payload: UserCreate = Body()):
    try:
        payload.password = get_password_hash(payload.password)
        update_stmt = (
            update(DbUser)
            .where(DbUser.id == user.id)
            .values(**payload.dict())
        ).returning(DbUser)
        result = await db.execute(update_stmt)
        return result.fetchone()[0].__dict__
    except DBAPIError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='email already exist')

# @router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
# def delete_current_user(user: UserLogin, db: GetDb) -> None:
#     current_user = db.query(models.User).where(models.User.id == user.id)
#     if not current_user.first():
#         return None
#     current_user.delete(synchronize_session=False)
#     db.commit()
