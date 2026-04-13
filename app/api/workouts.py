from fastapi import APIRouter, HTTPException
from app.dependencies import SessionDep, AuthDep
from app.models.workout_log import WorkoutSession
from app.models.routine import Routine
from app.schemas.workout import CompleteWorkoutRequest, WorkoutHistoryResponse
from sqlmodel import select
from datetime import datetime

router = APIRouter(prefix="/workouts", tags=["Workouts"])

@router.post("/complete")
async def complete_workout(db: SessionDep, user: AuthDep, data: CompleteWorkoutRequest):
    session = WorkoutSession(
        user_id=user.id,
        routine_id=data.routine_id,
        completed_at=datetime.utcnow(),
        total_duration_seconds=data.duration_seconds
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"message": "Workout completed", "session_id": session.id}

@router.get("/recent", response_model=list[WorkoutHistoryResponse])
async def get_recent_workouts(db: SessionDep, user: AuthDep):
    workouts = db.exec(
        select(WorkoutSession, Routine.name)
        .join(Routine, WorkoutSession.routine_id == Routine.id)
        .where(WorkoutSession.user_id == user.id, WorkoutSession.completed_at.isnot(None))
        .order_by(WorkoutSession.completed_at.desc())
        .limit(10)
    ).all()
    
    return [
        {
            "id": session.id,
            "routine_name": name,
            "date": session.completed_at,
            "duration_minutes": session.total_duration_seconds // 60 if session.total_duration_seconds else 0,
            "exercise_count": 0
        }
        for session, name in workouts
    ]