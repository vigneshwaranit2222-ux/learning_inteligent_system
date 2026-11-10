import sys
import os

sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("."))

from app.core.database import SessionLocal, init_db
from app.services.normalization.seed_skills import seed_master_data
from app.core.security import hash_password
from app.models.user import User, Learner
from sqlalchemy import select

def main():
    print("Initializing DB...")
    init_db()
    
    db = SessionLocal()
    try:
        print("Seeding canonical skills and curriculum...")
        seed_master_data(db)

        # Seed default Admin and Demo Learner if not present
        admin_user = db.scalar(select(User).where(User.email == "admin@intelligence.system"))
        if not admin_user:
            admin_user = User(
                email="admin@intelligence.system",
                hashed_password=hash_password("AdminPass123!"),
                full_name="System Administrator",
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("Default admin created: admin@intelligence.system / AdminPass123!")

        demo_learner = db.scalar(select(User).where(User.email == "learner@intelligence.system"))
        if not demo_learner:
            demo_learner = User(
                email="learner@intelligence.system",
                hashed_password=hash_password("LearnerPass123!"),
                full_name="Alex Mercer",
                role="learner",
                is_active=True
            )
            db.add(demo_learner)
            db.flush()

            learner_profile = Learner(
                user_id=demo_learner.id,
                headline="Aspiring AI & Backend Engineer",
                bio="Passionate developer eager to build production intelligent software systems.",
                target_role="Senior AI Backend Engineer",
                years_of_experience=2.5,
                education_level="Bachelor of Science in Computer Science",
                github_url="https://github.com/alexmercer-demo",
                linkedin_url="https://linkedin.com/in/alexmercer-demo"
            )
            db.add(learner_profile)
            db.commit()
            print("Default demo learner created: learner@intelligence.system / LearnerPass123!")

    finally:
        db.close()

if __name__ == "__main__":
    main()
