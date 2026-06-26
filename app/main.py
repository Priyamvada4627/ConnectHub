from . import models
from fastapi import FastAPI
from .database import engine
from .routers import post, user, auth, vote, comment, follow, message, chat,profile,feed,notification
from .config import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ConnectHub API",
    description="Backend API for ConnectHub, a real-time social networking platform.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
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
app.include_router(profile.router)
app.include_router(feed.router)
app.include_router(notification.router)


@app.get("/", tags=["Health"])
async def root():
    return {
    "status": "ok",
    "message": "ConnectHub API is running"
}
