from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String(100))
    images = Column(JSON, default=list)  # List of image URLs
    condition = Column(String(50), default="new")  # new, used, refurbished
    brand = Column(String(100))
    size = Column(String(50))
    color = Column(String(50))
    sku = Column(String(100), unique=True, index=True)
    quantity = Column(Integer, default=1)
    weight = Column(Float)  # in kg
    dimensions = Column(JSON)  # {length, width, height} in cm
    metadata = Column(JSON, default=dict)  # Additional custom fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="products")
    listings = relationship("Listing", back_populates="product", cascade="all, delete-orphan")

