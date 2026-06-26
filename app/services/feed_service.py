from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from .. import models, schemas


def get_feed(
    current_user: models.User,
    db: Session,
    limit: int,
    skip: int,
):
    # Users that the current user follows
    following_users = (
        db.query(models.Follow.following_id)
        .filter(models.Follow.follower_id == current_user.id)
        .subquery()
    )

    # Posts from followed users + own posts
    posts = (
        db.query(
            models.Post,
            func.count(models.Vote.post_id).label("likes"),
        )
        .outerjoin(
            models.Vote,
            models.Vote.post_id == models.Post.id,
        )
        .filter(
            or_(
                models.Post.owner_id.in_(following_users),
                models.Post.owner_id == current_user.id,
            )
        )
        .group_by(models.Post.id)
        .order_by(models.Post.created_at.desc())
        .limit(limit)
        .offset(skip)
        .all()
    )

    feed = []

    for post, likes in posts:

        # Count comments
        comment_count = (
            db.query(models.Comment)
            .filter(models.Comment.post_id == post.id)
            .count()
        )

        # Has current user liked this post?
        is_liked = (
            db.query(models.Vote)
            .filter(
                models.Vote.post_id == post.id,
                models.Vote.user_id == current_user.id,
            )
            .first()
            is not None
        )

        feed.append(
            schemas.FeedOut(
                post=post,
                likes=likes,
                comments=comment_count,
                is_liked=is_liked,
                is_owner=(post.owner_id == current_user.id),
            )
        )

    return feed