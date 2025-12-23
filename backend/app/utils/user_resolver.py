from sqlalchemy.orm import Session
from app.database.models import User

def resolve_user(db: Session, pic_name: str) -> User:
    clean_name = pic_name.strip().upper()

    user = (
        db.query(User)
        .filter(User.name == clean_name)
        .first()
    )

    if not user:
        user = User(name=clean_name)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user
