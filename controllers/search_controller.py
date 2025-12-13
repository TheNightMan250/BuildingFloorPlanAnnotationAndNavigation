from typing import List
from domain.search_engine import SearchEngine
from domain.buildings.room import Room
from domain.buildings.floor import Floor
from data.repositories.map_repo import IMapRepository


class SearchController:
    def __init__(self, search_engine: SearchEngine, map_repo: IMapRepository):
        self.search_engine = search_engine
        self.map_repo = map_repo
    
    def search_rooms(self, query: str) -> List[Room]:
        all_floors = self.map_repo.find_all()
        return self.search_engine.search_rooms_by_name(all_floors, query)
    
    def search_rooms_by_type(self, room_type: str) -> List[Room]:
        all_floors = self.map_repo.find_all()
        return self.search_engine.search_rooms_by_type(all_floors, room_type)
    
    def search_floors(self, query: str) -> List[Floor]:
        all_floors = self.map_repo.find_all()
        return self.search_engine.search_floors_by_name(all_floors, query)
