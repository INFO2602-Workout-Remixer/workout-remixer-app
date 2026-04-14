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
    from app.models.user import User
    from app.utilities.security import encrypt_password
    from sqlmodel import select
    
    with next(get_session()) as session:
        # ALWAYS create Bob user if not exists (this runs every time)
        existing_bob = session.exec(select(User).where(User.username == "bob")).first()
        if not existing_bob:
            bob = User(
                username="bob",
                email="bob@liftlab.com",
                password=encrypt_password("bobpass"),
                role="regular_user"
            )
            session.add(bob)
            session.commit()
            print("✅ Created test user: bob / bobpass")
        else:
            print("✅ Test user bob already exists")
        
        # Only seed exercises if none exist
        existing_count = session.exec(select(Exercise)).all()
        if len(existing_count) > 0:
            print(f"Database already has {len(existing_count)} exercises, skipping exercise seed")
            return
        
        exercises = [
            # Chest
            {"name": "Bench Press", "muscle_group": "chest", "equipment": "barbell", "youtube_url": "https://www.youtube.com/watch?v=gRVjAtPp0Ew", "form_tips": "Keep back arched, lower bar to mid-chest"},
            {"name": "Incline Dumbbell Press", "muscle_group": "chest", "equipment": "dumbbell", "youtube_url": "https://www.youtube.com/watch?v=4TYg2gffrZ4", "form_tips": "Set bench to 30-45 degrees"},
            {"name": "Push Up", "muscle_group": "chest", "equipment": "bodyweight", "youtube_url": "https://www.youtube.com/watch?v=IODxDxX7oi4", "form_tips": "Keep body straight, lower chest to ground"},
            {"name": "Squat", "muscle_group": "legs", "equipment": "barbell", "youtube_url": "https://www.youtube.com/watch?v=aclHkVu9f1I", "form_tips": "Go below parallel, keep chest up"},
            {"name": "Deadlift", "muscle_group": "back", "equipment": "barbell", "youtube_url": "https://www.youtube.com/watch?v=1ZXobu7JcKE", "form_tips": "Keep back flat, drive through heels"},
            {"name": "Pull Up", "muscle_group": "back", "equipment": "bodyweight", "youtube_url": "https://www.youtube.com/watch?v=eGo4IYlbE5g", "form_tips": "Use full range of motion"},
            {"name": "Overhead Press", "muscle_group": "shoulders", "equipment": "barbell", "youtube_url": "https://www.youtube.com/watch?v=2yjwXTZQDDI", "form_tips": "Keep core tight, don't lean back"},
            {"name": "Barbell Row", "muscle_group": "back", "equipment": "barbell", "youtube_url": "https://www.youtube.com/watch?v=9lEF8QyV7Ks", "form_tips": "Keep back straight, pull to lower chest"},
            {"name": "Bicep Curls", "muscle_group": "arms", "equipment": "dumbbell", "youtube_url": "https://www.youtube.com/watch?v=ykJmrZ5v0Oo", "form_tips": "Keep elbows tucked, don't swing"},
            {"name": "Tricep Pushdown", "muscle_group": "arms", "equipment": "cable", "youtube_url": "https://www.youtube.com/watch?v=2-LAMcpzODU", "form_tips": "Keep elbows locked at sides"},
            {"name": "Plank", "muscle_group": "core", "equipment": "bodyweight", "youtube_url": "https://www.youtube.com/watch?v=pSHjTRCQxIw", "form_tips": "Keep body straight, squeeze glutes"},
            {"name": "Leg Press", "muscle_group": "legs", "equipment": "machine", "youtube_url": "https://www.youtube.com/watch?v=IZxyjW7MPJQ", "form_tips": "Keep lower back pressed against pad"},
            {"name": "Lat Pulldown", "muscle_group": "back", "equipment": "cable", "youtube_url": "https://www.youtube.com/watch?v=CAwf7n6Luuc", "form_tips": "Lean back slightly, pull to upper chest"},
            {"name": "Lunges", "muscle_group": "legs", "equipment": "bodyweight", "youtube_url": "https://www.youtube.com/watch?v=QOVaHwm-Q6U", "form_tips": "Keep front knee behind toes"},
            {"name": "Face Pulls", "muscle_group": "shoulders", "equipment": "cable", "youtube_url": "https://www.youtube.com/watch?v=V8dZ2DNw_ZM", "form_tips": "Pull to face, squeeze shoulder blades"},
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