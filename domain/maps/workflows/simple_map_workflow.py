from domain.maps.workflows.map_workflow_base import MapApprovalWorkflow
from domain.buildings.floor import Floor


class SimpleMapWorkflow(MapApprovalWorkflow):
    def validate_floor(self, floor: Floor) -> bool:
        return floor.name and floor.image_path
    
    def check_permissions(self, floor: Floor) -> bool:
        return True
    
    def validate_rooms(self, floor: Floor) -> bool:
        return len(floor.rooms) >= 0
    
    def finalize_approval(self, floor: Floor) -> bool:
        return True

