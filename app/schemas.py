from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Annotated

# class CreatePost(BaseModel):
#     title: str
#     content: str
#     published: bool=True

# class UpdatePost(BaseModel): # having only publish here mean user can only change published value
#     published: bool
class UserOut(BaseModel):
    id:int
    email: EmailStr
    created_at: datetime
    class Config:
        orm_mode=True

class UserCreate(BaseModel):
    email: EmailStr
    password: str


    
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PostBase(BaseModel):
    title: str
    content: str
    published: bool=True
    
class PostCreate(PostBase):
    pass




class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    id:Optional[int]=None

class vote(BaseModel):
    post_id:int
    dir: Annotated[int, Field(le=1)]
    

class CommentResponse(BaseModel):
    id: int
    content: str
    user_id: int

    class Config:
        orm_mode = True

    
class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    comments: list[CommentResponse] = []

    class Config:
        orm_mode = True

    

class PostOut(BaseModel):
    Post: Post
    votes:int
    class Config:
        orm_mode=True


class CommentCreate(BaseModel):
    content: str


class CommentOut(BaseModel):
    id: int
    content: str
    user_id: int
    post_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class CommentUpdate(BaseModel):
    content: str

class FollowCreate(BaseModel):
    following_id: int

class MessageCreate(BaseModel):
    receiver_id: int
    content: str

class MessageOut(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    is_seen: bool
    created_at: datetime

    class Config:
        orm_mode = True
