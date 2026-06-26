from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
    UploadFile,
    File,
    Form,
    Query,
)
from sqlalchemy.orm import Session
from typing import Optional, List

from .. import schemas, models, oauth2
from ..database import get_db
from ..services import post_service

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


@router.get(
    "/",
    response_model=List[schemas.PostOut],
)
def get_posts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
    search: str = "",
):
    return post_service.get_posts(
        db=db,
        limit=limit,
        skip=skip,
        search=search,
    )


@router.get(
    "/{id}",
    response_model=schemas.PostOut,
)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    return post_service.get_post(
        id,
        db,
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.Post,
)
def create_post(
    title: str = Form(...),
    content: str = Form(...),
    published: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    return post_service.create_post(
        title,
        content,
        published,
        image,
        current_user,
        db,
    )


@router.put(
    "/{id}",
    response_model=schemas.Post,
)
def update_post(
    id: int,
    updated_post: schemas.PostUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    return post_service.update_post(
        id,
        updated_post,
        current_user,
        db,
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    post_service.delete_post(
        id,
        current_user,
        db,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )