import asyncio

from fastapi import WebSocket


class ConnectionHub:

    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}
        self._lock = asyncio.Lock()

    # -----------------------------------------------------
    # Connect
    # -----------------------------------------------------

    async def connect(
        self,
        user_id: int,
        websocket: WebSocket,
    ):
        await websocket.accept()

        async with self._lock:

            old = self.active_connections.get(user_id)

            if old:
                try:
                    await old.close()
                except Exception:
                    pass

            self.active_connections[user_id] = websocket

    # -----------------------------------------------------
    # Disconnect
    # -----------------------------------------------------

    async def disconnect(
        self,
        user_id: int,
    ):
        async with self._lock:
            self.active_connections.pop(user_id, None)

    # -----------------------------------------------------
    # Send to one user
    # -----------------------------------------------------

    async def send_personal_message(
        self,
        receiver_id: int,
        data: dict,
    ):
        async with self._lock:
            websocket = self.active_connections.get(receiver_id)

        if websocket:

            try:
                await websocket.send_json(data)

            except Exception:
                await self.disconnect(receiver_id)

    # -----------------------------------------------------
    # Broadcast to everyone
    # -----------------------------------------------------

    async def broadcast(
        self,
        data: dict,
    ):

        disconnected = []

        for user_id, websocket in self.active_connections.items():

            try:
                await websocket.send_json(data)

            except Exception:
                disconnected.append(user_id)

        for user_id in disconnected:
            await self.disconnect(user_id)

    # -----------------------------------------------------
    # Broadcast Presence
    # -----------------------------------------------------

    async def broadcast_online_status(
        self,
        user_id: int,
        online: bool,
    ):

        disconnected = []

        for uid, websocket in self.active_connections.items():

            if uid == user_id:
                continue

            try:

                await websocket.send_json(
                    {
                        "type": "presence",
                        "user_id": user_id,
                        "online": online,
                    }
                )

            except Exception:

                disconnected.append(uid)

        for uid in disconnected:
            await self.disconnect(uid)

    # -----------------------------------------------------
    # Online Status
    # -----------------------------------------------------

    def is_online(
        self,
        user_id: int,
    ) -> bool:

        return user_id in self.active_connections

    @property
    def online_users(self):

        return list(self.active_connections.keys())
    
manager= ConnectionHub()