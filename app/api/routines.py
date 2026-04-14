from fastapi import APIRouter, HTTPException
from app.dependencies import SessionDep, AuthDep
from app.models.routine import Routine
from app.models.routine_exercise import RoutineExercise
from app.schemas.routine import RoutineCreate, RoutineResponse
from sqlmodel import select

router = APIRouter(prefix="/routines", tags=["Routines"])

@router.get("/", response_model=list[RoutineResponse])
async def get_routines(db: SessionDep, user: AuthDep):
    routines = db.exec(select(Routine).where(Routine.user_id == user.id)).all()
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

@router.post("/")
async def create_routine(db: SessionDep, user: AuthDep, routine_data: dict):
    try:
        routine = Routine(
            user_id=user.id,
            name=routine_data.get("name"),
            description=routine_data.get("description"),
            is_public=routine_data.get("is_public", False)
        )
        db.add(routine)
        db.commit()
        db.refresh(routine)
        
        for ex_data in routine_data.get("exercises", []):
            routine_exercise = RoutineExercise(
                routine_id=routine.id,
                exercise_id=ex_data.get("exercise_id"),
                sets=ex_data.get("sets", 3),
                reps=ex_data.get("reps", 10),
                rest_seconds=ex_data.get("rest_seconds", 60),
                order=ex_data.get("order", 0)
            )
            db.add(routine_exercise)
        
        db.commit()
        return {"id": routine.id, "message": "Routine created successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{routine_id}")
async def delete_routine(db: SessionDep, user: AuthDep, routine_id: int):
    routine = db.exec(select(Routine).where(Routine.id == routine_id, Routine.user_id == user.id)).first()
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    db.delete(routine)
    db.commit()
    return {"message": "Routine deleted"}

@router.get("/{routine_id}")
async def get_routine(db: SessionDep, user: AuthDep, routine_id: int):
    routine = db.exec(select(Routine).where(Routine.id == routine_id, Routine.user_id == user.id)).first()
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    
    exercises = db.exec(select(RoutineExercise).where(RoutineExercise.routine_id == routine_id).order_by(RoutineExercise.order)).all()
    
    from app.models.exercise import Exercise
    exercise_list = []
    for re in exercises:
        exercise = db.get(Exercise, re.exercise_id)
        if exercise:
            exercise_list.append({
                "id": exercise.id,
                "name": exercise.name,
                "muscle_group": exercise.muscle_group,
                "sets": re.sets,
                "reps": re.reps,
                "rest_seconds": re.rest_seconds
            })
    
    return {
        "id": routine.id,
        "name": routine.name,
        "description": routine.description,
        "is_public": routine.is_public,
        "is_favorite": routine.is_favorite,
        "exercises": exercise_list
    }