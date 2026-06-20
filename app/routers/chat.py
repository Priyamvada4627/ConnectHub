from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..websocket.manager import manager
from ..database import SessionLocal
from .. import models
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
router = APIRouter(
    tags=["Chat"]
)

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int
):
    await manager.connect(
        user_id,
        websocket
    )

    db = SessionLocal()

    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            receiver_id = data["receiver_id"]
            if message_type == "typing":
                await manager.send_personal_message(receiver_id,{"type": "typing",
                 "user_id": user_id})
                continue

            new_message = models.Message(
                sender_id=user_id,
                receiver_id=receiver_id,
                content=data["content"]
            )

            db.add(new_message)
            db.commit()
            db.refresh(new_message)

            await manager.send_personal_message(
                receiver_id,
                {
                    "id": new_message.id,
                    "sender_id": user_id,
                    "receiver_id": receiver_id,
                    "content": data["content"],
                    "created_at": str(new_message.created_at)
                }
            )

    except WebSocketDisconnect:
        manager.disconnect(user_id)

    finally:
        db.close()


@router.get("/online-users")
def get_online_users():
    return {
        "online_users": manager.online_users
    }