from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .log import logger
from .router import main

app = FastAPI(
    title='Social Media',
    description='Develop by Polo',
    version='0.0.0.0',
    redoc_url=None,
)

# CORS settings
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['POST', 'GET', 'PUT', 'DELETE'],
    allow_headers=["*"],
)

# add routers
app.include_router(main.router)


@app.get('')
def home():
    return {'message': 'success'}


@app.get('/health')
def health():
    return {'status': 'healthy'}


logger.info('start logging')
