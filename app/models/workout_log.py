from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime

class WorkoutSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    routine_id: int = Field(foreign_key="routine.id")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    total_duration_seconds: Optional[int] = None

class ExerciseLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    workout_session_id: int = Field(foreign_key="workoutsession.id")
    exercise_id: int = Field(foreign_key="exercise.id")
    sets_completed: int
    reps_completed: int
    weight_used: Optional[float] = None
    notes: Optional[str] = None
    logged_at: datetime = Field(default_factory=datetime.utcnow)