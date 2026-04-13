from sqlmodel import SQLModel
from typing import Optional

class ExerciseCreate(SQLModel):
    name: str
    muscle_group: str
    equipment: Optional[str] = None
    youtube_url: Optional[str] = None
    form_tips: Optional[str] = None

class ExerciseResponse(ExerciseCreate):
    id: int