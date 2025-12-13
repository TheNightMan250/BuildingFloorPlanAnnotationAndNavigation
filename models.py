"""
Database models for floor plan application using SQLAlchemy.
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import json
import os

Base = declarative_base()


class FloorPlan(Base):
    """Represents a floor plan with an image."""
    __tablename__ = 'floor_plans'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    image_path = Column(String(500), nullable=False)
    
    # Relationship to rooms
    rooms = relationship("Room", back_populates="floor_plan", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<FloorPlan(id={self.id}, name='{self.name}')>"


class Room(Base):
    """Represents a room with vertices and properties."""
    __tablename__ = 'rooms'
    
    id = Column(Integer, primary_key=True)
    floor_plan_id = Column(Integer, ForeignKey('floor_plans.id'), nullable=False)
    name = Column(String(200), nullable=False, default="Room")
    room_type = Column(String(100), default="Room")
    vertices = Column(Text, nullable=False)  # JSON array of [x, y] coordinates
    
    # Relationship to floor plan
    floor_plan = relationship("FloorPlan", back_populates="rooms")
    
    def get_vertices(self):
        """Parse vertices from JSON string."""
        return json.loads(self.vertices) if self.vertices else []
    
    def set_vertices(self, vertices):
        """Store vertices as JSON string."""
        self.vertices = json.dumps(vertices)
    
    def __repr__(self):
        return f"<Room(id={self.id}, name='{self.name}', type='{self.room_type}')>"


class DatabaseManager:
    """Manages database connection and session."""
    
    def __init__(self, db_path="floorplan_project.db"):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
    
    def get_session(self):
        """Get a new database session."""
        return self.Session()
    
    def close(self):
        """Close database connection."""
        self.engine.dispose()

