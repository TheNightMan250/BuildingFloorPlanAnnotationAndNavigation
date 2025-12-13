from typing import List, Optional, Tuple


class Pathway:
    def __init__(self, pathway_id: Optional[int], floor_id: int, points: List[Tuple[float, float]]):
        self.pathway_id = pathway_id
        self.floor_id = floor_id
        self.points = points
