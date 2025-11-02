from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class MarketplaceConnection(Base):
    __tablename__ = "marketplace_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    marketplace_name = Column(String(50), nullable=False, index=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text)
    token_type = Column(String(50), default="Bearer")
    expires_at = Column(DateTime(timezone=True))
    scope = Column(String(500))
    is_active = Column(Boolean, default=True)
    metadata = Column(Text)  # JSON string for additional marketplace-specific data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_synced_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="marketplace_connections")

    # Ensure user can only have one connection per marketplace
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

