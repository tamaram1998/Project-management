from fastapi import (
    HTTPException,
    status,
    Depends,
    UploadFile,
    Response,
    APIRouter,
)
from sqlalchemy.orm import Session
from typing_extensions import List

# import boto3
# from botocore.exceptions import ClientError
from app.auth.jwt_handler import get_current_user
from app.database import get_db
from app.schemas import DocumentResponse
from app.models import User
from app.crud.project import get_project_by_id_with_access
from app.crud.documents import (
    has_access_to_document,
    upload_docs,
    update_project_document,
    get_project_documents,
    get_document,
    delete_project_document
)

router = APIRouter()


# List all document for the project
@router.get(
    "/project/{project_id}/documents",
    response_model=List[DocumentResponse],
    status_code=status.HTTP_200_OK,
    tags=["Document Methods"],
)
async def list_all_project_document(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    documents = await get_project_documents(
        user_id=current_user.id, project_id=project_id, db=db
    )
    if documents is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No documents found for this project",
        )
    return documents


# Upload a document endpoint
@router.post(
    "/project/{project_id}/documents/",
    response_model=None,
    status_code=status.HTTP_200_OK,
    tags=["Document Methods"],
)
async def upload_documents(
    project_id: int,
    files: List[UploadFile],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    has_access = get_project_by_id_with_access(project_id, current_user.id, db=db)
    if has_access is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this project",
        )
    db_project = await upload_docs(db=db, project_id=project_id, files=files)
    for file in files:
        if file.filename in files:
            raise HTTPException(
                status_code=403,
                detail="You have already uploaded file with the same name",
            )
    if db_project is None:
        raise HTTPException(
            status_code=404,
            detail="You don't have permission to upload the file on this project",
        )
    return db_project


# Download a document
@router.get(
    "/document/{document_id}", status_code=status.HTTP_200_OK, tags=["Document Methods"]
)
async def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.crud.documents import download_project_document

    has_access = has_access_to_document(document_id, current_user.id, db=db)
    if has_access is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this document",
        )
    document = get_document(document_id, db=db)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    document_content, error_msg = download_project_document(document=document)
    if error_msg:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_msg)
    file_name = document.file_url.split("/")[-1]
    return Response(
        content=document_content,
        headers={
            "Content-Disposition": f"attachment; filename={file_name}",
            "Content-Type": "application/octet-stream",
        },
    )


# Update document endpoint
@router.put(
    "/document/{document_id}", status_code=status.HTTP_200_OK, tags=["Document Methods"]
)
async def update_file_content(
    document_id: int,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    has_access = has_access_to_document(document_id, current_user.id, db=db)
    if has_access is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this document",
        )
    # check if document exists
    existing_document = get_document(document_id, db=db)
    if existing_document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    # update document content
    error_msg = await update_project_document(document=existing_document, file=file)
    if error_msg:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_msg)

    return {"message": "File content updated successfully"}


# Delete document endpoint
@router.delete(
    "/document/{document_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Document Methods"],
)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    has_access = has_access_to_document(document_id, current_user.id, db=db)
    if has_access is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this document",
        )
    document = get_document(document_id, db=db)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    error_msg = await delete_project_document(document=document, db=db)
    if error_msg:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_msg)
    return {"message": "Document successfully deleted"}
