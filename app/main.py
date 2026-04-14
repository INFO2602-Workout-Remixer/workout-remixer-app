import uvicorn
from fastapi import FastAPI, Request, status
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from app.routers import templates, static_files, router, api_router
from app.config import get_settings
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database import create_db_and_tables
    create_db_and_tables()
    await seed_database()
    yield


async def seed_database():
    from app.database import get_session
    from app.models.exercise import Exercise
    from sqlmodel import select
    
    with next(get_session()) as session:
        existing_count = session.exec(select(Exercise)).all()
        if len(existing_count) > 0:
            print(f"Database already has {len(existing_count)} exercises, skipping seed")
            return
        
        exercises = [
            # Chest
            {"name": "Bench Press", "muscle_group": "chest", "equipment": "barbell", "youtube_url": "https://www.youtube.com/watch?v=4Y2ZdHCOXok", "form_tips": "Keep back arched, lower bar to mid-chest"},
            {"name": "Incline Dumbbell Press", "muscle_group": "chest", "equipment": "dumbbell", "youtube_url": "https://www.youtube.com/watch?v=4TYg2gffrZ4", "form_tips": "Set bench to 30-45 degrees"},
            {"name": "Decline Press", "muscle_group": "chest", "equipment": "barbell", "form_tips": "Lower bar to lower chest"},
            {"name": "Push Up", "muscle_group": "chest", "equipment": "bodyweight", "youtube_url": "https://www.youtube.com/watch?v=IODxDxX7oi4", "form_tips": "Keep body straight, lower chest to ground"},
            {"name": "Chest Fly", "muscle_group": "chest", "equipment": "dumbbell", "youtube_url": "https://www.youtube.com/watch?v=eozdVDA78K0", "form_tips": "Slight bend in elbows, hug a tree motion"},
            {"name": "Cable Crossover", "muscle_group": "chest", "equipment": "cable", "youtube_url": "https://www.youtube.com/watch?v=taI4XduLpTk", "form_tips": "Lean forward slightly, cross hands at bottom"},
            
            # Back
            {"name": "Pull Up", "muscle_group": "back", "equipment": "bodyweight", "youtube_url": "https://www.youtube.com/watch?v=eGo4IYlbE5g", "form_tips": "Use full range of motion"},
            {"name": "Lat Pulldown", "muscle_group": "back", "equipment": "cable", "youtube_url": "https://www.youtube.com/watch?v=CAwf7n6Luuc", "form_tips": "Lean back slightly, pull to upper chest"},
            {"name": "Barbell Row", "muscle_group": "back", "equipment": "barbell", "youtube_url": "https://www.youtube.com/watch?v=9lEF8QyV7Ks", "form_tips": "Keep back straight, pull to lower chest"},
            {"name": "Seated Cable Row", "muscle_group": "back", "equipment": "cable", "youtube_url": "https://www.youtube.com/watch?v=GZbfZ033f74", "form_tips": "Squeeze shoulder blades together"},
            {"name": "T-Bar Row", "muscle_group": "back", "equipment": "machine", "form_tips": "Keep chest supported, pull to chest"},
            {"name": "Deadlift", "muscle_group": "back", "equipment": "barbell", "youtube_url": "https://www.youtube.com/watch?v=1ZXobu7JcKE", "form_tips": "Keep back flat, drive through heels"},
            
            # Legs
            {"name": "Squat", "muscle_group": "legs", "equipment": "barbell", "youtube_url": "https://www.youtube.com/watch?v=aclHkVu9f1I", "form_tips": "Go below parallel, keep chest up"},
            {"name": "Front Squat", "muscle_group": "legs", "equipment": "barbell", "youtube_url": "https://www.youtube.com/watch?v=uYdzGp-Cjt0", "form_tips": "Keep elbows high, chest up"},
            {"name": "Leg Press", "muscle_group": "legs", "equipment": "machine", "youtube_url": "https://www.youtube.com/watch?v=IZxyjW7MPJQ", "form_tips": "Keep lower back pressed against pad"},
            {"name": "Lunges", "muscle_group": "legs", "equipment": "bodyweight", "youtube_url": "https://www.youtube.com/watch?v=QOVaHwm-Q6U", "form_tips": "Keep front knee behind toes"},
            {"name": "Romanian Deadlift", "muscle_group": "legs", "equipment": "barbell", "youtube_url": "https://www.youtube.com/watch?v=JCXUYuzwNrM", "form_tips": "Keep slight bend in knees, push hips back"},
            {"name": "Leg Extension", "muscle_group": "legs", "equipment": "machine", "youtube_url": "https://www.youtube.com/watch?v=YyvSfVjQeL0", "form_tips": "Control the movement, squeeze at top"},
            {"name": "Hamstring Curl", "muscle_group": "legs", "equipment": "machine", "youtube_url": "https://www.youtube.com/watch?v=1Tq3QdYUuHs", "form_tips": "Keep hips pressed into pad"},
            {"name": "Calf Raises", "muscle_group": "legs", "equipment": "bodyweight", "youtube_url": "https://www.youtube.com/watch?v=_-ZMiDZupEU", "form_tips": "Full range of motion, hold at top"},
            
            # Shoulders
            {"name": "Overhead Press", "muscle_group": "shoulders", "equipment": "barbell", "youtube_url": "https://www.youtube.com/watch?v=2yjwXTZQDDI", "form_tips": "Keep core tight, don't lean back"},
            {"name": "Arnold Press", "muscle_group": "shoulders", "equipment": "dumbbell", "youtube_url": "https://www.youtube.com/watch?v=3ml7BH7mNvg", "form_tips": "Rotate palms outward as you press"},
            {"name": "Lateral Raises", "muscle_group": "shoulders", "equipment": "dumbbell", "youtube_url": "https://www.youtube.com/watch?v=3VcKaXpzqRo", "form_tips": "Slight bend in elbows, raise to shoulder height"},
            {"name": "Front Raises", "muscle_group": "shoulders", "equipment": "dumbbell", "youtube_url": "https://www.youtube.com/watch?v=-t7fuZ0KhDA", "form_tips": "Keep arms straight, raise to shoulder height"},
            {"name": "Face Pulls", "muscle_group": "shoulders", "equipment": "cable", "youtube_url": "https://www.youtube.com/watch?v=V8dZ2DNw_ZM", "form_tips": "Pull to face, squeeze shoulder blades"},
            {"name": "Upright Rows", "muscle_group": "shoulders", "equipment": "barbell", "youtube_url": "https://www.youtube.com/watch?v=amYJhqW0O_Q", "form_tips": "Keep bar close to body, elbows high"},
            
            # Arms
            {"name": "Bicep Curls", "muscle_group": "arms", "equipment": "dumbbell", "youtube_url": "https://www.youtube.com/watch?v=ykJmrZ5v0Oo", "form_tips": "Keep elbows tucked, don't swing"},
            {"name": "Hammer Curls", "muscle_group": "arms", "equipment": "dumbbell", "youtube_url": "https://www.youtube.com/watch?v=zC3nLlEvin4", "form_tips": "Palms facing each other throughout"},
            {"name": "Preacher Curls", "muscle_group": "arms", "equipment": "barbell", "youtube_url": "https://www.youtube.com/watch?v=eyL9T8XZ2VU", "form_tips": "Keep arms on pad, full range of motion"},
            {"name": "Tricep Pushdown", "muscle_group": "arms", "equipment": "cable", "youtube_url": "https://www.youtube.com/watch?v=2-LAMcpzODU", "form_tips": "Keep elbows locked at sides"},
            {"name": "Skull Crushers", "muscle_group": "arms", "equipment": "EZ bar", "youtube_url": "https://www.youtube.com/watch?v=d_KZxkY_0cM", "form_tips": "Lower to forehead, keep elbows in"},
            {"name": "Tricep Dips", "muscle_group": "arms", "equipment": "bodyweight", "youtube_url": "https://www.youtube.com/watch?v=0326dy_-CzM", "form_tips": "Keep shoulders down, elbows tucked"},
            {"name": "Close Grip Bench", "muscle_group": "arms", "equipment": "barbell", "youtube_url": "https://www.youtube.com/watch?v=nEF0bv2fgR4", "form_tips": "Hands shoulder width apart"},
            
            # Core
            {"name": "Plank", "muscle_group": "core", "equipment": "bodyweight", "youtube_url": "https://www.youtube.com/watch?v=pSHjTRCQxIw", "form_tips": "Keep body straight, squeeze glutes"},
            {"name": "Russian Twists", "muscle_group": "core", "equipment": "bodyweight", "youtube_url": "https://www.youtube.com/watch?v=wkD8rjkodUI", "form_tips": "Keep feet up, twist side to side"},
            {"name": "Leg Raises", "muscle_group": "core", "equipment": "bodyweight", "youtube_url": "https://www.youtube.com/watch?v=l4kQd9eWclE", "form_tips": "Keep lower back pressed down"},
            {"name": "Crunches", "muscle_group": "core", "equipment": "bodyweight", "youtube_url": "https://www.youtube.com/watch?v=Xyd_fa5zoEU", "form_tips": "Lift shoulder blades, not neck"},
            {"name": "Hanging Leg Raises", "muscle_group": "core", "equipment": "bodyweight", "youtube_url": "https://www.youtube.com/watch?v=JB2oyawG9KI", "form_tips": "Keep legs straight, control the movement"},
            {"name": "Ab Wheel Rollout", "muscle_group": "core", "equipment": "wheel", "youtube_url": "https://www.youtube.com/watch?v=Chy7jT8j8g4", "form_tips": "Keep back rounded, extend fully"},
        ]
        
        for ex_data in exercises:
            exercise = Exercise(**ex_data)
            session.add(exercise)
        
        session.commit()
        print(f"✅ Added {len(exercises)} exercises to database")


app = FastAPI(middleware=[
    Middleware(SessionMiddleware, secret_key=get_settings().secret_key)
],
    lifespan=lifespan
)   

app.include_router(router)
app.include_router(api_router)
app.mount("/static", static_files, name="static")

@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def unauthorized_redirect_handler(request: Request, exc: Exception):
    return templates.TemplateResponse(
        request=request, 
        name="401.html",
    )

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=get_settings().app_host, port=get_settings().app_port, reload=get_settings().env.lower()!="production")