from fastapi import APIRouter
from . import auth, comment, file, like, post, user

router = APIRouter(
    prefix='/api',
)

router.include_router(auth.router)
# router.include_router(comment.router)
# router.include_router(file.router)
# router.include_router(like.router)
router.include_router(post.router)
# router.include_router(user.router)
