import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from rooms import RoomManager


app = FastAPI()
room_manager = RoomManager()

import datetime
def log_event(msg):
    print(f"[{datetime.datetime.now().isoformat()}] {msg}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow frontend access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/check-room/{room_id}")
def check_room(room_id: str):
    exists = room_manager.room_exists(room_id)
    players = len(room_manager.get_players(room_id)) if exists else 0
    log_event(f"Check room: {room_id} exists={exists} players={players}")
    return {"exists": exists, "players": players}

@app.get("/")
def root():
    return {"message": "XO Multiplayer Backend Ready"}


@app.get("/create-room")
def create_room():
    room_id = room_manager.create_room()
    log_event(f"Created room: {room_id}")
    return {"room_id": room_id}


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    log_event(f"WebSocket connection attempt for room {room_id}")

    added = room_manager.add_player(room_id, websocket)
    log_event(f"Trying to add player to room {room_id}: {'Success' if added else 'Failed'}")

    if not added:
        log_event(f"WebSocket rejected for room {room_id}: Room full or invalid")
        await websocket.send_json({"type": "error", "message": "Room full or invalid."})
        return

    players = room_manager.get_players(room_id)
    log_event(f"Players in room {room_id}: {len(players)}")
    if len(players) == 2:
        for idx, player in enumerate(players):
            try:
                symbol = 'X' if idx == 0 else 'O'
                await player.send_json({"type": "start", "symbol": symbol})
                log_event(f"Player {idx} assigned symbol: {symbol} in room {room_id}")
            except Exception as e:
                log_event(f"Error assigning symbol to player {idx} in room {room_id}: {e}")

    try:
        while True:
            log_event(f"WAITING FOR CLIENT MESSAGE in room {room_id}...")
            data = await websocket.receive_json()
            log_event(f"RECEIVED FROM CLIENT in room {room_id}: {data}")
            if data.get("type") == "passMove":
                data["type"] = "move"
                for player in room_manager.get_players(room_id):
                    log_event(f"SENDING TO PLAYER in room {room_id}: {data}")
                    await player.send_json(data)
    except WebSocketDisconnect:
        log_event(f"Client disconnected from room {room_id}")
        room_manager.remove_player(room_id, websocket)

    # Close the WebSocket connection after use
    await websocket.close()
    log_event(f"WebSocket connection closed for room {room_id}")
