from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# =========================================================
# USER
# =========================================================

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=30
    )

    email: EmailStr

    password: str = Field(
        min_length=8
    )

    full_name: Optional[str] = Field(
        None,
        max_length=120
    )


class UserUpdate(BaseModel):
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=30
    )

    full_name: Optional[str] = Field(
        None,
        max_length=120
    )

    bio: Optional[str] = None

    avatar_url: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserSearchOut(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


# =========================================================
# AUTH
# =========================================================

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None



# =========================================================
# COMMENT
# =========================================================

class CommentCreate(BaseModel):
    content: str = Field(min_length=1)


class CommentResponse(BaseModel):
    id: int
    content: str
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CommentOut(BaseModel):
    id: int
    content: str
    user_id: int
    post_id: int
    created_at: datetime

    user: UserOut

    model_config = {
        "from_attributes": True
    }
class CommentUpdate(BaseModel):
    content: str = Field(min_length=1)


# =========================================================
# POST
# =========================================================

class PostBase(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255
    )

    content: str = Field(
        min_length=1
    )

    published: bool = True


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255
    )

    content: Optional[str] = Field(
        None,
        min_length=1
    )

    published: Optional[bool] = None


class Post(BaseModel):
    id: int

    title: str

    content: str

    published: bool

    owner_id: int

    image_url: Optional[str] = None

    created_at: datetime

    owner: UserOut

    comments: list[CommentResponse] = []

    model_config = {
        "from_attributes": True
    }


class PostOut(BaseModel):
    Post: Post
    votes: int

    model_config = {
        "from_attributes": True
    }


# =========================================================
# VOTE
# =========================================================

class Vote(BaseModel):
    post_id: int

    dir: int = Field(
        ...,
        ge=0,
        le=1,
        description="1 = like, 0 = remove like"
    )


# =========================================================
# FOLLOW
# =========================================================

class FollowCreate(BaseModel):
    following_id: int


class FollowOut(BaseModel):
    follower_id: int
    following_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# =========================================================
# MESSAGE
# =========================================================

class MessageCreate(BaseModel):
    receiver_id: int

    content: Optional[str] = None

    image_url: Optional[str] = None

    audio_url: Optional[str] = None


class MessageOut(BaseModel):
    id: int

    sender_id: int

    receiver_id: int

    content: Optional[str] = None

    image_url: Optional[str] = None

    audio_url: Optional[str] = None

    is_seen: bool

    created_at: datetime

    model_config = {"from_attributes": True}



class UserProfile(BaseModel):
    id: int

    username: str

    email: EmailStr

    full_name: Optional[str] = None

    bio: Optional[str] = None

    avatar_url: Optional[str] = None

    followers: int

    following: int

    posts_count: int

    is_following: bool

    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class UserMini(BaseModel):
    id: int
    username: str

    full_name: Optional[str] = None

    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}

# ------------------------------------------
# FEED
# ------------------------------------------
class FeedOut(BaseModel):
    post: Post

    likes: int

    comments: int

    is_liked: bool

    is_owner: bool

    model_config = {
        "from_attributes": True
    }

# --------------------------
# NOTIFICATION
# =-----------------------

class NotificationActor(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}

class NotificationOut(BaseModel):
    id: int

    actor: NotificationActor

    type: str

    reference_id: Optional[int] = None

    is_read: bool

    created_at: datetime

    model_config = {"from_attributes": True}
# ------------------------
# MESSAGES
# --------------------------------------------

class InboxUser(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


class InboxConversation(BaseModel):
    user: InboxUser

    last_message: Optional[str] = None

    # "text" | "image" | "audio" — lets the frontend decide how to render
    last_message_type: str = "text"

    last_message_time: datetime

    unread_count: int




class ProfilePostOut(BaseModel):

    post: Post

    likes: int

    comments: int

    is_liked: bool

    is_owner: bool

    model_config = {
        "from_attributes": True
    }