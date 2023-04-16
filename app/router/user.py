from fastapi import APIRouter, Body, status, HTTPException, Path
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm.query import Query

from app import schemas
from app.database import models
from app.database.database import GetDb
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


@router.get('/{user_id}', response_model=schemas.UserOut)
def get_user(db: GetDb, user_id: int = Path()):
    user = db.query(models.User).filter(models.User.id == user_id)
    check_user_exist(user, user_id)

    return user.first()
