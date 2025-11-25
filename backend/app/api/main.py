from fastapi import APIRouter
from app.api.routers.v1 import article_tags, articles, medias, tags, users, votes
from app.api.routers.v1 import auth

api_router = APIRouter()

# api_router.include_router(article_tags.router)
# api_router.include_router(articles.router)
# api_router.include_router(medias.router)
# api_router.include_router(tags.router)
api_router.include_router(users.router)
# api_router.include_router(votes.router)
api_router.include_router(auth.router)