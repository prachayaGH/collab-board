from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..core.jwt_auth import get_current_user
from ..crud import notification_crud

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/")
async def get_notifications(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notifications"""
    notifications = notification_crud.get_user_notifications(db, current_user["id"])
    
    return [
        {
            "id": notif.id,
            "type": notif.type.value,
            "title": notif.title,
            "content": notif.content,
            "is_read": notif.is_read,
            "created_at": notif.created_at.isoformat(),
            "related_user": {
                "id": notif.related_user.id,
                "display_name": notif.related_user.display_name,
                "avatar_url": notif.related_user.avatar_url
            } if notif.related_user else None
        }
        for notif in notifications
    ]

@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    notification_crud.mark_notification_as_read(db, notification_id, current_user["id"])
    return {"success": True}

@router.get("/unread-count")
async def get_unread_notification_count(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get unread notification count"""
    count = notification_crud.get_unread_notification_count(db, current_user["id"])
    return {"count": count}