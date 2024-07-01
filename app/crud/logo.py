from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from PIL import Image
import io
from urllib.parse import urlparse
from io import BytesIO
import boto3
import os
from botocore.exceptions import ClientError
import logging

from app.crud.documents import s3
from app.models import Project
from app.crud.project import get_project_by_id_with_access

BUCKET_NAME = os.getenv("LOGO_BUCKET_NAME")

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION"),
)


def allowed_file_extension(logo_file):
    return (
        "." in logo_file and logo_file.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


async def upload_to_s3(user_id: int, db: Session, project_id: int, logo: UploadFile):
    try:
        # read the image
        content = await logo.read()

        # create the s3 key and upload the image
        s3_key = f"{project_id}/{logo.filename}"
        s3.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=content)
        logo_url = f"https://{BUCKET_NAME}." f"s3.{BUCKET_NAME}.amazonaws.com/{s3_key}"
        project = get_project_by_id_with_access(project_id, user_id, db)
        project.logo_url = logo_url
        db.commit()
    except Exception:
        raise HTTPException(status_code=500, detail="Logo not uploaded successfully")
    return {"message": "Logo uploaded successfully"}


def get_project_logo_url(db: Session, project_id: int, user_id: int):
    project = get_project_by_id_with_access(project_id, user_id, db)
    if not project:
        raise HTTPException(status_code=500, detail="Project not found")
    if not project.logo_url:
        raise HTTPException(status_code=500, detail="Logo not found")
    return project.logo_url


def download_logo_from_s3(logo_url: str, project_id: int):
    try:
        filename = logo_url.split("/")[-1]
        s3_key = f"{project_id}/{filename}"
        s3_object = s3.get_object(Bucket=BUCKET_NAME, Key=s3_key)
        logo_image = s3_object["Body"].read()

        return logo_image, None
    except ClientError as e:
        error_message = f"Failed to download document: {e.response['Error']['Message']}"
        return None, error_message


def delete_logo(project_id: int, db: Session):
    try:
        bucket_name = os.getenv("LOGO_BUCKET_NAME")
        project_prefix = f"{project_id}/"

        # list all files in the project folder
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=project_prefix)

        if "Contents" in response:
            objects_to_delete = [{"Key": obj["Key"]} for obj in response["Contents"]]

            if objects_to_delete:
                s3_client.delete_objects(
                    Bucket=bucket_name, Delete={"Objects": objects_to_delete}
                )

        project_entry = (
            db.query(Project).filter(Project.project_id == project_id).first()
        )
        if project_entry:
            project_entry.logo = None
            db.commit()

        return "Successfully deleted project logo"

    except ClientError as e:
        error_message = (
            f"Failed to delete logo from S3: {e.response['Error']['Message']}"
        )
        return error_message
