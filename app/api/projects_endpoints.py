from fastapi import (
    HTTPException,
    status,
    Depends,
    APIRouter,
)
from sqlalchemy.orm import Session
from typing import List

from app.auth.jwt_handler import get_current_user
from app.database import get_db
from app.schemas import (
    CreateUpdateProject,
    ProjectDocumentInfo,
    ProjectResponse,
)
from app.models import User
from app.crud.project import (
    projects_info_with_docs,
    create_project_with_owner,
    update_project_info,
    delete_specific_project,
    get_project_by_id_with_access,
    get_project_by_id,
)
from app.crud.user import (
    is_only_participant,
    get_user_by_username,
    add_project_participant,
)

router = APIRouter()


# Create a new project endpoint
@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Project Methods"],
)
async def create_project(
    project: CreateUpdateProject,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # TODO: Add response model as project and return created project
    return create_project_with_owner(db=db, project=project, owner_id=current_user.id)


# Get all projects endpoint
@router.get(
    "/projects",
    response_model=List[ProjectDocumentInfo],
    status_code=status.HTTP_200_OK,
    tags=["Project Methods"],
)
async def list_all_projects(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return projects_info_with_docs(user_id=current_user.id, db=db)


# Get project specific details endpoint
@router.get(
    "/project/{project_id}/info",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    tags=["Project Methods"],
)
def get_project_details(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_project = get_project_by_id_with_access(
        db=db, project_id=project_id, user_id=current_user.id
    )
    if db_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )
    return db_project


# Update a project endpoint
@router.put(
    "/project/{project_id}/info",
    response_model=CreateUpdateProject,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Project Methods"],
)
def update_project_details(
    project_id: int,
    project: CreateUpdateProject,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_project = update_project_info(
        db=db, project=project, project_id=project_id, user_id=current_user.id
    )
    if db_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )
    return db_project


# Delete a project endpoint
@router.delete(
    "/project/{project_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Project Methods"],
)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delete = delete_specific_project(db, project_id, current_user.id)
    if is_only_participant(user_id=current_user.id, project_id=project_id, db=db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are participant of this project, cannot delete",
        )
    if delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )
    return {"message": "You have successfully deleted project!"}


# Invite a user to a project as a participant
@router.post(
    "/projects/{project_id}/invite",
    response_model=None,
    status_code=status.HTTP_200_OK,
    tags=["Project Methods"],
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
    user_to_invite = get_user_by_username(db, email=user_login)
    if not user_to_invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if user_to_invite.email == current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are the owner of the project, "
            "you cannot be added as participant",
        )
    try:
        add_project_participant(db=db, project_id=project_id, user_id=user_to_invite.id)
        return {
            "message": f"User {user_to_invite.email} has been invited to the project"
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user_to_invite.email} hasn't been invited to the project",
        )
