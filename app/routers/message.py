from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/messages",
    tags=["Messages"]
)

@router.post(
    "/",
    response_model=schemas.MessageOut,
    status_code=status.HTTP_201_CREATED
)
def send_message(
    message: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):

    receiver = db.query(models.User).filter(
        models.User.id == message.receiver_id
    ).first()

    if not receiver:
        raise HTTPException(
            status_code=404,
            detail="Receiver not found"
        )

    new_message = models.Message(
    sender_id=current_user.id,
    receiver_id=message.receiver_id,
    content=message.content,
    image_url=message.image_url
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message

@router.get(
    "/{user_id}",
    response_model=list[schemas.MessageOut]
)
def get_conversation(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    db.query(models.Message).filter(
    models.Message.sender_id == user_id,
    models.Message.receiver_id == current_user.id,
    models.Message.is_seen == False).update({"is_seen": True},synchronize_session=False)

    db.commit()

    messages = db.query(models.Message).filter(
        or_(
            and_(
                models.Message.sender_id == current_user.id,
                models.Message.receiver_id == user_id
            ),
            and_(
                models.Message.sender_id == user_id,
                models.Message.receiver_id == current_user.id
            )
        )
    ).order_by(
        models.Message.created_at
    ).all()

    return messages
