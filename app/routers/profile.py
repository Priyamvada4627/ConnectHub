from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from .. import models, schemas, oauth2
from ..database import get_db
from ..services import profile_service

router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)


# =========================================================
# MY PROFILE
# =========================================================

@router.get(
    "/me",
    response_model=schemas.UserProfile,
)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    return profile_service.build_profile(
        current_user,
        current_user,
        db,
    )


# =========================================================
# USER PROFILE
# =========================================================

@router.get(
    "/{username}",
    response_model=schemas.UserProfile,
)
def get_profile(
    username: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    user = profile_service.get_user_by_username(
        username,
        db,
    )

    return profile_service.build_profile(
        user,
        current_user,
        db,
    )


# =========================================================
# USER POSTS
# =========================================================

@router.get(
    "/{username}/posts",
    response_model=list[schemas.ProfilePostOut],
)
def get_user_posts(
    username: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    return profile_service.get_user_posts(
        username=username,
        current_user=current_user,
        db=db,
    )


# =========================================================
# USER FOLLOWERS
# =========================================================

@router.get(
    "/{username}/followers",
    response_model=list[schemas.UserSearchOut],
)
def get_followers(
    username: str,
    db: Session = Depends(get_db),
):
    return profile_service.get_followers(
        username,
        db,
    )


# =========================================================
# USER FOLLOWING
# =========================================================

@router.get(
    "/{username}/following",
    response_model=list[schemas.UserSearchOut],
)
def get_following(
    username: str,
    db: Session = Depends(get_db),
):
    return profile_service.get_following(
        username,
        db,
    )


@router.put(
    "/me",
    response_model=schemas.UserProfile,
)
def update_my_profile(

    full_name: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    avatar: Optional[UploadFile] = File(None),

    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        oauth2.get_current_user
    ),
):

    return profile_service.update_profile(
        current_user=current_user,
        full_name=full_name,
        bio=bio,
        avatar=avatar,
        db=db,
    )