from app.repositories.exercise_repo import ExerciseRepository
from app.schemas.exercise import ExerciseCreate

class ExerciseService:
    def __init__(self, repo: ExerciseRepository):
        self.repo = repo

    def create_exercise(self, data: ExerciseCreate):
        return self.repo.create(data.model_dump())

    def get_all_exercises(self):
        return self.repo.get_all()