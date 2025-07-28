from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base 
import enum

class NotificationType(enum.Enum):
    FRIEND_REQUEST = "friend_request"
    FRIEND_ACCEPTED = "friend_accepted"

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(Enum(NotificationType))
    title = Column(String(255))
    content = Column(Text)
    related_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    related_message_id = Column(Integer, ForeignKey("direct_messages.id"), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", foreign_keys=[user_id])
    related_user = relationship("User", foreign_keys=[related_user_id])
    related_message = relationship("DirectMessage", foreign_keys=[related_message_id])