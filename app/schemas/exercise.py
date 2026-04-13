from sqlmodel import SQLModel
from typing import Optional, List
from app.schemas.exercise import ExerciseResponse

class RoutineCreate(SQLModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False

class RoutineResponse(SQLModel):
    id: int
    name: str
    description: Optional[str] = None
    is_public: bool
    is_favorite: bool
    exercise_count: int

class RoutineDetailResponse(RoutineResponse):
    exercises: List[ExerciseResponse]

class RoutineExerciseCreate(SQLModel):
    exercise_id: int
    sets: int
    reps: int
    rest_seconds: int
    order: int