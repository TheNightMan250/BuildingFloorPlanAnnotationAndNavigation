from abc import ABC, abstractmethod
from typing import Optional, List
from domain.buildings.room import Room
from models import Room as RoomModel


class IRoomRepository(ABC):
    @abstractmethod
    def find_by_id(self, room_id: int) -> Optional[Room]:
        pass
    
    @abstractmethod
    def find_by_floor_id(self, floor_id: int) -> List[Room]:
        pass
    
    @abstractmethod
    def save(self, room: Room) -> Room:
        pass
    
    @abstractmethod
    def delete(self, room_id: int) -> bool:
        pass


class RoomRepository(IRoomRepository):
    def __init__(self, db_session=None):
        self.db_session = db_session
    
    def find_by_id(self, room_id: int) -> Optional[Room]:
        if not self.db_session:
            return None
        room_model = self.db_session.query(RoomModel).filter_by(id=room_id).first()
        if not room_model:
            return None
        return self._model_to_domain(room_model)
    
    def find_by_floor_id(self, floor_id: int) -> List[Room]:
        if not self.db_session:
            return []
        room_models = self.db_session.query(RoomModel).filter_by(floor_plan_id=floor_id).all()
        return [self._model_to_domain(rm) for rm in room_models]
    
    def save(self, room: Room) -> Room:
        if not self.db_session:
            return room
        
        if room.room_id:
            room_model = self.db_session.query(RoomModel).filter_by(id=room.room_id).first()
            if room_model:
                room_model.name = room.name
                room_model.room_type = room.room_type
                room_model.set_vertices(room.vertices)
            else:
                room_model = RoomModel(
                    floor_plan_id=room.floor_id,
                    name=room.name,
                    room_type=room.room_type
                )
                room_model.set_vertices(room.vertices)
                self.db_session.add(room_model)
        else:
            room_model = RoomModel(
                floor_plan_id=room.floor_id,
                name=room.name,
                room_type=room.room_type
            )
            room_model.set_vertices(room.vertices)
            self.db_session.add(room_model)
        
        self.db_session.commit()
        room.room_id = room_model.id
        return room
    
    def delete(self, room_id: int) -> bool:
        if not self.db_session:
            return False
        room_model = self.db_session.query(RoomModel).filter_by(id=room_id).first()
        if room_model:
            self.db_session.delete(room_model)
            self.db_session.commit()
            return True
        return False
    
    def _model_to_domain(self, room_model: RoomModel) -> Room:
        from domain.buildings.room import Room
        room = Room(
            room_model.id,
            room_model.name,
            room_model.room_type,
            room_model.get_vertices(),
            room_model.floor_plan_id
        )
        return room
