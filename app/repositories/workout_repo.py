from sqlmodel import Session, select, func
from app.models.workout_log import WorkoutSession, ExerciseLog
from app.models.routine import Routine
from datetime import datetime, timedelta
from typing import List

class WorkoutRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, user_id: int, routine_id: int) -> WorkoutSession:
        session = WorkoutSession(user_id=user_id, routine_id=routine_id)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def complete_session(self, session_id: int, duration_seconds: int) -> WorkoutSession:
        session = self.db.get(WorkoutSession, session_id)
        if session:
            session.completed_at = datetime.utcnow()
            session.total_duration_seconds = duration_seconds
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
        return session

    def log_exercise(self, session_id: int, exercise_id: int, sets: int, reps: int, weight: float = None):
        log = ExerciseLog(
            workout_session_id=session_id,
            exercise_id=exercise_id,
            sets_completed=sets,
            reps_completed=reps,
            weight_used=weight
        )
        self.db.add(log)
        self.db.commit()
        return log

    def get_user_workouts(self, user_id: int, limit: int = 10) -> List:
        query = (
            select(WorkoutSession, Routine.name)
            .join(Routine, WorkoutSession.routine_id == Routine.id)
            .where(WorkoutSession.user_id == user_id, WorkoutSession.completed_at.isnot(None))
            .order_by(WorkoutSession.completed_at.desc())
            .limit(limit)
        )
        results = self.db.exec(query).all()
        return [
            {
                "id": session.id,
                "routine_name": name,
                "date": session.completed_at,
                "duration_minutes": session.total_duration_seconds // 60 if session.total_duration_seconds else 0,
                "exercise_count": 0
            }
            for session, name in results
        ]

    def get_weekly_stats(self, user_id: int) -> List[int]:
        today = datetime.utcnow().date()
        start_of_week = today - timedelta(days=today.weekday())
        counts = []
        for i in range(7):
            day = start_of_week + timedelta(days=i)
            next_day = day + timedelta(days=1)
            count = self.db.exec(
                select(func.count(WorkoutSession.id))
                .where(
                    WorkoutSession.user_id == user_id,
                    WorkoutSession.completed_at >= day,
                    WorkoutSession.completed_at < next_day
                )
            ).one()
            counts.append(count)
        return counts