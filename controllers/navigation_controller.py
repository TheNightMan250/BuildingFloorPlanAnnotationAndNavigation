from typing import Optional, List, Tuple, Dict
from domain.buildings.room import Room
from domain.pathfinder.pathfinder import Pathfinder
from domain.pathfinder.building_graph import BuildingGraph
from data.repositories.map_repo import IMapRepository
from data.repositories.room_repo import IRoomRepository
from data.repositories.stair_repo import IStairRepository
from data.repositories.pathway_repo import IPathwayRepository


class NavigationController:
    def __init__(self, map_repo: IMapRepository, room_repo: IRoomRepository,
                 stair_repo: IStairRepository, pathfinder: Pathfinder,
                 pathway_repo: Optional[IPathwayRepository] = None):
        self.map_repo = map_repo
        self.room_repo = room_repo
        self.stair_repo = stair_repo
        self.pathfinder = pathfinder
        self.pathway_repo = pathway_repo
        self.start_room_id: Optional[int] = None
        self.end_room_id: Optional[int] = None
    
    def set_start_room(self, room_id: int) -> bool:
        room = self.room_repo.find_by_id(room_id)
        if room:
            self.start_room_id = room_id
            return True
        return False
    
    def set_end_room(self, room_id: int) -> bool:
        room = self.room_repo.find_by_id(room_id)
        if room:
            self.end_room_id = room_id
            return True
        return False
    
    def get_start_room(self) -> Optional[Room]:
        if self.start_room_id:
            return self.room_repo.find_by_id(self.start_room_id)
        return None
    
    def get_end_room(self) -> Optional[Room]:
        if self.end_room_id:
            return self.room_repo.find_by_id(self.end_room_id)
        return None
    
    def clear_selection(self):
        self.start_room_id = None
        self.end_room_id = None
    
    def get_navigation_path(self) -> Optional[List[Tuple[int, float, float]]]:
        if not self.start_room_id or not self.end_room_id:
            return None
        
        start_room = self.room_repo.find_by_id(self.start_room_id)
        end_room = self.room_repo.find_by_id(self.end_room_id)
        
        if not start_room or not end_room:
            return None
        
        all_floors = self.map_repo.find_all()
        all_stairs = []
        for floor in all_floors:
            if floor.floor_id:
                floor_rooms = self.room_repo.find_by_floor_id(floor.floor_id)
                for room in floor_rooms:
                    floor.add_room(room)

                floor_stairs = self.stair_repo.find_by_floor(floor.floor_id)
                all_stairs.extend(floor_stairs)
                for stair in floor_stairs:
                    floor.add_stair(stair)

        all_pathways = []
        if self.pathway_repo is not None:
            all_pathways = self.pathway_repo.find_all()

        building_graph = BuildingGraph(all_floors, all_stairs, pathways=all_pathways)
        
        path = self.pathfinder.find_multi_floor_path(
            self.start_room_id,
            self.end_room_id,
            building_graph
        )
        
        return path
    
    def get_path_by_floor(self) -> Dict[int, List[Tuple[float, float]]]:
        path = self.get_navigation_path()
        if not path:
            return {}
        
        by_floor: Dict[int, List[Tuple[float, float]]] = {}
        for node in path:
            floor_id, x, y = node
            if floor_id not in by_floor:
                by_floor[floor_id] = []
            by_floor[floor_id].append((x, y))
        
        return by_floor

