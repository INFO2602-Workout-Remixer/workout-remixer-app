from sqlmodel import SQLModel
from typing import Optional, List
from datetime import datetime

class CompleteWorkoutRequest(SQLModel):
    routine_id: int
    duration_seconds: int
    completed_exercises: List[dict]

class WorkoutHistoryResponse(SQLModel):
    id: int
    routine_name: str
    date: datetime
    duration_minutes: int
    exercise_count: int