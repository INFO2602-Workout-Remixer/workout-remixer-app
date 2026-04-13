from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime

class RoutineBase(SQLModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False
    is_favorite: bool = False

class Routine(RoutineBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: "User" = Relationship(back_populates="routines")