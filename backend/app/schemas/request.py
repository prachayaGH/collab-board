from pydantic import BaseModel
from typing import List, Optional

class FriendRequestCreate(BaseModel):
    email: str

class FriendRequestResponse(BaseModel):
    request_id: int
    action: str  # 'accept' or 'decline'