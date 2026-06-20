from . import models
from fastapi import FastAPI
from .database import engine
from .routers import post, user, auth, vote,comment,follow,message,chat
from .config import settings
from fastapi.middleware.cors import CORSMiddleware
# models.Base.metadata.create_all(bind=engine) //alembic can work

app=FastAPI()
origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)
app.include_router(comment.router)
app.include_router(follow.router)
app.include_router(message.router)
app.include_router(chat.router)
@app.get("/")
async def root():
    return {"message": "Hello World"}
