import os
import sys

# Add backend to path to import models and database
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import SessionLocal
import models
import auth

def seed_data():
    db = SessionLocal()
    
    # Check if dummy user exists
    user = db.query(models.User).filter(models.User.email == "test@stylesync.com").first()
    if not user:
        print("Creating dummy user...")
        hashed_password = auth.get_password_hash("password123")
        user = models.User(
            email="test@stylesync.com",
            hashed_password=hashed_password,
            body_type="Average",
            preferences={"styles": ["casual", "minimalist"]}
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        print("Dummy user already exists.")

    print(f"Seed completed. User ID: {user.id}")
    db.close()

if __name__ == "__main__":
    seed_data()
