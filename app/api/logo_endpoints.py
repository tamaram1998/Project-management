from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends,
    Response,
    status,
)
from sqlalchemy.orm import Session
from app.models import Project, User
from app.database import get_db
from app.auth.jwt_handler import get_current_user
from app.crud.logo import (
    upload_to_s3,
    allowed_file_extension,
    get_project_logo_url,
    delete_logo,
)
from app.crud.project import get_project_by_id_with_access

router = APIRouter()


# Upload logo endpoint
@router.put(
    "/project/{project_id}/logo",
    response_model=None,
    status_code=status.HTTP_200_OK,
    tags=["Logo Methods"],
)
async def upload_project_logo(
    project_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not allowed_file_extension(file.filename):
        raise HTTPException(
            status_code=400, detail="Only .jpg, .jpeg, and .png files are allowed"
        )

    project = get_project_by_id_with_access(project_id, current_user.id, db)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    image = await upload_to_s3(
        logo=file, project_id=project_id, db=db, user_id=current_user.id
    )

    return image


# Download logo endpoint
@router.get(
    "/project/{project_id}/logo", status_code=status.HTTP_200_OK, tags=["Logo Methods"]
)
async def download_project_logo(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.crud.logo import download_logo_from_s3

    logo_url = get_project_logo_url(db, project_id, current_user.id)

    logo_data, error_msg = download_logo_from_s3(logo_url, project_id)
    if error_msg:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_msg)
    filename = logo_url.split("/")[-1]
    return Response(
        content=logo_data,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "application/octet-stream",
        },
    )


# Delete logo endpoint
@router.delete(
    "/project/{project_id}/logo",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Logo Methods"],
)
async def delete_project_logo(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = get_project_by_id_with_access(project_id, user_id=current_user.id, db=db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this project",
        )
    if not project.logo_url:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Logo not found",
        )

    delete_logo(project_id=project_id, db=db)
    return {"message": "Logo deleted successfully"}
