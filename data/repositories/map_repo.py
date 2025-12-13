from abc import ABC, abstractmethod
from typing import Optional, List
from domain.buildings.floor import Floor
from models import FloorPlan as FloorPlanModel, DatabaseManager


class IMapRepository(ABC):
    @abstractmethod
    def find_by_id(self, floor_id: int) -> Optional[Floor]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[Floor]:
        pass
    
    @abstractmethod
    def save(self, floor: Floor) -> Floor:
        pass
    
    @abstractmethod
    def delete(self, floor_id: int) -> bool:
        pass


class MapRepository(IMapRepository):
    def __init__(self, db_session=None):
        self.db_session = db_session
    
    def find_by_id(self, floor_id: int) -> Optional[Floor]:
        if not self.db_session:
            return None
        floor_model = self.db_session.query(FloorPlanModel).filter_by(id=floor_id).first()
        if not floor_model:
            return None
        return self._model_to_domain(floor_model)
    
    def find_all(self) -> List[Floor]:
        if not self.db_session:
            return []
        floor_models = self.db_session.query(FloorPlanModel).all()
        return [self._model_to_domain(fm) for fm in floor_models]
    
    def save(self, floor: Floor) -> Floor:
        if not self.db_session:
            return floor
        
        if floor.floor_id:
            floor_model = self.db_session.query(FloorPlanModel).filter_by(id=floor.floor_id).first()
            if floor_model:
                floor_model.name = floor.name
                floor_model.image_path = floor.image_path
            else:
                floor_model = FloorPlanModel(name=floor.name, image_path=floor.image_path)
                self.db_session.add(floor_model)
        else:
            floor_model = FloorPlanModel(name=floor.name, image_path=floor.image_path)
            self.db_session.add(floor_model)
        
        self.db_session.commit()
        floor.floor_id = floor_model.id
        return floor
    
    def delete(self, floor_id: int) -> bool:
        if not self.db_session:
            return False
        floor_model = self.db_session.query(FloorPlanModel).filter_by(id=floor_id).first()
        if floor_model:
            self.db_session.delete(floor_model)
            self.db_session.commit()
            return True
        return False
    
    def _model_to_domain(self, floor_model: FloorPlanModel) -> Floor:
        from domain.buildings.floor import Floor
        floor = Floor(floor_model.id, floor_model.name, floor_model.image_path)
        return floor
