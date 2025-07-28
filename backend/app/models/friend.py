from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base 
import enum

class FriendshipStatus(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"

class Friendship(Base):
    __tablename__ = "friendships"
    
    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"))
    addressee_id = Column(Integer, ForeignKey("users.id"))
    status = Column(
        Enum(FriendshipStatus, name="friendship_status"),  # ใส่ชื่อ enum
        default=FriendshipStatus.PENDING,
        nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    requester = relationship("User", foreign_keys=[requester_id])
    addressee = relationship("User", foreign_keys=[addressee_id])