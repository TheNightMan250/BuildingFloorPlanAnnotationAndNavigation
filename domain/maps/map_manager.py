from abc import ABC, abstractmethod
from typing import List, Optional
from domain.buildings.floor import Floor
from domain.buildings.room import Room


class MapManager(ABC):
    def __init__(self):
        self.floors: List[Floor] = []
    
    def add_floor(self, floor: Floor):
        self.floors.append(floor)
    
    def remove_floor(self, floor: Floor):
        if floor in self.floors:
            self.floors.remove(floor)
    
    def get_floor(self, floor_id: int) -> Optional[Floor]:
        for floor in self.floors:
            if floor.floor_id == floor_id:
                return floor
        return None
    
    def get_all_floors(self) -> List[Floor]:
        return self.floors.copy()
    
    @abstractmethod
    def validate_floor(self, floor: Floor) -> bool:
        pass
    
    @abstractmethod
    def process_floor(self, floor: Floor) -> bool:
        pass
    
    def approve_floor(self, floor: Floor) -> bool:
        if not self.validate_floor(floor):
            return False
        return self.process_floor(floor)

