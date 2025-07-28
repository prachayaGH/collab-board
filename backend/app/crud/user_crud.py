from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from ..models import User, UserStatus, Friendship, FriendshipStatus
from typing import List

def get_user_friends(db: Session, user_id: int) -> List[User]:
    """Get all friends of a user with their status"""
    friendships = db.query(Friendship).filter(
        or_(
            and_(Friendship.requester_id == user_id, Friendship.status == FriendshipStatus.ACCEPTED),
            and_(Friendship.addressee_id == user_id, Friendship.status == FriendshipStatus.ACCEPTED)
        )
    ).all()
    
    friends = []
    for friendship in friendships:
        if friendship.requester_id == user_id:
            friend = friendship.addressee
        else:
            friend = friendship.requester
        friends.append(friend)
    
    return friends

def search_users(db: Session, query: str, current_user_id: int, limit: int = 10) -> List[User]:
    """Search users by email or display name"""
    return db.query(User).filter(
        or_(
            User.email.ilike(f"%{query}%"),
            User.display_name.ilike(f"%{query}%")
        ),
        User.id != current_user_id,
        User.is_active == True
    ).limit(limit).all()
