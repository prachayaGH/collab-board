import socketio
from typing import Dict, Set
from sqlalchemy.orm import Session
from ..database import get_db
from ..core.jwt_auth import verify_token
from ..models import User, UserStatus, UserStatusEnum as StatusEnum
from ..crud import user_crud
import asyncio

sio = socketio.AsyncServer(
    async_mode="asgi", 
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True
)

# Store active connections
active_connections: Dict[str, str] = {}  # socket_id -> user_id
user_connections: Dict[str, Set[str]] = {}  # user_id -> set of socket_ids

async def authenticate_socket(auth_data):
    """Authentication middleware for Socket.IO"""
    try:
        token = auth_data.get('access_token')
        if not token:
            return None
        
        payload = verify_token(token, "access")
        user_id = payload.get("sub")
        if user_id:
            return str(user_id)
        return None
    except Exception as e:
        print(f"Socket auth error: {e}")
        return None

@sio.event
async def connect(sid, environ, auth):
    """Handle client connection"""
    print(f"[socket] trying to connect sid={sid}, auth={auth}, query={environ.get('QUERY_STRING')}")

    token = auth.get("access_token") if auth else None

    if not token:
        return False
    
    user_id = await authenticate_socket(auth)
    if not user_id:
        print(f"Authentication failed for {sid}")
        await sio.disconnect(sid)
        return False
    
    # Store connection
    active_connections[sid] = user_id
    
    if user_id not in user_connections:
        user_connections[user_id] = set()
    user_connections[user_id].add(sid)
    
    # Update user status to online
    db = next(get_db())
    try:
        await update_user_status(db, int(user_id), StatusEnum.ONLINE)
    finally:
        db.close()
    
    # Join user to their personal room
    await sio.enter_room(sid, f"user_{user_id}")
    
    print(f"Client {sid} connected as user {user_id}")
    
    # Notify friends that user is online
    await notify_friends_status_change(user_id, StatusEnum.ONLINE)

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    user_id = active_connections.get(sid)
    if user_id:
        # Remove connection
        user_connections[user_id].discard(sid)
        del active_connections[sid]
        
        # If no more connections for this user, set offline
        if not user_connections.get(user_id):
            db = next(get_db())
            try:
                await update_user_status(db, int(user_id), StatusEnum.OFFLINE)
            finally:
                db.close()
            
            # Clean up empty user connections
            if user_id in user_connections:
                del user_connections[user_id]
            
            # Notify friends that user is offline
            await notify_friends_status_change(user_id, StatusEnum.OFFLINE)
    
    print(f"Client {sid} disconnected")

async def update_user_status(db: Session, user_id: int, status: StatusEnum):
    """Update user online status"""
    try:
        user_status = db.query(UserStatus).filter(UserStatus.user_id == user_id).first()
        if user_status:
            user_status.status = status
        else:
            user_status = UserStatus(user_id=user_id, status=status)
            db.add(user_status)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error updating user status: {e}")

async def notify_friends_status_change(user_id: str, status: StatusEnum):
    """Notify friends about user status change"""
    db = next(get_db())
    try:
        friends = user_crud.get_user_friends(db, int(user_id))
        for friend in friends:
            friend_id = str(friend.id)
            if friend_id in user_connections:
                await sio.emit('friend_status_changed', {
                    'user_id': user_id,
                    'status': status.value,
                    'display_name': friend.display_name,
                    'avatar_url': friend.avatar_url
                }, room=f"user_{friend_id}")
    finally:
        db.close()

@sio.event
async def send_friend_request(sid, data):
    """Handle sending friend request"""
    user_id = active_connections.get(sid)
    print(f"User {user_id} sending friend request")
    if not user_id:
        await sio.emit('error', {'message': 'Unauthorized'}, room=sid)
        return
    
    target_email = data.get('email')
    if not target_email:
        await sio.emit('error', {'message': 'Email is required'}, room=sid)
        return
    
    db = next(get_db())
    try:
        from ..crud import friend_crud
        result = friend_crud.send_friend_request(db, int(user_id), target_email)
        print(f"Friend request result: {result}")
        
        if result['success']:
            # Notify target user if online
            target_user_id = str(result['friendship'].addressee_id)
            if target_user_id in user_connections:
                await sio.emit('friend_request_received', {
                    'id': result['friendship'].id,
                    'requester': {
                        'id': result['friendship'].requester.id,
                        'display_name': result['friendship'].requester.display_name,
                        'avatar_url': result['friendship'].requester.avatar_url,
                        'email': result['friendship'].requester.email
                    },
                    'created_at': result['friendship'].created_at.isoformat()
                }, room=f"user_{target_user_id}")
            
            await sio.emit('friend_request_sent', result, room=sid)
        else:
            await sio.emit('error', {'message': result['message']}, room=sid)
    finally:
        db.close()

