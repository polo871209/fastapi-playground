from datetime import datetime, timedelta
from typing import Annotated, Type

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select

from .config import env
from . import models
from .db import GetDb
from .models import DbUser
from .schemas import TokenData

SECRET_KEY = env.SECRET_KEY
ALGORITHM = env.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = env.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/login')
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/login')


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        user_id: str = payload.get('user_id')
        if not user_id:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception

    return token_data


async def get_user(db: GetDb, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail='could not validate credentials',
                                          headers={'WWW-Authenticate': 'Bearer'})
    token_data = verify_access_token(token, credentials_exception)

    stmt = select(DbUser).where(DbUser.id == int(token_data.user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    return user


UserLogin = Annotated[Type[models.DbUser], Depends(get_user)]
