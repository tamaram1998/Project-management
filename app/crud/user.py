from sqlalchemy.orm import Session

from app.schemas import UsersCreate
from app.auth.jwt_handler import hash_pass
from app.models import User, ProjectParticipant


# Check if the user is only a participant
def is_only_participant(user_id: int, project_id: int, db: Session):
    participant_project = (
        db.query(ProjectParticipant)
        .filter(
            ProjectParticipant.project_id == project_id,
            ProjectParticipant.user_id == user_id,
        )
        .first()
    )
    if participant_project:
        return True


# Get user by login details
def get_user_by_username(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


# Create user
async def create_user_db(user: UsersCreate, db: Session):
    hashed_password = await hash_pass(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# check existing user with the same username
async def is_existing_user(email: str, db: Session):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return True


# Add participant to the project
def add_project_participant(db: Session, project_id: int, user_id: int):
    # Check if the user is already a participant in the project
    existing_participant = (
        db.query(ProjectParticipant)
        .filter_by(project_id=project_id, user_id=user_id)
        .first()
    )
    if existing_participant:
        return existing_participant
    participant = ProjectParticipant(project_id=project_id, user_id=user_id)
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant
