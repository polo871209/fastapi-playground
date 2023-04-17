from typing import Type

from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from src.database.database import GetDb
from src.database.models import DbUser
from src.oauth2 import create_access_token
from src.schemas import TokenOut
from src.utils.hash import verify_password

router = APIRouter(
    prefix='/login',
    tags=['Auth']
)


def check_user_exist(user: Type[DbUser]) -> None:
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Invalid Credentials')


def check_password(plain_password: str, hashed_password: str) -> None:
    if not verify_password(plain_password, hashed_password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Invalid Credentials')


@router.post('/', response_model=TokenOut)
def login(db: GetDb, payload: OAuth2PasswordRequestForm = Depends()):
    user = db.query(DbUser).where(DbUser.email == payload.username).first()
    check_user_exist(user)
    check_password(payload.password, user.password)
    access_token = create_access_token({'user_id': user.id})
    return {'access_token': access_token, 'token_type': 'bearer'}
