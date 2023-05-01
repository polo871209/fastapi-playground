from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from.database.database import database
from .database import database
from .log import logger
from .router import post, user, auth, like, comment, file

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


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# add routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(post.router)
app.include_router(like.router)
app.include_router(file.router)
app.include_router(comment.router)

logger.info('application start successfully')
