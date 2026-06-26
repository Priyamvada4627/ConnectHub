from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from fastapi import UploadFile
from ..cloudinary_helper import upload_image

# =========================================================
# COMMON HELPERS
# =========================================================

def get_user_by_username(
    username: str,
    db: Session,
) -> models.User:
    """
    Returns a user by username.
    Raises 404 if user does not exist.
    """

    user = (
        db.query(models.User)
        .filter(models.User.username == username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


# =========================================================
# PROFILE
# =========================================================

def build_profile(
    user: models.User,
    current_user: models.User,
    db: Session,
) -> schemas.UserProfile:

    followers = (
        db.query(models.Follow)
        .filter(
            models.Follow.following_id == user.id
        )
        .count()
    )

    following = (
        db.query(models.Follow)
        .filter(
            models.Follow.follower_id == user.id
        )
        .count()
    )

    posts_count = (
        db.query(models.Post)
        .filter(
            models.Post.owner_id == user.id
        )
        .count()
    )

    if current_user.id == user.id:
        is_following = False
    else:
        is_following = (
            db.query(models.Follow)
            .filter(
                models.Follow.follower_id == current_user.id,
                models.Follow.following_id == user.id,
            )
            .first()
            is not None
        )

    return schemas.UserProfile(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        bio=user.bio,
        avatar_url=user.avatar_url,
        followers=followers,
        following=following,
        posts_count=posts_count,
        is_following=is_following,
        created_at=user.created_at,
    )


# =========================================================
# POSTS
# =========================================================

def get_user_posts(
    username: str,
    current_user: models.User,
    db: Session,
):

    user = get_user_by_username(
        username,
        db,
    )

    posts = (
        db.query(models.Post)
        .filter(
            models.Post.owner_id == user.id
        )
        .order_by(
            models.Post.created_at.desc()
        )
        .all()
    )

    result = []

    for post in posts:

        likes = (
            db.query(models.Vote)
            .filter(
                models.Vote.post_id == post.id
            )
            .count()
        )

        comments = (
            db.query(models.Comment)
            .filter(
                models.Comment.post_id == post.id
            )
            .count()
        )

        is_liked = (
            db.query(models.Vote)
            .filter(
                models.Vote.post_id == post.id,
                models.Vote.user_id == current_user.id,
            )
            .first()
            is not None
        )

        result.append({

            "post": post,

            "likes": likes,

            "comments": comments,

            "is_liked": is_liked,

            "is_owner": post.owner_id == current_user.id,

        })

    return result
# =========================================================
# FOLLOWERS
# =========================================================

def get_followers(
    username: str,
    db: Session,
):

    user = get_user_by_username(
        username,
        db,
    )

    followers = (
        db.query(models.User)
        .join(
            models.Follow,
            models.Follow.follower_id == models.User.id,
        )
        .filter(
            models.Follow.following_id == user.id
        )
        .all()
    )

    return followers


# =========================================================
# FOLLOWING
# =========================================================

def get_following(
    username: str,
    db: Session,
):

    user = get_user_by_username(
        username,
        db,
    )

    following = (
        db.query(models.User)
        .join(
            models.Follow,
            models.Follow.following_id == models.User.id,
        )
        .filter(
            models.Follow.follower_id == user.id
        )
        .all()
    )

    return following


def update_profile(

    current_user: models.User,

    full_name: str | None,

    bio: str | None,

    avatar: UploadFile | None,

    db: Session,

):

    if full_name is not None:
        current_user.full_name = full_name

    if bio is not None:
        current_user.bio = bio

    if avatar and avatar.filename:

        avatar_url = upload_image(
            avatar.file,
            folder="resume_ready/avatars",
        )

        current_user.avatar_url = avatar_url

    db.commit()

    db.refresh(current_user)

    return build_profile(
        current_user,
        current_user,
        db,
    )