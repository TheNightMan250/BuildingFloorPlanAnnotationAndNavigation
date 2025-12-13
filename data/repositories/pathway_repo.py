from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from sqlalchemy import Column, Integer, Text
import json

from models import Base
from domain.buildings.pathway import Pathway


class PathwayModel(Base):
    __tablename__ = 'pathways'
    id = Column(Integer, primary_key=True)
    floor_id = Column(Integer, nullable=False)
    points = Column(Text, nullable=False)  # JSON list of [x, y]


class IPathwayRepository(ABC):
    @abstractmethod
    def find_by_id(self, pathway_id: int) -> Optional[Pathway]:
        pass

    @abstractmethod
    def find_by_floor(self, floor_id: int) -> List[Pathway]:
        pass

    @abstractmethod
    def find_all(self) -> List[Pathway]:
        pass

    @abstractmethod
    def save(self, pathway: Pathway) -> Pathway:
        pass

    @abstractmethod
    def delete(self, pathway_id: int) -> bool:
        pass


class PathwayRepository(IPathwayRepository):
    def __init__(self, db_session=None, db_engine=None):
        self.db_session = db_session
        self.db_engine = db_engine

    def find_by_id(self, pathway_id: int) -> Optional[Pathway]:
        if not self.db_session:
            return None
        model = self.db_session.query(PathwayModel).filter_by(id=pathway_id).first()
        return self._model_to_domain(model) if model else None

    def find_by_floor(self, floor_id: int) -> List[Pathway]:
        if not self.db_session:
            return []
        models = self.db_session.query(PathwayModel).filter_by(floor_id=floor_id).all()
        return [self._model_to_domain(m) for m in models]

    def find_all(self) -> List[Pathway]:
        if not self.db_session:
            return []
        models = self.db_session.query(PathwayModel).all()
        return [self._model_to_domain(m) for m in models]

    def save(self, pathway: Pathway) -> Pathway:
        if not self.db_session:
            return pathway

        if not pathway.points or len(pathway.points) < 2:
            return pathway

        if pathway.pathway_id:
            model = self.db_session.query(PathwayModel).filter_by(id=pathway.pathway_id).first()
            if model:
                model.floor_id = pathway.floor_id
                model.points = json.dumps([[float(x), float(y)] for x, y in pathway.points])
            else:
                model = PathwayModel(
                    floor_id=pathway.floor_id,
                    points=json.dumps([[float(x), float(y)] for x, y in pathway.points]),
                )
                self.db_session.add(model)
        else:
            model = PathwayModel(
                floor_id=pathway.floor_id,
                points=json.dumps([[float(x), float(y)] for x, y in pathway.points]),
            )
            self.db_session.add(model)

        self.db_session.commit()
        pathway.pathway_id = model.id
        return pathway

    def delete(self, pathway_id: int) -> bool:
        if not self.db_session:
            return False
        model = self.db_session.query(PathwayModel).filter_by(id=pathway_id).first()
        if not model:
            return False
        self.db_session.delete(model)
        self.db_session.commit()
        return True

    def _model_to_domain(self, model: PathwayModel) -> Pathway:
        points_raw = json.loads(model.points) if model.points else []
        points: List[Tuple[float, float]] = [(float(p[0]), float(p[1])) for p in points_raw]
        return Pathway(model.id, model.floor_id, points)
