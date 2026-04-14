from pydantic import BaseModel, EmailStr
from typing import Optional

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
 
class AdminCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "admin"

class RegularUserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "regular_user"

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str