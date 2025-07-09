from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.schemas.user import UserCreate,UserOut
from sqlalchemy.orm import Session
from ..database import SessionLocal
from backend.app.core.security import validate_password
from backend.app.services.auth_service import get_user_by_email, create_user,get_user_by_oauth_id, create_oauth_user
from backend.app.models.user import User
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from starlette.config import Config
import os
from dotenv import load_dotenv
from authlib.common.security import generate_token
from backend.app.schemas.auth import TokenResponse, RefreshTokenRequest
from backend.app.core.jwt_auth import create_access_token, create_refresh_token, verify_token, get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

load_dotenv()
config = Config() 
oauth = OAuth(config)

config = Config(environ={
    "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID"),
    "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET"),
})

oauth = OAuth(config)
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Register a new user
    try:
        # Validate password strength
        if not validate_password(user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one digit"
            )
        
        # Check if user already exists
        existing_user = get_user_by_email(db, user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        new_user = create_user(db, user)

        return UserOut(
            id=new_user.id,
            email=new_user.email,
            oauth_provider=new_user.oauth_provider,
            oauth_id=new_user.oauth_id,
            display_name=new_user.display_name,
            avatar_url=new_user.avatar_url,
            is_active=new_user.is_active,
            created_at=new_user.created_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating user: {str(e)}"
        )
    
@router.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    # Get user by ID
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/me", response_model=UserOut)
async def get_current_user_info(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """ดึงข้อมูล user ปัจจุบันจาก JWT token"""
    user = db.query(User).filter(User.id == current_user["id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token ด้วย refresh token"""
    payload = verify_token(refresh_request.refresh_token, "refresh")
    user_id = payload.get("sub")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # สร้าง token ใหม่
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "display_name": user.display_name}
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "email": user.email,
            "display_name": user.display_name,
            "avatar_url": user.avatar_url
        }
    )

@router.get("/auth/google/login")
async def google_login(request: Request):
    nonce = generate_token()
    request.session[f"{oauth.google.name}_nonce"] = nonce
    print("✅ SET NONCE IN SESSION:", nonce)
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri, nonce=nonce)

@router.get("/auth/google/callback", name="google_callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        print("✅ DEBUG token:", token)

        if not token:
            raise HTTPException(status_code=400, detail="Google authentication failed: Token not received.")
        
        if "id_token" not in token:
            raise HTTPException(status_code=400, detail="Google authentication failed: 'id_token' not found in token.")
        
        nonce_from_session = request.session.get(f"{oauth.google.name}_nonce")
        if not nonce_from_session:
            raise HTTPException(status_code=400, detail="Nonce not found in session")

        user_info = await oauth.google.parse_id_token(token, nonce=nonce_from_session)
        request.session["user"] = dict(user_info)
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authentication failed: {str(e)}"
        )
    # ตรวจสอบว่าผู้ใช้เคย login ด้วย Google มาก่อนมั้ย
    user = get_user_by_oauth_id(db, "google", user_info["sub"])

    if not user:
        user = create_oauth_user(
            db,
            UserCreate(
                email=user_info["email"],
                password="OauthGoogle123",       # ผ่าน validate_password
                display_name=user_info["name"],
                avatar_url=user_info["picture"],
                oauth_provider="google",
                oauth_id=user_info["sub"],
            ),
        )

    # 🔐 สร้าง JWT tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "display_name": user.display_name}
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # ✅ วิธีที่ 2: Redirect ไปหน้า success พร้อม set cookie (แนะนำ)
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    response = RedirectResponse(url=f"{frontend_url}/dashboard")

    # Set HTTP-only cookies (ปลอดภัยกว่า localStorage)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,  # 30 minutes
        secure=True if os.getenv("ENVIRONMENT") == "production" else False,
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=604800,  # 7 days
        secure=True if os.getenv("ENVIRONMENT") == "production" else False,
        samesite="lax"
    )
    
    return response

@router.get("/auth/google/success", response_model=TokenResponse)
async def google_success(request: Request, db: Session = Depends(get_db)):
    """Alternative: ส่งกลับ JSON response พร้อม tokens"""
    user_info = request.session.get("user")
    if not user_info:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = get_user_by_oauth_id(db, "google", user_info["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "display_name": user.display_name}
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "email": user.email,
            "display_name": user.display_name,
            "avatar_url": user.avatar_url
        }
    )

@router.post("/logout")
async def logout():
    """Logout endpoint (ใน production ควรเก็บ blacklist ของ tokens)"""
    return {"message": "Logged out successfully"}