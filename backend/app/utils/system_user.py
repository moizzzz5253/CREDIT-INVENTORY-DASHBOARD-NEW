from app.database.models import User

def ensure_system_user(db):
    user = db.query(User).first()
    if not user:
        user = User(name="SYSTEM")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
