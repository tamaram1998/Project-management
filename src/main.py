from fastapi import FastAPI, HTTPException, status
from typing import List, Dict

from src.pydantic_models import Project, CreateUpdateProject

app = FastAPI()

# In-memory storage
projects_db: Dict[int, Project] = {}


# Create a new project endpoint
@app.post("/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(project: CreateUpdateProject):
    next_id = max(projects_db.keys(), default=0) + 1
    new_project = Project(id=next_id, name=project.name, description=project.description)
    projects_db[next_id] = new_project

    return new_project


# Get all projects endpoint
@app.get("/projects", response_model=List[Project], status_code=status.HTTP_200_OK)
def get_all_projects():
    return projects_db.values()


# Get all projects specific details
@app.get("/project/{project_id}/info", response_model=Project, status_code=status.HTTP_200_OK)
def get_project_details(project_id: int):
    # If no project is found with the given ID, raise a 404 HTTPException
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")

    return projects_db[project_id]


# Update specific project details endpoint
@app.put("/project/{project_id}/info", response_model=Project, status_code=status.HTTP_202_ACCEPTED)
def update_project_details(project_id: int, updated_project: CreateUpdateProject):
    # Check if the project with the given ID exists
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")
    # Retrieve the project from the database
    project = projects_db[project_id]
    # Update project details based on the provided project_update
    project.name = updated_project.name
    project.description = updated_project.description

    return project


# Delete a project endpoint
@app.delete("/project/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")

    del projects_db[project_id]
    return {"message": "Project deleted successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
