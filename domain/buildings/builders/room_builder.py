from typing import List, Optional
from domain.buildings.room import Room


class RoomBuilder:
    def __init__(self):
        self.room_id: Optional[int] = None
        self.name: str = "Room"
        self.room_type: str = "Room"
        self.vertices: List[List[float]] = []
        self.floor_id: int = 0
    
    def with_id(self, room_id: int):
        self.room_id = room_id
        return self
    
    def with_name(self, name: str):
        self.name = name
        return self
    
    def with_type(self, room_type: str):
        self.room_type = room_type
        return self
    
    def with_vertices(self, vertices: List[List[float]]):
        self.vertices = vertices
        return self
    
    def with_floor_id(self, floor_id: int):
        self.floor_id = floor_id
        return self
    
    def build(self) -> Room:
        return Room(self.room_id, self.name, self.room_type, self.vertices, self.floor_id)

