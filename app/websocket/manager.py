from fastapi import WebSocket
class ConnectionManager:

    def __init__(self):
        self.active_connections = {}
    
    async def connect(self,user_id: int,websocket: WebSocket):
        await websocket.accept()

        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: int):
        self.active_connections.pop(
        user_id,
        None
    )
        
    async def send_personal_message(self,receiver_id: int,data: dict):
        receiver_ws = self.active_connections.get(receiver_id)

        if receiver_ws:
            await receiver_ws.send_json(data)
    @property
    def online_users(self):
        return list(self.active_connections.keys())

manager = ConnectionManager()

