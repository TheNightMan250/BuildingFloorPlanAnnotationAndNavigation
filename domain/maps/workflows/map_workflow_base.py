from abc import ABC, abstractmethod
from domain.buildings.floor import Floor


class MapApprovalWorkflow(ABC):
    def approve(self, floor: Floor) -> bool:
        if not self.validate_floor(floor):
            return False
        if not self.check_permissions(floor):
            return False
        if not self.validate_rooms(floor):
            return False
        return self.finalize_approval(floor)
    
    @abstractmethod
    def validate_floor(self, floor: Floor) -> bool:
        pass
    
    @abstractmethod
    def check_permissions(self, floor: Floor) -> bool:
        pass
    
    @abstractmethod
    def validate_rooms(self, floor: Floor) -> bool:
        pass
    
    @abstractmethod
    def finalize_approval(self, floor: Floor) -> bool:
        pass

