from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..core.jwt_auth import get_current_user
from ..crud import message_crud
from pydantic import BaseModel
from typing import List, Optional
from ..schemas.chat import MessageCreate

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/send")
async def send_message(
    message: MessageCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a direct message"""
    msg = message_crud.send_message(
        db, current_user["id"], message.receiver_id, message.content
    )
    
    return {
        "id": msg.id,
        "sender_id": msg.sender_id,
        "receiver_id": msg.receiver_id,
        "content": msg.content,
        "is_read": msg.is_read,
        "created_at": msg.created_at.isoformat(),
        "sender": {
            "id": msg.sender.id,
            "display_name": msg.sender.display_name,
            "avatar_url": msg.sender.avatar_url
        }
    }

@router.get("/history/{friend_id}")
async def get_chat_history(
    friend_id: int,
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history with a friend"""
    messages = message_crud.get_chat_history(db, current_user["id"], friend_id, limit)
    
    return [
        {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "receiver_id": msg.receiver_id,
            "content": msg.content,
            "is_read": msg.is_read,
            "created_at": msg.created_at.isoformat(),
            "sender": {
                "id": msg.sender.id,
                "display_name": msg.sender.display_name,
                "avatar_url": msg.sender.avatar_url
            }
        }
        for msg in messages
    ]

@router.post("/read/{sender_id}")
async def mark_messages_read(
    sender_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark messages from a sender as read"""
    message_crud.mark_messages_as_read(db, sender_id, current_user["id"])
    return {"success": True}

@router.get("/conversations")
async def get_conversations(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation previews"""
    conversations = message_crud.get_conversation_previews(db, current_user["id"])
    
    return [
        {
            "friend": {
                "id": conv["friend"].id,
                "display_name": conv["friend"].display_name,
                "avatar_url": conv["friend"].avatar_url,
                "status": conv["friend"].status.status.value if conv["friend"].status else "offline"
            },
            "last_message": {
                "id": conv["last_message"].id,
                "content": conv["last_message"].content,
                "sender_id": conv["last_message"].sender_id,
                "created_at": conv["last_message"].created_at.isoformat()
            } if conv["last_message"] else None,
            "unread_count": conv["unread_count"]
        }
        for conv in conversations
    ]

@router.get("/unread-count")
async def get_unread_count(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get total unread message count"""
    count = message_crud.get_unread_message_count(db, current_user["id"])
    return {"count": count}
