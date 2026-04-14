from fastapi import APIRouter, HTTPException
from app.dependencies import SessionDep, AuthDep
from app.models.routine import Routine
from app.models.routine_exercise import RoutineExercise
from app.models.exercise import Exercise
from app.models.user import User
from sqlmodel import select
import httpx
import random

router = APIRouter(prefix="/routines", tags=["Routines"])

AI_API_KEY = "sk-59addf63a8bd464c92242421db666aa1"
AI_BASE_URL = "https://ai-gen.sundaebytesett.com"
AI_MODEL = "meta/llama-3.2-3b-instruct"

async def get_ai_suggestion(exercise_name: str, muscle_group: str, equipment: str) -> str:
    fallbacks = {
        "chest": ["Push Up", "Incline Dumbbell Press", "Dumbbell Press", "Chest Fly", "Cable Crossover"],
        "back": ["Pull Up", "Lat Pulldown", "Seated Cable Row", "Barbell Row", "Pull Up"],
        "legs": ["Squat", "Lunge", "Leg Press", "Deadlift", "Goblet Squat"],
        "shoulders": ["Overhead Press", "Lateral Raise", "Front Raise", "Face Pull", "Arnold Press"],
        "arms": ["Bicep Curl", "Tricep Pushdown", "Hammer Curl", "Skull Crusher", "Close Grip Bench"],
        "core": ["Plank", "Russian Twist", "Leg Raise", "Crunches", "Mountain Climber"]
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{AI_BASE_URL}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {AI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": AI_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a fitness expert. Give short, direct answers with just the exercise name."},
                        {"role": "user", "content": f"Suggest a different exercise to replace {exercise_name} that works the {muscle_group}. Keep it short."}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 30
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                suggestion = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                if suggestion and len(suggestion) < 40:
                    return suggestion.strip()
    except Exception as e:
        print(f"AI API error: {e}")
    
    options = fallbacks.get(muscle_group.lower(), ["Push Up", "Squat", "Plank"])
    valid_options = [o for o in options if o.lower() != exercise_name.lower()]
    if valid_options:
        return random.choice(valid_options)
    return exercise_name

@router.get("/")
async def get_routines(db: SessionDep, user: AuthDep):
    try:
        routines = db.exec(select(Routine).where(Routine.user_id == user.id)).all()
        result = []
        for r in routines:
            exercise_count = db.exec(select(RoutineExercise).where(RoutineExercise.routine_id == r.id)).all()
            result.append({
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "is_public": r.is_public,
                "is_favorite": r.is_favorite,
                "exercise_count": len(exercise_count)
            })
        return result
    except Exception as e:
        print(f"Error in get_routines: {e}")
        return []

@router.get("/public")
async def get_public_routines(db: SessionDep, user: AuthDep):
    try:
        routines = db.exec(select(Routine).where(Routine.is_public == True)).all()
        result = []
        for r in routines:
            owner = db.exec(select(User).where(User.id == r.user_id)).first()
            exercise_count = db.exec(select(RoutineExercise).where(RoutineExercise.routine_id == r.id)).all()
            result.append({
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "exercise_count": len(exercise_count),
                "username": owner.username if owner else "Unknown"
            })
        return result
    except Exception as e:
        print(f"Error in get_public_routines: {e}")
        return []

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
        print(f"Error in create_routine: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{routine_id}/remix")
async def remix_routine(db: SessionDep, user: AuthDep, routine_id: int):
    try:
        routine = db.exec(select(Routine).where(Routine.id == routine_id, Routine.user_id == user.id)).first()
        if not routine:
            raise HTTPException(status_code=404, detail="Routine not found")
        
        exercises = db.exec(select(RoutineExercise).where(RoutineExercise.routine_id == routine_id).order_by(RoutineExercise.order)).all()
        
        remixed_exercises = []
        
        for re in exercises:
            exercise = db.get(Exercise, re.exercise_id)
            if exercise:
                replacement_name = await get_ai_suggestion(exercise.name, exercise.muscle_group, exercise.equipment or "bodyweight")
                
                existing_replacement = db.exec(select(Exercise).where(Exercise.name == replacement_name)).first()
                if not existing_replacement:
                    existing_replacement = Exercise(
                        name=replacement_name,
                        muscle_group=exercise.muscle_group,
                        equipment=exercise.equipment,
                        form_tips=f"AI suggested alternative to {exercise.name}"
                    )
                    db.add(existing_replacement)
                    db.commit()
                    db.refresh(existing_replacement)
                
                remixed_exercises.append({
                    "original_id": exercise.id,
                    "original_name": exercise.name,
                    "replacement_id": existing_replacement.id,
                    "replacement_name": existing_replacement.name,
                    "sets": re.sets,
                    "reps": re.reps,
                    "rest_seconds": re.rest_seconds
                })
        
        new_routine = Routine(
            user_id=user.id,
            name=f"{routine.name} (AI Remix)",
            description=f"AI-generated remix of {routine.name} with alternative exercises",
            is_public=False
        )
        db.add(new_routine)
        db.commit()
        db.refresh(new_routine)
        
        for i, ex in enumerate(remixed_exercises):
            re = RoutineExercise(
                routine_id=new_routine.id,
                exercise_id=ex["replacement_id"],
                sets=ex["sets"],
                reps=ex["reps"],
                rest_seconds=ex["rest_seconds"],
                order=i
            )
            db.add(re)
        
        db.commit()
        
        return {
            "id": new_routine.id,
            "name": new_routine.name,
            "description": new_routine.description,
            "exercises": remixed_exercises
        }
    except Exception as e:
        print(f"Error in remix_routine: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{routine_id}")
async def delete_routine(db: SessionDep, user: AuthDep, routine_id: int):
    try:
        routine = db.exec(select(Routine).where(Routine.id == routine_id, Routine.user_id == user.id)).first()
        if not routine:
            raise HTTPException(status_code=404, detail="Routine not found")
        
        existing_exercises = db.exec(select(RoutineExercise).where(RoutineExercise.routine_id == routine_id)).all()
        for re in existing_exercises:
            db.delete(re)
        
        db.delete(routine)
        db.commit()
        return {"message": "Routine deleted"}
    except Exception as e:
        db.rollback()
        print(f"Error in delete_routine: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{routine_id}")
async def get_routine(db: SessionDep, user: AuthDep, routine_id: int):
    try:
        routine = db.exec(select(Routine).where(Routine.id == routine_id, Routine.user_id == user.id)).first()
        if not routine:
            raise HTTPException(status_code=404, detail="Routine not found")
        
        exercises = db.exec(select(RoutineExercise).where(RoutineExercise.routine_id == routine_id).order_by(RoutineExercise.order)).all()
        
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
    except Exception as e:
        print(f"Error in get_routine: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{routine_id}/workout-data")
async def get_workout_data(db: SessionDep, user: AuthDep, routine_id: int):
    try:
        routine = db.exec(select(Routine).where(Routine.id == routine_id, Routine.user_id == user.id)).first()
        if not routine:
            raise HTTPException(status_code=404, detail="Routine not found")
        
        exercises = db.exec(select(RoutineExercise).where(RoutineExercise.routine_id == routine_id).order_by(RoutineExercise.order)).all()
        
        exercise_list = []
        for re in exercises:
            exercise = db.get(Exercise, re.exercise_id)
            if exercise:
                exercise_list.append({
                    "id": exercise.id,
                    "name": exercise.name,
                    "sets": re.sets,
                    "reps": re.reps,
                    "rest_seconds": re.rest_seconds
                })
        
        return {
            "routine_name": routine.name,
            "exercises": exercise_list
        }
    except Exception as e:
        print(f"Error in get_workout_data: {e}")
        raise HTTPException(status_code=500, detail=str(e))