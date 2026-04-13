from sqlmodel import Session, select
from app.models.exercise import Exercise
from typing import Optional, List

class ExerciseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, exercise_data: dict) -> Exercise:
        exercise = Exercise(**exercise_data)
        self.db.add(exercise)
        self.db.commit()
        self.db.refresh(exercise)
        return exercise

    def get_all(self) -> List[Exercise]:
        return self.db.exec(select(Exercise)).all()

    def get_by_id(self, exercise_id: int) -> Optional[Exercise]:
        return self.db.get(Exercise, exercise_id)