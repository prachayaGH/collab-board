from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base 
import enum

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    oauth_provider = Column(String(20), nullable=True)
    oauth_id = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=True)
    display_name = Column(String(100), nullable=False)
    avatar_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserStatusEnum(enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"

class UserStatus(Base):
    __tablename__ = "user_status"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    status = Column(
        Enum(UserStatusEnum, name="user_status_enum"), 
        default=UserStatusEnum.OFFLINE,
        nullable=False
    )
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="status")

class DirectMessage(Base):
    __tablename__ = "direct_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])

# Add relationships
User.status = relationship("UserStatus", back_populates="user", uselist=False)