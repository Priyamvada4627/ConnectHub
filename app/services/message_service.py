from fastapi import HTTPException, status,UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from .. import models, schemas
from . import notification_service

from ..cloudinary_helper import upload_image, upload_audio
# =========================================================
# CREATE MESSAGE (Shared by REST & WebSocket)
# =========================================================

def create_message(
    sender_id: int,
    receiver_id: int,
    content: str | None,
    image_url: str | None,
    audio_url: str | None,
    db: Session,
):

    receiver = (
        db.query(models.User)
        .filter(models.User.id == receiver_id)
        .first()
    )

    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receiver not found",
        )

    if sender_id == receiver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot message yourself",
        )

    if (
        not content
        and image_url is None
        and audio_url is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )

    new_message = models.Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content,
        image_url=image_url,
        audio_url=audio_url,
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    notification_service.create_notification(
        recipient_id=receiver_id,
        actor_id=sender_id,
        notification_type="MESSAGE",
        reference_id=new_message.id,
        db=db,
    )

    return new_message
# =========================================================
# MARK MESSAGE AS SEEN
# =========================================================

def mark_message_seen(
    message_id: int,
    current_user_id: int,
    db: Session,
):

    message = (
        db.query(models.Message)
        .filter(models.Message.id == message_id)
        .first()
    )

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )

    if message.receiver_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    if not message.is_seen:
        message.is_seen = True
        db.commit()
        db.refresh(message)

    return message
# =========================================================
# SEND MESSAGE
# =========================================================



def send_message(
    receiver_id: int,
    content: str | None,
    image: UploadFile | None,
    audio: UploadFile | None,
    current_user: models.User,
    db: Session,
):

    image_url = None
    audio_url = None

    # Upload image if provided
    if image and image.filename:
        image_url = upload_image(
            image.file,
            folder="resume_ready/messages",
        )

    # Upload audio if provided
    if audio and audio.filename:
        audio_url = upload_audio(
            audio.file,
            folder="resume_ready/audio",
        )

    return create_message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        content=content,
        image_url=image_url,
        audio_url=audio_url,
        db=db,
    )
# =========================================================
# MARK CONVERSATION AS SEEN
# =========================================================
def mark_conversation_seen(
    sender_id: int,
    receiver_id: int,
    db: Session,
):

    messages = (
        db.query(models.Message)
        .filter(
            models.Message.sender_id == sender_id,
            models.Message.receiver_id == receiver_id,
            models.Message.is_seen == False,
        )
        .all()
    )

    for message in messages:
        message.is_seen = True

    db.commit()

    return messages
# =========================================================
# GET CONVERSATION
# =========================================================

def get_conversation(
    user_id: int,
    current_user: models.User,
    db: Session,
    limit: int,
    skip: int,
):

    user = (
        db.query(models.User)
        .filter(models.User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Fetch newest messages first (skip/limit on most recent),
    # then reverse so the response is chronological (oldest → newest).
    messages = (
        db.query(models.Message)
        .filter(
            or_(
                and_(
                    models.Message.sender_id == current_user.id,
                    models.Message.receiver_id == user_id,
                ),
                and_(
                    models.Message.sender_id == user_id,
                    models.Message.receiver_id == current_user.id,
                ),
            )
        )
        .order_by(models.Message.created_at.desc())
        .limit(limit)
        .offset(skip)
        .all()
    )

    # Return in chronological order for the frontend
    return list(reversed(messages))
# =========================================================
# INBOX
# =========================================================

def get_inbox(
    current_user: models.User,
    db: Session,
):
    """
    Returns the latest message from every conversation.
    Uses a single query + one subquery for unread counts — no N+1.
    """
    uid = current_user.id

    # Subquery: unread count per sender (messages sent TO current user, unseen)
    unread_sq = (
        db.query(
            models.Message.sender_id.label("other_id"),
            func.count(models.Message.id).label("unread_count"),
        )
        .filter(
            models.Message.receiver_id == uid,
            models.Message.is_seen == False,
        )
        .group_by(models.Message.sender_id)
        .subquery()
    )

    # All messages involving the current user, newest first
    messages = (
        db.query(models.Message)
        .filter(
            or_(
                models.Message.sender_id == uid,
                models.Message.receiver_id == uid,
            )
        )
        .order_by(desc(models.Message.created_at))
        .all()
    )

    # Build inbox in Python — one pass, no extra queries
    visited: dict[int, dict] = {}

    for message in messages:
        other_id = (
            message.receiver_id if message.sender_id == uid else message.sender_id
        )
        if other_id in visited:
            continue
        visited[other_id] = message

    if not visited:
        return []

    # Fetch all other users in one query
    other_users = (
        db.query(models.User)
        .filter(models.User.id.in_(visited.keys()))
        .all()
    )
    user_map = {u.id: u for u in other_users}

    # Fetch unread counts in one query
    unread_rows = (
        db.query(unread_sq.c.other_id, unread_sq.c.unread_count)
        .all()
    )
    unread_map = {row.other_id: row.unread_count for row in unread_rows}

    # Assemble inbox — preserve order (newest conversation first)
    inbox = []
    for other_id, message in visited.items():
        other_user = user_map.get(other_id)
        if not other_user:
            continue

        if message.audio_url:
            last_message_text = None
            last_message_type = "audio"
        elif message.image_url:
            last_message_text = None
            last_message_type = "image"
        else:
            last_message_text = message.content
            last_message_type = "text"

        inbox.append(
            {
                "user": other_user,
                "last_message": last_message_text,
                "last_message_type": last_message_type,
                "last_message_time": message.created_at,
                "unread_count": unread_map.get(other_id, 0),
            }
        )

    return inbox