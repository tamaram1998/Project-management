from fastapi import FastAPI, HTTPException, status, Depends
from typing_extensions import List
from sqlalchemy.orm import Session
from src.schemas import Project, CreateUpdateProject
from src import models, crud
from src.database import engine, get_db


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Create a new project endpoint


@app.post("/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(project: CreateUpdateProject, db: Session = Depends(get_db)):
    return crud.create_one_project(db=db, project=project)


# Get all projects endpoint
@app.get("/projects", response_model=List[Project], status_code=status.HTTP_200_OK)
async def list_all_projects(db: Session = Depends(get_db)):
    return crud.get_all_projects(db=db)


# Get all projects specific details
@app.get(
    "/project/{project_id}/info", response_model=Project, status_code=status.HTTP_200_OK
)
def get_project_details(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.get_project_info(project_id=project_id, db=db)
    if db_project is None:
        raise HTTPException(
            status_code=404, detail=f"Project with ID {project_id} not found"
        )
    return db_project


# Update a project endpoint
@app.put(
    "/project/{project_id}/info",
    response_model=Project,
    status_code=status.HTTP_202_ACCEPTED,
)
def update_project_details(
    project_id: int, project: CreateUpdateProject, db: Session = Depends(get_db)
):
    db_project = crud.update_project_info(db=db, project=project, project_id=project_id)
    if db_project is None:
        raise HTTPException(
            status_code=404, detail=f"Project with ID {project_id} not found"
        )
    return db_project


# Delete a project endpoint
@app.delete("/project/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.delete_specific_project(project_id=project_id, db=db)
    if db_project is None:
        raise HTTPException(
            status_code=404, detail=f"Project with ID {project_id} not found"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
