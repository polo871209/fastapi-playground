from typing import List
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, status, HTTPException
from sqlalchemy.orm import Query

from ..database.database import GetDb
from ..database.models import DbUserFile
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


def check_file_exist(query: Query, file_name: str) -> None:
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'file {file_name} not found')


@router.post('/', response_model=FileOut, status_code=status.HTTP_201_CREATED)
def upload_file(user: UserLogin, db: GetDb, file: UploadFile = File()):
    db_file = db.query(DbUserFile).where(DbUserFile.user_id == user.id, DbUserFile.file_name == file.filename).first()
    if not db_file:
        key = str(uuid4())
        if upload_fileobj(file.file, key) == 'success':
            new_file = DbUserFile(user_id=user.id, file_name=file.filename, s3_key_name=key)
            db.add(new_file)
            db.commit()
            db.refresh(new_file)
            return new_file
    upload_fileobj(file.file, db_file.s3_key_name)
    return {'file_name': file.filename}


@router.get('/all', response_model=List[FileOut])
def list_all_files(user: UserLogin, db: GetDb):
    return db.query(DbUserFile).where(DbUserFile.user_id == user.id).all()


@router.get('/{file_name}')
def get_file(user: UserLogin, db: GetDb, file_name: str):
    file = db.query(DbUserFile).where(DbUserFile.user_id == user.id, DbUserFile.file_name == file_name)
    check_file_exist(file, file_name)
    return create_presigned_url(file_name)


@router.delete('/{filename}', status_code=status.HTTP_204_NO_CONTENT)
def delete_file(user: UserLogin, db: GetDb, file_name: str):
    file = db.query(DbUserFile).where(DbUserFile.user_id == user.id, DbUserFile.file_name == file_name)
    check_file_exist(file, file_name)
    file.delete(synchronize_session=False)
    db.commit()
    delete_object(file_name)
