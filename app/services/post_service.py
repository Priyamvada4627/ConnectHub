from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from .. import models, schemas
from ..cloudinary_helper import upload_image


def get_posts(
    db: Session,
    limit: int,
    skip: int,
    search: str,
):
    return (
        db.query(
            models.Post,
            func.count(models.Vote.post_id).label("votes"),
        )
        .join(
            models.Vote,
            models.Vote.post_id == models.Post.id,
            isouter=True,
        )
        .group_by(models.Post.id)
        .filter(models.Post.title.icontains(search))
        .order_by(models.Post.created_at.desc())
        .limit(limit)
        .offset(skip)
        .all()
    )


def get_post(
    post_id: int,
    db: Session,
):
    post = (
        db.query(
            models.Post,
            func.count(models.Vote.post_id).label("votes"),
        )
        .join(
            models.Vote,
            models.Vote.post_id == models.Post.id,
            isouter=True,
        )
        .group_by(models.Post.id)
        .filter(models.Post.id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post {post_id} not found",
        )

    return post


def create_post(
    title: str,
    content: str,
    published: bool,
    image: Optional[UploadFile],
    current_user: models.User,
    db: Session,
):
    image_url = None

    if image:
        image_url = upload_image(image.file)

    new_post = models.Post(
        title=title,
        content=content,
        published=published,
        owner_id=current_user.id,
        image_url=image_url,
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


def update_post(
    post_id: int,
    updated_post: schemas.PostUpdate,
    current_user: models.User,
    db: Session,
):
    post_query = (
        db.query(models.Post)
        .filter(models.Post.id == post_id)
    )

    post = post_query.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post {post_id} not found",
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    post_query.update(
        updated_post.model_dump(exclude_none=True),
        synchronize_session=False,
    )

    db.commit()

    return post_query.first()


def delete_post(
    post_id: int,
    current_user: models.User,
    db: Session,
):
    post_query = (
        db.query(models.Post)
        .filter(models.Post.id == post_id)
    )

    post = post_query.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post {post_id} not found",
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    post_query.delete(synchronize_session=False)

    db.commit()