from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from ..models import DirectMessage, User
from typing import List

def send_message(db: Session, sender_id: int, receiver_id: int, content: str) -> DirectMessage:
    """Send a direct message"""
    message = DirectMessage(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_chat_history(db: Session, user_id: int, friend_id: int, limit: int = 50) -> List[DirectMessage]:
    """Get chat history between two users"""
    messages = db.query(DirectMessage).filter(
        or_(
            and_(DirectMessage.sender_id == user_id, DirectMessage.receiver_id == friend_id),
            and_(DirectMessage.sender_id == friend_id, DirectMessage.receiver_id == user_id)
        ),
        DirectMessage.is_deleted == False
    ).order_by(desc(DirectMessage.created_at)).limit(limit).all()
    
    return list(reversed(messages))

def mark_messages_as_read(db: Session, sender_id: int, receiver_id: int):
    """Mark all messages from sender to receiver as read"""
    db.query(DirectMessage).filter(
        DirectMessage.sender_id == sender_id,
        DirectMessage.receiver_id == receiver_id,
        DirectMessage.is_read == False
    ).update({"is_read": True})
    db.commit()

def get_unread_message_count(db: Session, user_id: int) -> int:
    """Get count of unread messages for a user"""
    return db.query(DirectMessage).filter(
        DirectMessage.receiver_id == user_id,
        DirectMessage.is_read == False
    ).count()

def get_conversation_previews(db: Session, user_id: int) -> List[dict]:
    """Get conversation previews with last message for each friend"""
    # Get all friends
    from . import friend_crud
    friends = friend_crud.get_user_friends(db, user_id)
    
    conversations = []
    for friend in friends:
        # Get last message between user and friend
        last_message = db.query(DirectMessage).filter(
            or_(
                and_(DirectMessage.sender_id == user_id, DirectMessage.receiver_id == friend.id),
                and_(DirectMessage.sender_id == friend.id, DirectMessage.receiver_id == user_id)
            ),
            DirectMessage.is_deleted == False
        ).order_by(desc(DirectMessage.created_at)).first()
        
        # Get unread count
        unread_count = db.query(DirectMessage).filter(
            DirectMessage.sender_id == friend.id,
            DirectMessage.receiver_id == user_id,
            DirectMessage.is_read == False
        ).count()
        
        conversations.append({
            "friend": friend,
            "last_message": last_message,
            "unread_count": unread_count
        })
    
    # Sort by last message time
    conversations.sort(key=lambda x: x["last_message"].created_at if x["last_message"] else x["friend"].created_at, reverse=True)
    
    return conversations