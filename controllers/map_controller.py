from typing import Optional, List, Tuple
from domain.buildings.floor import Floor
from domain.buildings.room import Room
from domain.pathfinder.pathfinder import Pathfinder
from domain.maps.workflows.map_workflow_base import MapApprovalWorkflow
from data.repositories.map_repo import IMapRepository
from data.repositories.room_repo import IRoomRepository


class MapController:
    def __init__(self, map_repo: IMapRepository, room_repo: IRoomRepository,
                 pathfinder: Pathfinder, workflow: MapApprovalWorkflow):
        self.map_repo = map_repo
        self.room_repo = room_repo
        self.pathfinder = pathfinder
        self.workflow = workflow
    
    def set_pathfinder(self, pathfinder: Pathfinder):
        self.pathfinder = pathfinder
    
    def load_map(self, floor_id: int) -> Optional[Floor]:
        return self.map_repo.find_by_id(floor_id)
    
    def get_path(self, start: Tuple[float, float], end: Tuple[float, float], 
                 floor_id: int) -> Optional[List[Tuple[float, float]]]:
        floor = self.map_repo.find_by_id(floor_id)
        if not floor:
            return None
        rooms = self.room_repo.find_by_floor_id(floor_id)
        return self.pathfinder.find_path(start, end, rooms)
    
    def submit_map(self, floor: Floor) -> bool:
        saved_floor = self.map_repo.save(floor)
        for room in floor.rooms:
            self.room_repo.save(room)
        return saved_floor is not None
    
    def approve_map(self, floor_id: int) -> bool:
        floor = self.map_repo.find_by_id(floor_id)
        if not floor:
            return False
        return self.workflow.approve(floor)
    
    def get_all_maps(self) -> List[Floor]:
        return self.map_repo.find_all()
    
    def create_room(self, floor_id: int, name: str, room_type: str, 
                   vertices: List[List[float]]) -> Room:
        from domain.buildings.builders.room_builder import RoomBuilder
        room = (RoomBuilder()
                .with_floor_id(floor_id)
                .with_name(name)
                .with_type(room_type)
                .with_vertices(vertices)
                .build())
        saved_room = self.room_repo.save(room)
        floor = self.map_repo.find_by_id(floor_id)
        if floor:
            floor.add_room(saved_room)
        return saved_room
    
    def delete_room(self, room_id: int) -> bool:
        return self.room_repo.delete(room_id)

