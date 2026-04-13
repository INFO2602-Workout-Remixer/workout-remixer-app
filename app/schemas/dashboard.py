from sqlmodel import SQLModel
from typing import List

class DashboardStats(SQLModel):
    total_workouts: int
    total_exercises: int
    total_routines: int
    workouts_this_week: int
    week_labels: List[str]
    workout_counts: List[int]