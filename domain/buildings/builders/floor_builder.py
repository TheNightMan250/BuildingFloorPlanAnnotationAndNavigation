from typing import Optional
from domain.buildings.floor import Floor


class FloorBuilder:
    def __init__(self):
        self.floor_id: Optional[int] = None
        self.name: str = ""
        self.image_path: str = ""
        self.building_id: Optional[int] = None
    
    def with_id(self, floor_id: int):
        self.floor_id = floor_id
        return self
    
    def with_name(self, name: str):
        self.name = name
        return self
    
    def with_image_path(self, image_path: str):
        self.image_path = image_path
        return self
    
    def with_building_id(self, building_id: int):
        self.building_id = building_id
        return self
    
    def build(self) -> Floor:
        return Floor(self.floor_id, self.name, self.image_path, self.building_id)

