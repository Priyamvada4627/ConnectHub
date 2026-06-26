from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas


# =========================================================
# CREATE NOTIFICATION
# =========================================================

def create_notification(
    recipient_id: int,
    actor_id: int,
    notification_type: str,
    db: Session,
    reference_id: int | None = None,
):
    # Don't notify yourself
    if recipient_id == actor_id:
        return

    notification = models.Notification(
        recipient_id=recipient_id,
        actor_id=actor_id,
        type=notification_type,
        reference_id=reference_id,
    )

    db.add(notification)
    db.commit()


# =========================================================
# GET NOTIFICATIONS
# =========================================================

def get_notifications(
    current_user: models.User,
    db: Session,
):

    notifications = (
        db.query(models.Notification)
        .filter(
            models.Notification.recipient_id == current_user.id
        )
        .order_by(
            models.Notification.created_at.desc()
        )
        .all()
    )

    result = []

    for notification in notifications:

        result.append(
            schemas.NotificationOut(
                id=notification.id,
                actor=notification.actor,
                type=notification.type,
                reference_id=notification.reference_id,
                is_read=notification.is_read,
                created_at=notification.created_at,
            )
        )

    return result


# =========================================================
# UNREAD COUNT
# =========================================================

def get_unread_count(
    current_user: models.User,
    db: Session,
):

    return (
        db.query(models.Notification)
        .filter(
            models.Notification.recipient_id == current_user.id,
            models.Notification.is_read == False,
        )
        .count()
    )


# =========================================================
# MARK ONE READ
# =========================================================

def mark_read(
    notification_id: int,
    current_user: models.User,
    db: Session,
):

    notification = (
        db.query(models.Notification)
        .filter(
            models.Notification.id == notification_id,
            models.Notification.recipient_id == current_user.id,
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    notification.is_read = True

    db.commit()
    db.refresh(notification)

    return schemas.NotificationOut(
        id=notification.id,
        actor=notification.actor,
        type=notification.type,
        reference_id=notification.reference_id,
        is_read=notification.is_read,
        created_at=notification.created_at,
    )


# =========================================================
# MARK ALL READ
# =========================================================
def mark_all_read(
    current_user: models.User,
    db: Session,
):

    notifications = (
        db.query(models.Notification)
        .filter(
            models.Notification.recipient_id == current_user.id,
            models.Notification.is_read == False,
        )
        .all()
    )

    print("Unread:", len(notifications))

    for notification in notifications:
        notification.is_read = True

    db.commit()

    print("Done")
# =========================================================
# DELETE NOTIFICATION
# =========================================================

def delete_notification(
    notification_id: int,
    current_user: models.User,
    db: Session,
):

    notification = (
        db.query(models.Notification)
        .filter(
            models.Notification.id == notification_id,
            models.Notification.recipient_id == current_user.id,
        )
    )

    if not notification.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    notification.delete(
        synchronize_session=False,
    )

    db.commit()