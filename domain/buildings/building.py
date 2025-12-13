from typing import List, Optional
from domain.buildings.floor import Floor


class Building:
    def __init__(self, building_id: Optional[int], name: str):
        self.building_id = building_id
        self.name = name
        self.floors: List[Floor] = []
    
    def add_floor(self, floor: Floor):
        floor.building_id = self.building_id
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

