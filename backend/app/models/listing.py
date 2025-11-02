from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    marketplace_name = Column(String(50), nullable=False, index=True)
    marketplace_listing_id = Column(String(255), unique=True, index=True)  # External marketplace ID
    status = Column(String(50), default="active")  # active, sold, pending, failed, deleted
    price = Column(Float, nullable=False)
    url = Column(String(500))  # Direct link to listing on marketplace
    last_sync_status = Column(String(50), default="pending")  # success, failed, pending
    last_error = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    synced_at = Column(DateTime(timezone=True), onupdate=func.now())
    sold_at = Column(DateTime(timezone=True))

    # Relationships
    product = relationship("Product", back_populates="listings")

