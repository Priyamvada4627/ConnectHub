from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, oauth2, schemas
from ..database import get_db
from ..services import notification_service

router = APIRouter(
    prefix="/follow",
    tags=["Follow"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def follow_user(
    follow: schemas.FollowCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):

    if follow.following_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow yourself",
        )

    user_followed = (
        db.query(models.User)
        .filter(models.User.id == follow.following_id)
        .first()
    )

    if not user_followed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    already_following = (
        db.query(models.Follow)
        .filter(
            models.Follow.follower_id == current_user.id,
            models.Follow.following_id == follow.following_id,
        )
        .first()
    )

    if already_following:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already following",
        )

    new_follow = models.Follow(
        follower_id=current_user.id,
        following_id=follow.following_id,
    )

    db.add(new_follow)
    db.commit()

    # Don't notify yourself
    if user_followed.id != current_user.id:
        notification_service.create_notification(
            recipient_id=user_followed.id,
            actor_id=current_user.id,
            notification_type="FOLLOW",
            db=db,
        )

    return {
        "message": "Followed successfully"
    }


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def unfollow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):

    follow_query = (
        db.query(models.Follow)
        .filter(
            models.Follow.follower_id == current_user.id,
            models.Follow.following_id == user_id,
        )
    )

    if not follow_query.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not following this user",
        )

    follow_query.delete(synchronize_session=False)
    db.commit()

    return {
        "message": "Unfollowed successfully"
    }


@router.get(
    "/followers/{user_id}",
    response_model=list[schemas.FollowOut],
)
def get_followers(
    user_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Follow)
        .filter(models.Follow.following_id == user_id)
        .all()
    )


@router.get(
    "/following/{user_id}",
    response_model=list[schemas.FollowOut],
)
def get_following(
    user_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Follow)
        .filter(models.Follow.follower_id == user_id)
        .all()
    )


@router.get("/counts/{user_id}")
def get_follow_counts(
    user_id: int,
    db: Session = Depends(get_db),
):
    followers = (
        db.query(models.Follow)
        .filter(models.Follow.following_id == user_id)
        .count()
    )

    following = (
        db.query(models.Follow)
        .filter(models.Follow.follower_id == user_id)
        .count()
    )

    return {
        "followers": followers,
        "following": following,
    }