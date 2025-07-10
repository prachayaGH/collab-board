from pydantic import BaseModel
from typing import Optional

# Define the constant or import it from your settings
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Set this to your desired value or import from config

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60
    user: dict

class RefreshTokenRequest(BaseModel):
    refresh_token: str