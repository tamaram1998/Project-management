from pydantic import BaseModel, field_validator
from typing import Optional


class Project(BaseModel):
    id: int
    name: str
    description: Optional[str] = None


class CreateUpdateProject(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator('name')
    def name_must_not_be_empty(cls, value):
        if not value or value.strip() == '':
            raise ValueError('name must not be an empty string')
        return value
