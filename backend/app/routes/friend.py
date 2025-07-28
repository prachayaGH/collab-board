from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..core.jwt_auth import get_current_user
from ..crud import friend_crud, user_crud, notification_crud
from ..schemas.request import FriendRequestCreate,FriendRequestResponse
from ..models.friend import Friendship, FriendshipStatus
from sqlalchemy import or_, and_

router = APIRouter(prefix="/friends", tags=["friends"])

@router.post("/request")
async def send_friend_request(
    request: FriendRequestCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a friend request"""
    result = friend_crud.send_friend_request(db, current_user["id"], request.email)
    print(f"Friend request result: {result}")
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/respond")
async def respond_friend_request(
    response: FriendRequestResponse,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Respond to a friend request"""
    result = friend_crud.respond_to_friend_request(
        db, current_user["id"], response.request_id, response.action
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.get("/requests/pending")
async def get_pending_requests(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pending friend requests"""
    requests = friend_crud.get_pending_friend_requests(db, current_user["id"])
    return [
        {
            "id": req.id,
            "requester": {
                "id": req.requester.id,
                "display_name": req.requester.display_name,
                "avatar_url": req.requester.avatar_url,
                "email": req.requester.email
            },
            "created_at": req.created_at.isoformat()
        }
        for req in requests
    ]

@router.get("/requests/sent")
async def get_sent_requests(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get sent friend requests"""
    requests = friend_crud.get_sent_friend_requests(db, current_user["id"])
    return [
        {
            "id": req.id,
            "addressee": {
                "id": req.addressee.id,
                "display_name": req.addressee.display_name,
                "avatar_url": req.addressee.avatar_url,
                "email": req.addressee.email
            },
            "created_at": req.created_at.isoformat()
        }
        for req in requests
    ]

@router.get("/")
async def get_friends(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's friends list"""
    friends = user_crud.get_user_friends(db, current_user["id"])
    return [
        {
            "id": friend.id,
            "display_name": friend.display_name,
            "avatar_url": friend.avatar_url,
            "email": friend.email,
            "status": friend.status.status.value if friend.status else "offline",
            "last_seen": friend.status.last_seen.isoformat() if friend.status and friend.status.last_seen else None
        }
        for friend in friends
    ]

@router.get("/search")
async def search_users(
    q: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search users by email or display name"""
    if len(q) < 2:
        return []
    
    users = user_crud.search_users(db, q, current_user["id"])
    result = []

    for user in users:
        # ตรวจสอบสถานะความสัมพันธ์
        friendship = db.query(Friendship).filter(
            or_(
                and_(Friendship.requester_id == current_user["id"], Friendship.addressee_id == user.id),
                and_(Friendship.requester_id == user.id, Friendship.addressee_id == current_user["id"])
            )
        ).first()

        if friendship:
            if friendship.status == FriendshipStatus.ACCEPTED:
                relationship = "friends"
            elif friendship.status == FriendshipStatus.PENDING:
                if friendship.requester_id == current_user["id"]:
                    relationship = "requested"
                else:
                    relationship = "incoming"
            else:
                relationship = "none"
        else:
            relationship = "none"

        result.append({
            "id": user.id,
            "display_name": user.display_name,
            "avatar_url": user.avatar_url,
            "email": user.email,
            "status": user.status,
            "relationship": relationship
        })

    return result