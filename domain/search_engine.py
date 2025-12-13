from typing import List, Optional
from domain.buildings.room import Room
from domain.buildings.floor import Floor


class SearchEngine:
    def __init__(self):
        pass
    
    def search_rooms_by_name(self, floors: List[Floor], query: str) -> List[Room]:
        results = []
        query_lower = query.lower()
        for floor in floors:
            for room in floor.get_all_rooms():
                if query_lower in room.name.lower():
                    results.append(room)
        return results
    
    def search_rooms_by_type(self, floors: List[Floor], room_type: str) -> List[Room]:
        results = []
        for floor in floors:
            for room in floor.get_all_rooms():
                if room.room_type == room_type:
                    results.append(room)
        return results
    
    def search_floors_by_name(self, floors: List[Floor], query: str) -> List[Floor]:
        results = []
        query_lower = query.lower()
        for floor in floors:
            if query_lower in floor.name.lower():
                results.append(floor)
        return results
