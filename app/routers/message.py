from fastapi import APIRouter, Depends, Query, status,UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Annotated
from .. import schemas, models, oauth2
from ..database import get_db
from ..services import message_service
from ..websocket.manager import manager
router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
)


# =========================================================
# SEND MESSAGE
# =========================================================
@router.post(
    "/",
    response_model=schemas.MessageOut,
    status_code=status.HTTP_201_CREATED,
)
def send_message(
    receiver_id: int = Form(...),
    content: str | None = Form(None),

    image: Annotated[UploadFile | None, File()] = None,
    audio: Annotated[UploadFile | None, File()] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):

    return message_service.send_message(
        receiver_id=receiver_id,
        content=content,
        image=image,
        audio=audio,
        current_user=current_user,
        db=db,
    )
# =========================================================
# GET CONVERSATION
# =========================================================
@router.get(
    "/{user_id}",
    response_model=list[schemas.MessageOut],
)
async def get_conversation(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
):

    # Mark messages as seen
    seen_messages = message_service.mark_conversation_seen(
        sender_id=user_id,
        receiver_id=current_user.id,
        db=db,
    )

    # Notify sender
    for message in seen_messages:

        await manager.send_personal_message(
            message.sender_id,
            {
                "type": "seen",
                "message_id": message.id,
            },
        )

    # Fetch conversation
    messages = message_service.get_conversation(
        user_id=user_id,
        current_user=current_user,
        db=db,
        limit=limit,
        skip=skip,
    )

    return messages

# =========================================================
# GET INBOX
# =========================================================

@router.get(
    "/",
    response_model=list[schemas.InboxConversation],
)
def get_inbox(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):

    return message_service.get_inbox(
        current_user=current_user,
        db=db,
    )