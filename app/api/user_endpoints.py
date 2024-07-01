from fastapi import (
    HTTPException,
    status,
    Depends,
    Request,
    APIRouter,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.jwt_handler import get_current_user, create_access_token, authenticate
from app.database import get_db
from app.schemas import UsersCreate, UserResponse, UsersLoginResponse
from app.models import User
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.crud.user import (
    is_existing_user,
    add_project_participant,
    get_user_by_username,
    create_user_db,
)
from app.crud.project import get_project_by_id

router = APIRouter()

# initialize the limiter
limiter = Limiter(key_func=get_remote_address)


# Create user (login, password, repeat password)
@router.post(
    "/auth",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["User Methods"],
)
async def create_user(user: UsersCreate, db: Session = Depends(get_db)):
    already_existing_username = await is_existing_user(user.username, db)
    if already_existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This username is already in use",
        )
    new_user = await create_user_db(user, db)
    return new_user


# Login endpoint
@router.post(
    "/login",
    response_model=UsersLoginResponse,
    status_code=status.HTTP_200_OK,
    tags=["User Methods"],
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    db_user = await authenticate(db, form_data.username, form_data.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = await create_access_token(db_user.username)
    return {"access_token": access_token, "token_type": "bearer"}


# Invite a user to a project as a participant
@router.post(
    "/projects/{project_id}/invite",
    response_model=None,
    status_code=status.HTTP_200_OK,
    tags=["User Methods"],
)
async def invite_user_to_project(
    project_id: int,
    user_login: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # check if current user is the owner of the project
    project = get_project_by_id(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can invite participants",
        )

    # fetch the user by their login
    user_to_invite = get_user_by_username(db, username=user_login)
    if not user_to_invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if user_to_invite.username == current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are the owner of the project, "
            "you cannot be added as participant",
        )
    try:
        add_project_participant(db=db, project_id=project_id, user_id=user_to_invite.id)
        return {
            "message": f"User {user_to_invite.username} has been invited to the project"
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
