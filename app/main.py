import uvicorn
from fastapi import FastAPI

from app.database.database import engine, mapper_registry
from router import post, user, auth, like

mapper_registry.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(user.router)
app.include_router(post.router)
app.include_router(auth.router)
app.include_router(like.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
