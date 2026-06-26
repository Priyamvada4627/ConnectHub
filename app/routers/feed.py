from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, oauth2
from ..database import get_db
from ..services import feed_service

router = APIRouter(
    prefix="/feed",
    tags=["Feed"],
)


# =========================================================
# HOME FEED
# =========================================================

@router.get(
    "/",
    response_model=List[schemas.FeedOut],
)
def get_feed(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        oauth2.get_current_user
    ),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
):
    return feed_service.get_feed(
        current_user=current_user,
        db=db,
        limit=limit,
        skip=skip,
    )