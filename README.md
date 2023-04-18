# fastapi-playground

## create table 
```
alembic upgrade head
```
## start app
docker build 
```
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000 
```
### Naming rules
- sqlalchemy models: Db${Dbname}
- response pydantic Base: ${Base}Out
- create pydantic Base: ${Base}Create
