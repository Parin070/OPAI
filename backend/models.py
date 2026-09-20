import uuid
from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from database import Base

# Association table for Outfit and ClothingItem
outfit_items = Table(
    'outfit_items',
    Base.metadata,
    Column('outfit_id', UUID(as_uuid=True), ForeignKey('outfits.id'), primary_key=True),
    Column('clothing_item_id', UUID(as_uuid=True), ForeignKey('clothing_items.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    body_type = Column(String, nullable=True) # Slim, Athletic, Average, Broad, Plus-size
    preferences = Column(JSONB, nullable=True)
    
    clothing_items = relationship("ClothingItem", back_populates="owner")
    outfits = relationship("Outfit", back_populates="owner")

class ClothingItem(Base):
    __tablename__ = 'clothing_items'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    image_url = Column(String, nullable=False)
    category = Column(String, nullable=True)
    color = Column(String, nullable=True)
    pattern = Column(String, nullable=True)
    formality_score = Column(Float, nullable=True) # E.g., 0.0 to 10.0
    season = Column(String, nullable=True)
    # Using pgvector with 512 dimensions for CLIP openai/clip-vit-base-patch32
    embedding = Column(Vector(512)) 
    
    owner = relationship("User", back_populates="clothing_items")
    outfits = relationship("Outfit", secondary=outfit_items, back_populates="items")

class Outfit(Base):
    __tablename__ = 'outfits'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    event_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_rating = Column(Integer, nullable=True) # +1 or -1
    
    owner = relationship("User", back_populates="outfits")
    items = relationship("ClothingItem", secondary=outfit_items, back_populates="outfits")
