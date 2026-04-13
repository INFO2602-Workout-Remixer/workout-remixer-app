from fastapi import APIRouter
from app.dependencies import SessionDep, AuthDep
from app.models.workout_log import WorkoutSession
from app.models.exercise import Exercise
from app.models.routine import Routine
from sqlmodel import select, func
from datetime import datetime, timedelta
from app.schemas.dashboard import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: SessionDep, user: AuthDep):
    total_workouts = db.exec(select(func.count(WorkoutSession.id)).where(WorkoutSession.user_id == user.id)).one()
    total_exercises = db.exec(select(func.count(Exercise.id))).one()
    total_routines = db.exec(select(func.count(Routine.id)).where(Routine.user_id == user.id)).one()
    
    today = datetime.utcnow().date()
    start_of_week = today - timedelta(days=today.weekday())
    workouts_this_week = db.exec(
        select(func.count(WorkoutSession.id))
        .where(
            WorkoutSession.user_id == user.id,
            WorkoutSession.completed_at >= start_of_week
        )
    ).one()
    
    week_labels = []
    workout_counts = []
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        week_labels.append(day.strftime("%a"))
        next_day = day + timedelta(days=1)
        count = db.exec(
            select(func.count(WorkoutSession.id))
            .where(
                WorkoutSession.user_id == user.id,
                WorkoutSession.completed_at >= day,
                WorkoutSession.completed_at < next_day
            )
        ).one()
        workout_counts.append(count)
    
    return DashboardStats(
        total_workouts=total_workouts,
        total_exercises=total_exercises,
        total_routines=total_routines,
        workouts_this_week=workouts_this_week,
        week_labels=week_labels,
        workout_counts=workout_counts
    )