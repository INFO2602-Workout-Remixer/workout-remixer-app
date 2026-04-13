from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime

class ExerciseBase(SQLModel):
    name: str = Field(index=True, unique=True)
    muscle_group: str
    equipment: Optional[str] = None
    youtube_url: Optional[str] = None
    form_tips: Optional[str] = None

class Exercise(ExerciseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)