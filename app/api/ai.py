from fastapi import APIRouter
from app.dependencies import SessionDep, AuthDep
from app.models.routine import Routine
from app.models.exercise import Exercise
from app.models.routine_exercise import RoutineExercise
from sqlmodel import select
import httpx

router = APIRouter(prefix="/ai", tags=["AI"])

AI_API_KEY = "sk-59addf63a8bd464c92242421db666aa1"
AI_BASE_URL = "https://ai-gen.sundaebytesett.com"
AI_MODEL = "meta/llama-3.2-3b-instruct"

@router.post("/ask")
async def ask_ai(db: SessionDep, user: AuthDep, request: dict):
    question = request.get("question", "")
    
    if not question:
        return {"answer": "Please ask a question about fitness or workouts."}
    
    prompt = f"""You are a fitness expert AI assistant. Answer the following question about fitness, exercise, or working out. Keep your answer helpful, safe, and under 150 words.

Question: {question}

Answer:"""
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{AI_BASE_URL}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {AI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": AI_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a fitness expert AI assistant. Give helpful, safe advice about exercise and workouts."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 300
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return {"answer": answer.strip()}
            else:
                return {"answer": get_fallback_answer(question)}
    except Exception as e:
        print(f"AI API error: {e}")
        return {"answer": get_fallback_answer(question)}

@router.post("/generate-workout")
async def generate_workout(db: SessionDep, user: AuthDep, request: dict):
    goal = request.get("goal", "build muscle")
    equipment = request.get("equipment", "bodyweight")
    
    prompt = f"""Create a workout routine for someone who wants to {goal} using {equipment}. 
Return ONLY 5-7 exercise names separated by commas. Example format: "Push Up, Squat, Pull Up, Lunge, Plank"
Do not add any other text."""
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{AI_BASE_URL}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {AI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": AI_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a personal trainer creating workout routines. Give short, comma-separated exercise names only."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 100
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                exercises_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                exercise_names = [e.strip() for e in exercises_text.split(',') if e.strip()]
                
                routine = Routine(
                    user_id=user.id,
                    name=f"AI {goal.capitalize()} Workout",
                    description=f"AI-generated workout for {goal} using {equipment}",
                    is_public=False
                )
                db.add(routine)
                db.commit()
                db.refresh(routine)
                
                for order, ex_name in enumerate(exercise_names[:7]):
                    existing_exercise = db.exec(select(Exercise).where(Exercise.name == ex_name)).first()
                    if not existing_exercise:
                        existing_exercise = Exercise(
                            name=ex_name,
                            muscle_group="full_body",
                            equipment=equipment,
                            form_tips=f"AI suggested exercise for {goal}"
                        )
                        db.add(existing_exercise)
                        db.commit()
                        db.refresh(existing_exercise)
                    
                    re = RoutineExercise(
                        routine_id=routine.id,
                        exercise_id=existing_exercise.id,
                        sets=3,
                        reps=10,
                        rest_seconds=60,
                        order=order
                    )
                    db.add(re)
                
                db.commit()
                return {"routine_name": routine.name, "exercises": exercise_names}
    except Exception as e:
        print(f"AI API error: {e}")
    
    fallback_exercises = ["Push Up", "Squat", "Pull Up", "Lunge", "Plank"]
    routine = Routine(
        user_id=user.id,
        name=f"AI {goal.capitalize()} Workout",
        description=f"AI-generated workout for {goal} using {equipment}",
        is_public=False
    )
    db.add(routine)
    db.commit()
    db.refresh(routine)
    
    for order, ex_name in enumerate(fallback_exercises):
        existing_exercise = db.exec(select(Exercise).where(Exercise.name == ex_name)).first()
        if existing_exercise:
            re = RoutineExercise(
                routine_id=routine.id,
                exercise_id=existing_exercise.id,
                sets=3,
                reps=10,
                rest_seconds=60,
                order=order
            )
            db.add(re)
    
    db.commit()
    return {"routine_name": routine.name, "exercises": fallback_exercises}

def get_fallback_answer(question):
    question_lower = question.lower()
    
    if "chest" in question_lower:
        return "For chest workouts, try: Bench Press, Push Ups, Incline Dumbbell Press, Chest Flys, and Cable Crossovers. Aim for 3-4 sets of 8-12 reps."
    elif "back" in question_lower:
        return "For back workouts, try: Pull Ups, Lat Pulldowns, Barbell Rows, Seated Cable Rows, and Deadlifts. Focus on squeezing your shoulder blades together."
    elif "leg" in question_lower or "squat" in question_lower:
        return "For leg workouts, try: Squats, Lunges, Leg Press, Romanian Deadlifts, and Calf Raises. Always maintain proper form to protect your knees and lower back."
    elif "shoulder" in question_lower:
        return "For shoulder workouts, try: Overhead Press, Lateral Raises, Front Raises, Face Pulls, and Arnold Press. Keep your core tight and don't use momentum."
    elif "arm" in question_lower or "bicep" in question_lower or "tricep" in question_lower:
        return "For arm workouts, try: Bicep Curls, Hammer Curls, Tricep Pushdowns, Skull Crushers, and Close Grip Bench Press. Control the movement on the way down."
    elif "core" in question_lower or "ab" in question_lower:
        return "For core workouts, try: Planks, Russian Twists, Leg Raises, Crunches, and Hanging Leg Raises. Engage your core throughout each movement."
    elif "form" in question_lower or "technique" in question_lower:
        return "Proper form is crucial! Keep your back straight, engage your core, control the movement (don't use momentum), and breathe properly. Consider recording yourself to check form."
    else:
        return "Great question! For general fitness, focus on compound exercises (squats, deadlifts, bench press, overhead press, rows), progressive overload (gradually increase weight/reps), and consistency. Always warm up before workouts and cool down after. Rest 48 hours between training the same muscle groups."