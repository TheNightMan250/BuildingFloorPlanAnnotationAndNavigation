from domain.maps.workflows.map_workflow_base import MapApprovalWorkflow
from domain.buildings.floor import Floor


class ComplexMapWorkflow(MapApprovalWorkflow):
    def validate_floor(self, floor: Floor) -> bool:
        if not floor.name or not floor.image_path:
            return False
        return len(floor.name) > 0
    
    def check_permissions(self, floor: Floor) -> bool:
        return True
    
    def validate_rooms(self, floor: Floor) -> bool:
        if len(floor.rooms) == 0:
            return False
        for room in floor.rooms:
            if not room.vertices or len(room.vertices) < 3:
                return False
        return True
    
    def finalize_approval(self, floor: Floor) -> bool:
        return True