@sio.event
async def respond_friend_request(sid, data):
    """Handle responding to friend request"""
    user_id = active_connections.get(sid)
    if not user_id:
        await sio.emit('error', {'message': 'Unauthorized'}, room=sid)
        return
    
    request_id = data.get('request_id')
    action = data.get('action')  # 'accept' or 'decline'
    
    if not request_id or action not in ['accept', 'decline']:
        await sio.emit('error', {'message': 'Invalid request'}, room=sid)
        return
    
    db = next(get_db())
    try:
        from ..crud import friend_crud
        result = friend_crud.respond_to_friend_request(db, int(user_id), request_id, action)
        
        if result['success']:
            # Notify requester if online
            requester_id = str(result['friendship'].requester_id)
            if requester_id in user_connections:
                await sio.emit('friend_request_responded', {
                    'id': result['friendship'].id,
                    'action': action,
                    'user': {
                        'id': result['friendship'].addressee.id,
                        'display_name': result['friendship'].addressee.display_name,
                        'avatar_url': result['friendship'].addressee.avatar_url,
                        'email': result['friendship'].addressee.email
                    }
                }, room=f"user_{requester_id}")
            
            await sio.emit('friend_request_updated', result, room=sid)
        else:
            await sio.emit('error', {'message': result['message']}, room=sid)
    finally:
        db.close()

@sio.event
async def join_chat(sid, data):
    """Join a private chat room"""
    user_id = active_connections.get(sid)
    if not user_id:
        await sio.emit('error', {'message': 'Unauthorized'}, room=sid)
        return
    
    friend_id = data.get('friend_id')
    if not friend_id:
        await sio.emit('error', {'message': 'Friend ID is required'}, room=sid)
        return
    
    # Create room name (consistent ordering)
    room_name = f"chat_{min(int(user_id), friend_id)}_{max(int(user_id), friend_id)}"
    
    await sio.enter_room(sid, room_name)
    await sio.emit('joined_chat', {'room': room_name, 'friend_id': friend_id}, room=sid)

@sio.event
async def send_message(sid, data):
    """Send a direct message"""
    user_id = active_connections.get(sid)
    if not user_id:
        await sio.emit('error', {'message': 'Unauthorized'}, room=sid)
        return
    
    receiver_id = data.get('receiver_id')
    content = data.get('content')
    
    if not receiver_id or not content:
        await sio.emit('error', {'message': 'Receiver ID and content are required'}, room=sid)
        return
    
    db = next(get_db())
    try:
        from ..crud import message_crud
        message = message_crud.send_message(db, int(user_id), receiver_id, content)
        
        # Create room name
        room_name = f"chat_{min(int(user_id), receiver_id)}_{max(int(user_id), receiver_id)}"
        
        message_data = {
            'id': message.id,
            'sender_id': message.sender_id,
            'receiver_id': message.receiver_id,
            'content': message.content,
            'is_read': message.is_read,
            'created_at': message.created_at.isoformat(),
            'sender': {
                'id': message.sender.id,
                'display_name': message.sender.display_name,
                'avatar_url': message.sender.avatar_url
            }
        }
        
        # Send to chat room
        await sio.emit('message_received', message_data, room=room_name)
        
        # Send notification to receiver if not in chat room
        receiver_id_str = str(receiver_id)
        if receiver_id_str in user_connections:
            await sio.emit('new_message_notification', {
                'message': message_data,
                'sender': message_data['sender']
            }, room=f"user_{receiver_id_str}")
    
    finally:
        db.close()

async def mark_messages_read(sid, data):
    """Mark messages as read"""
    user_id = active_connections.get(sid)
    if not user_id:
        await sio.emit('error', {'message': 'Unauthorized'}, room=sid)
        return
    
    sender_id = data.get('sender_id')
    if not sender_id:
        await sio.emit('error', {'message': 'Sender ID is required'}, room=sid)
        return
    
    db = next(get_db())
    try:
        from ..crud import message_crud
        message_crud.mark_messages_as_read(db, sender_id, int(user_id))
        
        await sio.emit('messages_marked_read', {
            'sender_id': sender_id,
            'receiver_id': int(user_id)
        }, room=sid)
    finally:
        db.close()

def get_online_users():
    """Get list of currently online users"""
    return list(user_connections.keys())