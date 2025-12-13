from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from domain.buildings.room import Room
from domain.pathfinder.building_graph import BuildingGraph


class Pathfinder(ABC):
    @abstractmethod
    def find_path(self, start: Tuple[float, float], end: Tuple[float, float], 
                  rooms: List[Room]) -> Optional[List[Tuple[float, float]]]:
        pass
    
    @abstractmethod
    def find_multi_floor_path(self, start_room_id: int, end_room_id: int,
                              building_graph: BuildingGraph) -> Optional[List[Tuple[int, float, float]]]:
        pass
    
    @abstractmethod
    def get_algorithm_name(self) -> str:
        pass

