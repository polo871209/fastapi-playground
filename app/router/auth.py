from typing import Type

from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import app.schemas as schema
from app.database import model
from app.database.database import get_db
from app.oauth2 import create_access_token
from app.utils.hash import verify_password

router = APIRouter(
    prefix='/login',
    tags=['auth']
)


def check_user_exist(user: Type[model.User]) -> None:
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Invalid Credentials')


def check_password(plain_password: str, hashed_password: str) -> None:
    if not verify_password(plain_password, hashed_password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Invalid Credentials')


@router.post('/', response_model=schema.TokenOut)
def login(payload: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(model.User).where(model.User.email == payload.username).first()
    check_user_exist(user)
    check_password(payload.password, user.password)
    access_token = create_access_token({'user_id': user.id})
    return {'access_token': access_token, 'token_type': 'bearer'}
