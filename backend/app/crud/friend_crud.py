from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.friend import Friendship, FriendshipStatus
from app.models.user import User
from app.models.notification import Notification, NotificationType
# from ..schemas.Request import FriendRequestCreate, FriendRequestResponse 
from typing import List, Dict, Any

def send_friend_request(db: Session, requester_id: int, target_email: str) -> Dict[str, Any]:
    """Send a friend request"""
    # Find target user
    target_user = db.query(User).filter(User.email == target_email).first()
    if not target_user:
        return {"success": False, "message": "User not found"}
    
    if target_user.id == requester_id:
        return {"success": False, "message": "Cannot send friend request to yourself"}
    
    # Check if friendship already exists
    existing_friendship = db.query(Friendship).filter(
        or_(
            and_(Friendship.requester_id == requester_id, Friendship.addressee_id == target_user.id),
            and_(Friendship.requester_id == target_user.id, Friendship.addressee_id == requester_id)
        )
    ).first()
    
    if existing_friendship:
        if existing_friendship.status == FriendshipStatus.PENDING:
            return {"success": False, "message": "Friend request already sent"}
        elif existing_friendship.status == FriendshipStatus.ACCEPTED:
            return {"success": False, "message": "Already friends"}
    
    # Create friendship request
    friendship = Friendship(
        requester_id=requester_id,
        addressee_id=target_user.id,
        status=FriendshipStatus.PENDING
    )
    db.add(friendship)
    
    # Create notification
    notification = Notification(
        user_id=target_user.id,
        type=NotificationType.FRIEND_REQUEST,
        title="New Friend Request",
        content=f"You have a new friend request",
        related_user_id=requester_id
    )
    db.add(notification)
    
    db.commit()
    db.refresh(friendship)
    
    return {
        "success": True,
        "message": "Friend request sent successfully",
        "friendship": friendship
    }

def respond_to_friend_request(db: Session, user_id: int, request_id: int, action: str) -> Dict[str, Any]:
    """Respond to a friend request (accept/decline)"""
    friendship = db.query(Friendship).filter(
        Friendship.id == request_id,
        Friendship.addressee_id == user_id,
        Friendship.status == FriendshipStatus.PENDING
    ).first()
    
    if not friendship:
        return {"success": False, "message": "Friend request not found"}
    
    if action == "accept":
        friendship.status = FriendshipStatus.ACCEPTED
        
        # Create notification for requester
        notification = Notification(
            user_id=friendship.requester_id,
            type=NotificationType.FRIEND_ACCEPTED,
            title="Friend Request Accepted",
            content=f"Your friend request has been accepted",
            related_user_id=user_id
        )
        db.add(notification)
        
    elif action == "decline":
        friendship.status = FriendshipStatus.DECLINED
    
    db.commit()
    db.refresh(friendship)
    
    return {
        "success": True,
        "message": f"Friend request {action}ed successfully",
        "friendship": friendship
    }

def get_pending_friend_requests(db: Session, user_id: int) -> List[Friendship]:
    """Get pending friend requests for a user"""
    return db.query(Friendship).filter(
        Friendship.addressee_id == user_id,
        Friendship.status == FriendshipStatus.PENDING
    ).all()

def get_sent_friend_requests(db: Session, user_id: int) -> List[Friendship]:
    """Get sent friend requests by a user"""
    return db.query(Friendship).filter(
        Friendship.requester_id == user_id,
        Friendship.status == FriendshipStatus.PENDING
    ).all()

def get_user_friends(db: Session, user_id: int) -> List[User]:
    """Get all friends of a user"""
    friendships = db.query(Friendship).filter(
        or_(
            and_(Friendship.requester_id == user_id, Friendship.status == FriendshipStatus.ACCEPTED),
            and_(Friendship.addressee_id == user_id, Friendship.status == FriendshipStatus.ACCEPTED)
        )
    ).all()
    
    friends = []
    for friendship in friendships:
        if friendship.requester_id == user_id:
            friends.append(friendship.addressee)
        else:
            friends.append(friendship.requester)
    
    return friends