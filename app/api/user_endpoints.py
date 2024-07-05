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
    create_user_db,
)


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
    already_existing_username = await is_existing_user(user.email, db)
    if already_existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This email is already in use",
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
            detail="Incorrect email or password",
        )
    access_token = await create_access_token(db_user.email)
    return {"access_token": access_token, "token_type": "bearer"}
