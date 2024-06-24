from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing_extensions import List
import boto3
from botocore.exceptions import ClientError
import os

from app.models import Document, Project, ProjectParticipant
from app.crud.project import get_project_by_id_with_access

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION"),
)


# Upload document/documents
async def upload_docs(db: Session, project_id: int, files: List[UploadFile]):
    # checking if projects exist
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    uploaded_files = []
    for file in files:
        content = await file.read()
        s3_key = f"{project_id}/{file.filename}"
        s3.put_object(Bucket=os.getenv("AWS_S3_BUCKET_NAME"), Key=s3_key, Body=content)
        file_url = (
            f"https://{os.getenv('AWS_S3_BUCKET_NAME')}."
            f"s3.{os.getenv('AWS_DEFAULT_REGION')}.amazonaws.com/{s3_key}"
        )
        filename = file_url.split("/")[-1]
        document = Document(project_id=project_id, file_url=file_url, filename=filename)
        db.add(document)
        uploaded_files.append(file_url)
    db.commit()
    return {"message": "Files uploaded successfully"}


# Get one specified document
def get_document(document_id: int, db: Session):
    document = db.query(Document).filter(Document.id == document_id).first()
    return document


# Check if user has access to document
def has_access_to_document(document_id: int, user_id: int, db: Session):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        return False
    # check if the user is the owner of the project
    if document.project.owner_id == user_id:
        return True
    # check if the user is a participant in the project
    project_participant = (
        db.query(ProjectParticipant)
        .filter(
            ProjectParticipant.project_id == document.project_id,
            ProjectParticipant.user_id == user_id,
        )
        .first()
    )
    if project_participant:
        return True
    return False


# Get all documents from one project
async def get_project_documents(project_id: int, user_id: int, db: Session):
    project = get_project_by_id_with_access(project_id, user_id, db)
    if project is None:
        return None
    if project.project_id == project_id:
        documents = db.query(Document).filter(Document.project_id == project_id).all()
        return documents


# Download document from bucket
def download_project_document(document: Document):
    try:
        s3_key = f"{document.project_id}/{document.file_url.split('/')[-1]}"
        response = s3.get_object(Bucket=os.getenv("AWS_S3_BUCKET_NAME"), Key=s3_key)
        document_content = response["Body"].read()
        return document_content, None
    except ClientError as e:
        error_message = f"Failed to download document: {e.response['Error']['Message']}"
        return None, error_message


# Update document from bucket
async def update_project_document(document: Document, file: UploadFile):
    try:
        s3_key = f"{document.project_id}/{file.filename}"
        try:
            s3.head_object(Bucket=os.getenv("AWS_S3_BUCKET_NAME"), Key=s3_key)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return f"File not found in S3: {s3_key}"

        # upload updated file
        s3.put_object(
            Bucket=os.getenv("AWS_S3_BUCKET_NAME"), Key=s3_key, Body=file.file
        )
        return {"message": "File content updated successfully"}

    except ClientError as e:
        error_message = f"Failed to update file content: {str(e)}"
        return error_message


# Delete document from bucket and corresponding project
async def delete_project_document(document: Document, db: Session):
    try:
        s3_key = f"{document.project_id}/{document.file_url.split('/')[-1]}"
        s3.delete_object(Bucket=os.getenv("AWS_S3_BUCKET_NAME"), Key=s3_key)
        db.delete(document)
        db.commit()
    except ClientError as e:
        error_message = f"Failed to download document: {e.response['Error']['Message']}"
        return error_message
