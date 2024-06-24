from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)
from typing import List
import re


class CreateUpdateProject(BaseModel):
    name: str
    description: str

    @field_validator("name")
    def name_must_not_be_empty(cls, value):
        if not value or value.strip() == "":
            raise ValueError("name must not be an empty string")
        return value


class ProjectResponse(CreateUpdateProject):
    project_id: int
    owner_id: int


class Project(CreateUpdateProject):
    project_id: int


class DocumentFilename(BaseModel):
    filename: str


class ProjectDocumentInfo(BaseModel):
    id: int
    name: str
    description: str
    documents: List[DocumentFilename]


class UsersCreate(BaseModel):
    username: EmailStr = Field(default=None)
    password: str
    repeat_password: str

    @model_validator(mode="after")
    def validate_password(cls, values):
        password = values.password
        repeat_password = values.repeat_password

        if password != repeat_password:
            raise ValueError("Passwords don't match")

        if len(password) < 10:
            raise ValueError("Password must be at least 10 characters long")
        if len(password) > 100:
            raise ValueError("Password must be no more than 128 characters long")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError("Password must contain at least one special character")

        return values


class UserResponse(BaseModel):
    username: EmailStr
    hashed_password: str
    id: int


class UsersLogin(BaseModel):
    username: EmailStr = Field(default=None)
    password: str = Field(default=None)


class UsersLoginResponse(BaseModel):
    access_token: str
    token_type: str


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_url: str
