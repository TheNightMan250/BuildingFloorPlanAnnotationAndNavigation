from abc import ABC, abstractmethod
from typing import Optional, List
from domain.buildings.stair import Stair
from models import Base
from sqlalchemy import Column, Integer, Float, ForeignKey


class StairModel(Base):
    __tablename__ = 'stairs'
    id = Column(Integer, primary_key=True)
    from_floor_id = Column(Integer, nullable=False)
    to_floor_id = Column(Integer, nullable=False)
    position_x = Column(Float, nullable=False)
    position_y = Column(Float, nullable=False)


class IStairRepository(ABC):
    @abstractmethod
    def find_by_id(self, stair_id: int) -> Optional[Stair]:
        pass
    
    @abstractmethod
    def find_by_floor(self, floor_id: int) -> List[Stair]:
        pass
    
    @abstractmethod
    def find_between_floors(self, floor_id_1: int, floor_id_2: int) -> List[Stair]:
        pass
    
    @abstractmethod
    def save(self, stair: Stair) -> Stair:
        pass
    
    @abstractmethod
    def delete(self, stair_id: int) -> bool:
        pass


class StairRepository(IStairRepository):
    def __init__(self, db_session=None, db_engine=None):
        self.db_session = db_session
        self.db_engine = db_engine
    
    def find_by_id(self, stair_id: int) -> Optional[Stair]:
        if not self.db_session:
            return None
        stair_model = self.db_session.query(StairModel).filter_by(id=stair_id).first()
        if not stair_model:
            return None
        return self._model_to_domain(stair_model)
    
    def find_by_floor(self, floor_id: int) -> List[Stair]:
        if not self.db_session:
            return []
        stair_models = self.db_session.query(StairModel).filter(
            (StairModel.from_floor_id == floor_id) | (StairModel.to_floor_id == floor_id)
        ).all()
        return [self._model_to_domain(sm) for sm in stair_models]
    
    def find_between_floors(self, floor_id_1: int, floor_id_2: int) -> List[Stair]:
        if not self.db_session:
            return []
        stair_models = self.db_session.query(StairModel).filter(
            ((StairModel.from_floor_id == floor_id_1) & (StairModel.to_floor_id == floor_id_2)) |
            ((StairModel.from_floor_id == floor_id_2) & (StairModel.to_floor_id == floor_id_1))
        ).all()
        return [self._model_to_domain(sm) for sm in stair_models]
    
    def save(self, stair: Stair) -> Stair:
        if not self.db_session:
            return stair
        
        if stair.stair_id:
            stair_model = self.db_session.query(StairModel).filter_by(id=stair.stair_id).first()
            if stair_model:
                stair_model.from_floor_id = stair.from_floor_id
                stair_model.to_floor_id = stair.to_floor_id
                stair_model.position_x = stair.position[0]
                stair_model.position_y = stair.position[1]
            else:
                stair_model = StairModel(
                    from_floor_id=stair.from_floor_id,
                    to_floor_id=stair.to_floor_id,
                    position_x=stair.position[0],
                    position_y=stair.position[1]
                )
                self.db_session.add(stair_model)
        else:
            stair_model = StairModel(
                from_floor_id=stair.from_floor_id,
                to_floor_id=stair.to_floor_id,
                position_x=stair.position[0],
                position_y=stair.position[1]
            )
            self.db_session.add(stair_model)
        
        self.db_session.commit()
        stair.stair_id = stair_model.id
        return stair
    
    def delete(self, stair_id: int) -> bool:
        if not self.db_session:
            return False
        stair_model = self.db_session.query(StairModel).filter_by(id=stair_id).first()
        if stair_model:
            self.db_session.delete(stair_model)
            self.db_session.commit()
            return True
        return False
    
    def _model_to_domain(self, stair_model: StairModel) -> Stair:
        from domain.buildings.stair import Stair
        stair = Stair(
            stair_model.id,
            stair_model.from_floor_id,
            stair_model.to_floor_id,
            (stair_model.position_x, stair_model.position_y)
        )
        return stair

