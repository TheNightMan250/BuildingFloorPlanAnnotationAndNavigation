from typing import Tuple, Optional


class Stair:
    def __init__(self, stair_id: Optional[int], from_floor_id: int, to_floor_id: int, 
                 position: Tuple[float, float]):
        self.stair_id = stair_id
        self.from_floor_id = from_floor_id
        self.to_floor_id = to_floor_id
        self.position = position
    
    def connects_floors(self, floor_id_1: int, floor_id_2: int) -> bool:
        return (self.from_floor_id == floor_id_1 and self.to_floor_id == floor_id_2) or \
               (self.from_floor_id == floor_id_2 and self.to_floor_id == floor_id_1)
    
    def get_other_floor(self, floor_id: int) -> Optional[int]:
        if self.from_floor_id == floor_id:
            return self.to_floor_id
        elif self.to_floor_id == floor_id:
            return self.from_floor_id
        return None

