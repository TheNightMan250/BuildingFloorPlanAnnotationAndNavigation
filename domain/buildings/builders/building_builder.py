from typing import Optional
from domain.buildings.building import Building


class BuildingBuilder:
    def __init__(self):
        self.building_id: Optional[int] = None
        self.name: str = ""
    
    def with_id(self, building_id: int):
        self.building_id = building_id
        return self
    
    def with_name(self, name: str):
        self.name = name
        return self
    
    def build(self) -> Building:
        return Building(self.building_id, self.name)

