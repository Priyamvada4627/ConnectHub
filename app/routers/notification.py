from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .. import oauth2, models, schemas
from ..database import get_db
from ..services import notification_service

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


# =========================================================
# GET ALL
# =========================================================

@router.get(
    "/",
    response_model=list[schemas.NotificationOut],
)
def get_notifications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        oauth2.get_current_user,
    ),
):
    return notification_service.get_notifications(
        current_user,
        db,
    )


# =========================================================
# UNREAD COUNT
# =========================================================

@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        oauth2.get_current_user,
    ),
):

    return {
        "count": notification_service.get_unread_count(
            current_user,
            db,
        )
    }


# =========================================================
# MARK READ
# =========================================================

@router.patch(
    "/{notification_id}/read",
    response_model=schemas.NotificationOut,
)
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        oauth2.get_current_user,
    ),
):

    return notification_service.mark_read(
        notification_id,
        current_user,
        db,
    )


# =========================================================
# MARK ALL READ
# =========================================================

@router.patch("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        oauth2.get_current_user,
    ),
):

    notification_service.mark_all_read(
        current_user,
        db,
    )

    return {
        "message": "All notifications marked as read"
    }


# =========================================================
# DELETE
# =========================================================

@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        oauth2.get_current_user,
    ),
):

    notification_service.delete_notification(
        notification_id,
        current_user,
        db,
    )