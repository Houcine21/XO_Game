import uuid

class RoomManager:
    def __init__(self):
        self.active_rooms = {}  # room_id: [websocket1, websocket2]

    def create_room(self):
        room_id = str(uuid.uuid4())[:6]  # Short unique room code
        self.active_rooms[room_id] = []
        print(f"Room created: {room_id}")
        return room_id

    def room_exists(self, room_id: str) -> bool:
        return room_id in self.active_rooms

    def add_player(self, room_id, websocket):
        if room_id not in self.active_rooms:
            print(f"add_player: room {room_id} does not exist")
            return False
        if websocket in self.active_rooms[room_id]:
            print(f"add_player: websocket already in room {room_id}")
            return True
        if len(self.active_rooms[room_id]) >= 2:
            print(f"add_player: room {room_id} full ({len(self.active_rooms[room_id])} players)")
            return False
        self.active_rooms[room_id].append(websocket)
        print(f"add_player: websocket added to room {room_id}, total players now: {len(self.active_rooms[room_id])}")
        return True

    def remove_player(self, room_id, websocket):
        if room_id in self.active_rooms:
            if websocket in self.active_rooms[room_id]:
                self.active_rooms[room_id].remove(websocket)
                print(f"remove_player: websocket removed from room {room_id}, players left: {len(self.active_rooms[room_id])}")
            if not self.active_rooms[room_id]:
                print(f"remove_player: no players left in room {room_id}, deleting room")
                del self.active_rooms[room_id]

    def get_players(self, room_id):
        return self.active_rooms.get(room_id, [])
