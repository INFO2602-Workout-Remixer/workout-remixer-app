from app.database import get_cli_session
from app.models import Exercise
from app.repositories.user import UserRepository
from app.utilities.security import encrypt_password
from sqlmodel import select

def seed_database():
    with get_cli_session() as session:
        user_repo = UserRepository(session)
        
        bob = user_repo.get_by_username("bob")
        
        if not bob:
            bob = user_repo.create({
                "username": "bob",
                "email": "bob@example.com",
                "password": encrypt_password("bobpass"),
                "role": "regular_user"
            })
            print("Created user: bob")
        
        exercises = [
            {"name": "Bench Press", "muscle_group": "chest", "equipment": "barbell"},
            {"name": "Squat", "muscle_group": "legs", "equipment": "barbell"},
            {"name": "Deadlift", "muscle_group": "back", "equipment": "barbell"},
            {"name": "Pull Up", "muscle_group": "back", "equipment": "bodyweight"},
            {"name": "Push Up", "muscle_group": "chest", "equipment": "bodyweight"},
            {"name": "Overhead Press", "muscle_group": "shoulders", "equipment": "barbell"},
            {"name": "Barbell Row", "muscle_group": "back", "equipment": "barbell"},
            {"name": "Lunges", "muscle_group": "legs", "equipment": "bodyweight"},
            {"name": "Plank", "muscle_group": "core", "equipment": "bodyweight"},
            {"name": "Bicep Curls", "muscle_group": "arms", "equipment": "dumbbell"},
        ]
        
        for ex_data in exercises:
            existing = session.exec(select(Exercise).where(Exercise.name == ex_data["name"])).first()
            if not existing:
                exercise = Exercise(**ex_data)
                session.add(exercise)
                print(f"Added exercise: {ex_data['name']}")
        
        session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()
