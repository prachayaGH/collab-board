from fastapi import APIRouter, Depends, HTTPException, status
from ..schemas.user import UserCreate, UserOut, LoginRequest
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..core.security import validate_password,verify_password
from ..services.auth_service import get_user_by_email, create_user,get_user_by_oauth_id, create_oauth_user
from ..models.user import User
from fastapi.responses import RedirectResponse, Response
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from starlette.config import Config
import os
from dotenv import load_dotenv
from authlib.common.security import generate_token
from ..schemas.auth import TokenResponse, RefreshTokenRequest
from ..core.jwt_auth import create_access_token, create_refresh_token, verify_token, get_current_user
from fastapi.responses import JSONResponse

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
    
@router.post("/login", response_model=TokenResponse)
async def login(user: LoginRequest, db: Session = Depends(get_db)):
    user_data = get_user_by_email(db, user.email)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    if not verify_password(user.password, user_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = create_access_token(
        data={"sub": str(user_data.id), "email": user_data.email, "display_name": user_data.display_name}
    )
    refresh_token = create_refresh_token(data={"sub": str(user_data.id)})
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    response = JSONResponse(content={"message": "Login successful", "redirect_url": "/dashboard"})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,  # 30 minutes
        secure=True if os.getenv("ENVIRONMENT") == "production" else False,
        samesite="none" if os.getenv("ENVIRONMENT") == "production" else "lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=604800,  # 7 days
        secure=True if os.getenv("ENVIRONMENT") == "production" else False,
        samesite="none" if os.getenv("ENVIRONMENT") == "production" else "lax"
    )

    return response
    
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
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri, nonce=nonce)

@router.get("/auth/google/callback", name="google_callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)

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

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "display_name": user.display_name}
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    response = RedirectResponse(url=f"{frontend_url}/dashboard")

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,  # 30 minutes
        secure=True if os.getenv("ENVIRONMENT") == "production" else False,
        samesite="none" if os.getenv("ENVIRONMENT") == "production" else "lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=604800,  # 7 days
        secure=True if os.getenv("ENVIRONMENT") == "production" else False,
        samesite="none" if os.getenv("ENVIRONMENT") == "production" else "lax"
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
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully"}