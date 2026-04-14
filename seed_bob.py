from app.database import get_cli_session 
from app.models.user import User 
from app.utilities.security import encrypt_password 
from sqlmodel import select 
 
def create_bob(): 
    with get_cli_session() as session: 
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
            print("? Created test user: bob / bobpass") 
        else: 
            print("? Bob user already exists") 
 
if __name__ == "__main__": 
    create_bob() 
