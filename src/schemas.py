from pydantic import BaseModel, field_validator


class Project(BaseModel):
    project_id: int
    name: str
    description: str


class CreateUpdateProject(BaseModel):
    name: str
    description: str

    @field_validator("name")
    def name_must_not_be_empty(cls, value):
        if not value or value.strip() == "":
            raise ValueError("name must not be an empty string")
        return value
