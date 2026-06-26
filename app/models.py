from .database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Index,
    Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text


# =========================================================
# USER
# =========================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(String(50), unique=True, nullable=False)

    email = Column(String(255), unique=True, nullable=False)

    password = Column(String, nullable=False)

    full_name = Column(String(120))

    bio = Column(Text)

    avatar_url = Column(String)

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )

    posts = relationship("Post", back_populates="owner")

    comments = relationship("Comment", back_populates="user")

    __table_args__ = (
        Index("ix_users_username", "username"),
        Index("ix_users_email", "email"),
    )

    followers = relationship(
    "Follow",
    foreign_keys="Follow.following_id",
    cascade="all, delete"
    )

    following = relationship(
    "Follow",
    foreign_keys="Follow.follower_id",
    cascade="all, delete"
    )

# =========================================================
# POST
# =========================================================

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)

    title = Column(String(255))

    content = Column(Text, nullable=False)

    image_url = Column(String)

    published = Column(
        Boolean,
        nullable=False,
        server_default="TRUE"
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )

    owner = relationship("User", back_populates="posts")

    comments = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete"
    )

    votes = relationship(
        "Vote",
        back_populates="post",
        cascade="all, delete"
    )

    __table_args__ = (
        Index("ix_posts_owner_id", "owner_id"),
        Index("ix_posts_created_at", "created_at"),
    )


# =========================================================
# COMMENT
# =========================================================

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)

    content = Column(Text, nullable=False)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    post_id = Column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )

    user = relationship("User", back_populates="comments")

    post = relationship("Post", back_populates="comments")


# =========================================================
# LIKE
# =========================================================

class Vote(Base):
    __tablename__ = "votes"

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    post_id = Column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True
    )

    post = relationship("Post", back_populates="votes")


# =========================================================
# FOLLOW
# =========================================================

class Follow(Base):
    __tablename__ = "follows"

    follower_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    following_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )


# =========================================================
# MESSAGE
# =========================================================

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)

    sender_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    receiver_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    content = Column(Text)

    image_url = Column(String)

    audio_url = Column(String)

    is_seen = Column(
        Boolean,
        nullable=False,
        server_default="FALSE"
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )

    __table_args__ = (
        Index("ix_messages_sender_receiver",
              "sender_id",
              "receiver_id"),
        Index("ix_messages_created_at",
              "created_at"),
    )


# =========================================================
# NOTIFICATION
# =========================================================

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)

    recipient_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    actor_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    type = Column(String(30), nullable=False)

    reference_id = Column(Integer)

    is_read = Column(
        Boolean,
        nullable=False,
        server_default="FALSE"
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )

    __table_args__ = (
        Index("ix_notifications_recipient",
              "recipient_id"),
        Index("ix_notifications_created_at",
              "created_at"),
    )
    recipient = relationship(
    "User",
    foreign_keys=[recipient_id])

    actor = relationship(
    "User",
    foreign_keys=[actor_id]
    )