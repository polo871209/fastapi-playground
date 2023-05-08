from typing import List
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, status, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Query

from src.db import GetDb
from src.models import DbUserFile
from ..oauth2 import UserLogin
from ..schemas import FileOut
from ..utils.aws_s3 import upload_fileobj, create_presigned_url, delete_object

router = APIRouter(
    prefix='/file',
    tags=['File']
)
MB = 1048576


def check_file_size():
    pass


def check_file_exist(file) -> None:
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='file not found')


@router.post('/', response_model=FileOut, status_code=status.HTTP_201_CREATED)
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


@router.get('/all', response_model=List[FileOut])
async def list_all_files(
        user: UserLogin, db: GetDb
):
    stmt = select(DbUserFile).where(DbUserFile.user_id == user.id)
    result = await db.execute(stmt)
    files = result.scalars().all()

    check_file_exist(files)

    return files


@router.get('/{file_name}')
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


@router.delete('/{file_name}', status_code=status.HTTP_204_NO_CONTENT)
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
