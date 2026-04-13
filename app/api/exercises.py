from fastapi import APIRouter, HTTPException
from app.dependencies import SessionDep, AuthDep
from app.models.exercise import Exercise
from app.schemas.exercise import ExerciseCreate, ExerciseResponse
from sqlmodel import select

router = APIRouter(prefix="/exercises", tags=["Exercises"])

@router.get("/", response_model=list[ExerciseResponse])
async def get_exercises(db: SessionDep, user: AuthDep):
    exercises = db.exec(select(Exercise)).all()
    return exercises

@router.post("/", response_model=ExerciseResponse)
async def create_exercise(db: SessionDep, user: AuthDep, exercise_data: ExerciseCreate):
    exercise = Exercise(**exercise_data.model_dump())
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise