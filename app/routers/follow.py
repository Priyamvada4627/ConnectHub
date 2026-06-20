from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, oauth2, schemas
from ..database import get_db

router = APIRouter(
    prefix="/follow",
    tags=["Follow"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def follow_user(
    follow: schemas.FollowCreate,
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):

    if follow.following_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot follow yourself"
        )

    user = db.query(models.User).filter(
        models.User.id == follow.following_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    existing_follow = db.query(models.Follow).filter(
        models.Follow.follower_id == current_user.id,
        models.Follow.following_id == follow.following_id
    ).first()

    if existing_follow:
        raise HTTPException(
            status_code=409,
            detail="Already following this user"
        )

    new_follow = models.Follow(
        follower_id=current_user.id,
        following_id=follow.following_id
    )

    db.add(new_follow)
    db.commit()

    return {"message": "Followed successfully"}

@router.delete("/{user_id}")
def unfollow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):

    follow_query = db.query(models.Follow).filter(
        models.Follow.follower_id == current_user.id,
        models.Follow.following_id == user_id
    )

    follow = follow_query.first()

    if not follow:
        raise HTTPException(
            status_code=404,
            detail="Follow relationship not found"
        )

    follow_query.delete(
        synchronize_session=False
    )

    db.commit()

    return {"message": "Unfollowed successfully"}

@router.get("/followers/{user_id}")
def get_followers(
    user_id: int,
    db: Session = Depends(get_db)
):

    followers = db.query(models.Follow).filter(
        models.Follow.following_id == user_id
    ).all()

    return followers

@router.get("/following/{user_id}")
def get_following(
    user_id: int,
    db: Session = Depends(get_db)
):

    following = db.query(models.Follow).filter(
        models.Follow.follower_id == user_id
    ).all()

    return following