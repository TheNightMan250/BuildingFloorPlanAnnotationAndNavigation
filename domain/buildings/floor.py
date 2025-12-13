from typing import List, Optional
from domain.buildings.room import Room
from domain.buildings.stair import Stair


class Floor:
    def __init__(self, floor_id: Optional[int], name: str, image_path: str, building_id: Optional[int] = None):
        self.floor_id = floor_id
        self.name = name
        self.image_path = image_path
        self.building_id = building_id
        self.rooms: List[Room] = []
        self.stairs: List[Stair] = []
    
    def add_room(self, room: Room):
        room.floor_id = self.floor_id
        self.rooms.append(room)
    
    def remove_room(self, room: Room):
        if room in self.rooms:
            self.rooms.remove(room)
    
    def get_room(self, room_id: int) -> Optional[Room]:
        for room in self.rooms:
            if room.room_id == room_id:
                return room
        return None
    
    def get_all_rooms(self) -> List[Room]:
        return self.rooms.copy()
    
    def add_stair(self, stair: Stair):
        if stair.from_floor_id == self.floor_id or stair.to_floor_id == self.floor_id:
            self.stairs.append(stair)
    
    def get_connected_floors(self) -> List[int]:
        connected = []
        for stair in self.stairs:
            other_floor = stair.get_other_floor(self.floor_id)
            if other_floor and other_floor not in connected:
                connected.append(other_floor)
        return connected
    
    def get_stairs_to_floor(self, target_floor_id: int) -> List[Stair]:
        return [stair for stair in self.stairs if stair.connects_floors(self.floor_id, target_floor_id)]

