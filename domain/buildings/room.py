from typing import List, Tuple, Optional


class Room:
    def __init__(self, room_id: Optional[int], name: str, room_type: str, vertices: List[List[float]], floor_id: int):
        self.room_id = room_id
        self.name = name
        self.room_type = room_type
        self.vertices = vertices
        self.floor_id = floor_id
    
    def get_center(self) -> Tuple[float, float]:
        if not self.vertices:
            return (0.0, 0.0)
        x_coords = [v[0] for v in self.vertices]
        y_coords = [v[1] for v in self.vertices]
        center_x = sum(x_coords) / len(x_coords)
        center_y = sum(y_coords) / len(y_coords)
        return (center_x, center_y)
    
    def get_area(self) -> float:
        if len(self.vertices) < 3:
            return 0.0
        x = [v[0] for v in self.vertices]
        y = [v[1] for v in self.vertices]
        area = 0.5 * abs(sum(x[i] * y[i+1] - x[i+1] * y[i] 
                             for i in range(-1, len(self.vertices)-1)))
        return area

