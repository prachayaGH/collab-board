from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models import Notification
from typing import List

def get_user_notifications(db: Session, user_id: int, limit: int = 20) -> List[Notification]:
    """Get notifications for a user"""
    return db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(desc(Notification.created_at)).limit(limit).all()

def mark_notification_as_read(db: Session, notification_id: int, user_id: int):
    """Mark a notification as read"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()
    
    if notification:
        notification.is_read = True
        db.commit()

def get_unread_notification_count(db: Session, user_id: int) -> int:
    """Get count of unread notifications"""
    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).count()