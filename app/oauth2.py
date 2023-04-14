from datetime import datetime, timedelta
from typing import Annotated, Type

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

import app.schemas as schema
from app.database import model
from app.database.database import GetDb

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        user_id: str = payload.get('user_id')
        if not user_id:
            raise credentials_exception
        token_data = schema.TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception

    return token_data


def get_user(db: GetDb, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail='could not validate credentials',
                                          headers={'WWW-Authenticate': 'Bearer'})
    token_data = verify_access_token(token, credentials_exception)
    user = db.query(model.User).where(model.User.id == token_data.user_id).first()
    return user


UserLogin = Annotated[Type[model.User], Depends(get_user)]
