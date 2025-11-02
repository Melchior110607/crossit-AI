from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable until we identify the user
    marketplace_name = Column(String(50), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)  # sale, order_update, listing_update, etc.
    payload = Column(Text, nullable=False)  # JSON string of the full webhook payload
    processed = Column(Boolean, default=False)
    processing_error = Column(Text)
    external_id = Column(String(255), index=True)  # Marketplace's event ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="webhook_events")

