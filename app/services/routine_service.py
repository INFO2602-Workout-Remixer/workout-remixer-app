from app.repositories.routine_repo import RoutineRepository
from app.schemas.routine import RoutineCreate

class RoutineService:
    def __init__(self, repo: RoutineRepository):
        self.repo = repo

    def create_routine(self, user_id: int, data: RoutineCreate):
        return self.repo.create(user_id, data.name, data.description, data.is_public)

    def get_user_routines(self, user_id: int):
        routines = self.repo.get_user_routines(user_id)
        return [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "is_public": r.is_public,
                "is_favorite": r.is_favorite,
                "exercise_count": 0
            }
            for r in routines
        ]

    def delete_routine(self, routine_id: int, user_id: int):
        return self.repo.delete(routine_id, user_id)

    def add_exercise_to_routine(self, routine_id: int, user_id: int, exercise_id: int, sets: int, reps: int, rest_seconds: int, order: int):
        routine = self.repo.get_by_id(routine_id, user_id)
        if not routine:
            return None
        return self.repo.add_exercise(routine_id, exercise_id, sets, reps, rest_seconds, order)

    def get_workout_data(self, routine_id: int, user_id: int):
        routine = self.repo.get_by_id(routine_id, user_id)
        if not routine:
            return None
        exercises = self.repo.get_routine_exercises(routine_id)
        return {
            "routine_name": routine.name,
            "exercises": [
                {
                    "id": re.exercise_id,
                    "name": re.exercise.name if re.exercise else "Unknown",
                    "sets": re.sets,
                    "reps": re.reps,
                    "rest_seconds": re.rest_seconds
                }
                for re in exercises
            ]
        }