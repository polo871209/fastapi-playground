FROM python:3.11.3-buster
# working directory
WORKDIR /app
# copy and install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt
# copy all the require codes
COPY . .
# expose port
EXPOSE ${PORT}
# create mysql tables and starup application
CMD alembic upgrade head&&uvicorn src.main:app --host 0.0.0.0 --port ${PORT}