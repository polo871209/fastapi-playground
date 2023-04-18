FROM python:3.11.3-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["alembic", "upgrade", "head"]
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]