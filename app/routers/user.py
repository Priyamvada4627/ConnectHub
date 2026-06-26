from .. import models, schemas, utils, oauth2
from fastapi import (
    status,
    HTTPException,
    Depends,
    APIRouter,
    File,
    UploadFile,
)
from sqlalchemy.orm import Session
from ..database import get_db
from ..cloudinary_helper import upload_image

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# =========================================================
# CREATE USER
# =========================================================

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserOut,
)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
):

    existing_email = (
        db.query(models.User)
        .filter(models.User.email == user.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    existing_username = (
        db.query(models.User)
        .filter(models.User.username == user.username)
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    hashed_password = utils.hash(user.password)

    new_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        full_name=user.full_name,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# =========================================================
# CURRENT USER
# =========================================================

@router.get(
    "/me",
    response_model=schemas.UserOut,
)
def get_me(
    current_user: models.User = Depends(
        oauth2.get_current_user
    ),
):
    return current_user


# =========================================================
# UPDATE PROFILE
# =========================================================

@router.put(
    "/me",
    response_model=schemas.UserOut,
)
def update_me(
    updates: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        oauth2.get_current_user
    ),
):

    if updates.username:

        existing = (
            db.query(models.User)
            .filter(
                models.User.username == updates.username,
                models.User.id != current_user.id,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Username already taken",
            )

    user_query = (
        db.query(models.User)
        .filter(models.User.id == current_user.id)
    )

    user_query.update(
        updates.model_dump(exclude_none=True),
        synchronize_session=False,
    )

    db.commit()

    return user_query.first()


# =========================================================
# UPLOAD AVATAR
# =========================================================

@router.post(
    "/me/avatar",
    response_model=schemas.UserOut,
)
def upload_avatar(
    avatar: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        oauth2.get_current_user
    ),
):

    avatar_url = upload_image(avatar.file)

    (
        db.query(models.User)
        .filter(models.User.id == current_user.id)
        .update(
            {"avatar_url": avatar_url},
            synchronize_session=False,
        )
    )

    db.commit()

    db.refresh(current_user)

    return current_user


# =========================================================
# SEARCH USERS
# =========================================================

@router.get(
    "/search/",
    response_model=list[schemas.UserSearchOut],
)
def search_users(
    q: str,
    db: Session = Depends(get_db),
):

    users = (
        db.query(models.User)
        .filter(
            models.User.username.ilike(f"%{q}%")
        )
        .limit(20)
        .all()
    )

    return users


# =========================================================
# GET USER BY USERNAME
# =========================================================

@router.get(
    "/username/{username}",
    response_model=schemas.UserOut,
)
def get_user_by_username(
    username: str,
    db: Session = Depends(get_db),
):

    user = (
        db.query(models.User)
        .filter(
            models.User.username == username
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


# =========================================================
# GET USER BY ID
# =========================================================

@router.get(
    "/{id}",
    response_model=schemas.UserOut,
)
def get_user(
    id: int,
    db: Session = Depends(get_db),
):

    user = (
        db.query(models.User)
        .filter(models.User.id == id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User {id} not found",
        )

    return user