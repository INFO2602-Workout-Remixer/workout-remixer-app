from sqlmodel import Session, select, func
from app.models.routine import Routine
from app.models.routine_exercise import RoutineExercise
from typing import Optional, List

class RoutineRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, name: str, description: str = None, is_public: bool = False) -> Routine:
        routine = Routine(user_id=user_id, name=name, description=description, is_public=is_public)
        self.db.add(routine)
        self.db.commit()
        self.db.refresh(routine)
        return routine

    def get_user_routines(self, user_id: int) -> List[Routine]:
        return self.db.exec(select(Routine).where(Routine.user_id == user_id)).all()

    def get_by_id(self, routine_id: int, user_id: int) -> Optional[Routine]:
        return self.db.exec(select(Routine).where(Routine.id == routine_id, Routine.user_id == user_id)).first()

    def delete(self, routine_id: int, user_id: int) -> bool:
        routine = self.get_by_id(routine_id, user_id)
        if routine:
            self.db.delete(routine)
            self.db.commit()
            return True
        return False

    def add_exercise(self, routine_id: int, exercise_id: int, sets: int, reps: int, rest_seconds: int, order: int):
        re = RoutineExercise(
            routine_id=routine_id,
            exercise_id=exercise_id,
            sets=sets,
            reps=reps,
            rest_seconds=rest_seconds,
            order=order
        )
        self.db.add(re)
        self.db.commit()
        return re

    def get_routine_exercises(self, routine_id: int) -> List:
        return self.db.exec(select(RoutineExercise).where(RoutineExercise.routine_id == routine_id).order_by(RoutineExercise.order)).all()