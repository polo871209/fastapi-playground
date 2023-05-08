from typing import Annotated, Type, List
from uuid import uuid4

import uvicorn
from fastapi import HTTPException, Depends, status, FastAPI, UploadFile
from fastapi.params import File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.models import DbUser, DbUserFile
from src.oauth2 import create_access_token, UserLogin
from src.router.file import check_file_exist
from src.schemas import FileOut
from src.utils.aws_s3 import upload_fileobj, create_presigned_url, delete_object
from src.utils.hash import verify_password

async_engine = create_async_engine('mysql+aiomysql://user:password@localhost/fastapi', future=True)
AsyncSessionMaker = async_sessionmaker(async_engine, class_=AsyncSession, future=True)


# Async Dependency
async def get_db() -> AsyncSession:
    async with AsyncSessionMaker() as session:
        yield session


GetDb = Annotated[AsyncSession, Depends(get_db)]

app = FastAPI()


def check_user_exist(user: Type[DbUser]) -> None:
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Invalid Credentials')


def check_password(plain_password: str, hashed_password: str) -> None:
    if not verify_password(plain_password, hashed_password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Invalid Credentials')


@app.post('/login')
async def login(db: GetDb, payload: OAuth2PasswordRequestForm = Depends()):
    stmt = select(DbUser).where(DbUser.email == payload.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    check_user_exist(user)  # Make sure check_user_exist is async or update accordingly
    check_password(payload.password, user.password)  # Make sure check_password is async or update accordingly

    access_token = create_access_token({'user_id': user.id})
    return {'access_token': access_token, 'token_type': 'bearer'}


@app.post('/', response_model=FileOut, status_code=status.HTTP_201_CREATED)
async def upload_file(
        user: UserLogin, db: GetDb,
        file: UploadFile = File()
):
    stmt = select(DbUserFile).where(DbUserFile.user_id == user.id, DbUserFile.file_name == file.filename)
    db_file = await db.execute(stmt)
    db_file = db_file.scalar_one_or_none()

    if not db_file:
        key = str(uuid4())
        if upload_fileobj(file.file, key):
            new_file = DbUserFile(user_id=user.id, file_name=file.filename, s3_key_name=key)
            db.add(new_file)
            await db.commit()
            await db.refresh(new_file)
            return new_file
    elif upload_fileobj(file.file, db_file.s3_key_name):
        return {'file_name': file.filename}

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='please try again')


@app.get('/all', response_model=List[FileOut])
async def list_all_files(
        user: UserLogin, db: GetDb
):
    stmt = select(DbUserFile).where(DbUserFile.user_id == user.id)
    result = await db.execute(stmt)
    files = result.scalars().all()

    check_file_exist(files)

    return files


@app.get('/{file_name}')
async def get_file(
        user: UserLogin, db: GetDb,
        file_name: str
):
    """temporary link for file download"""
    stmt = select(DbUserFile).where(DbUserFile.user_id == user.id, DbUserFile.file_name == file_name)
    file = await db.execute(stmt)
    file = file.scalar_one_or_none()

    check_file_exist(file)

    response = create_presigned_url(file.s3_key_name)
    if response:
        return response

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='please try again')


@app.delete('/{file_name}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
        user: UserLogin, db: GetDb,
        file_name: str
):
    stmt = select(DbUserFile).where(DbUserFile.user_id == user.id, DbUserFile.file_name == file_name)
    file = await db.execute(stmt)
    file = file.scalar_one_or_none()

    check_file_exist(file)

    if delete_object(file.s3_key_name):
        delete_stmt = DbUserFile.__table__.delete().where(DbUserFile.user_id == user.id,
                                                          DbUserFile.file_name == file_name)
        await db.execute(delete_stmt)
        await db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='please try again')


if __name__ == '__main__':
    uvicorn.run('test:app', reload=True)
