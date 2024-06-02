from sqlalchemy.orm import Session
from src import models
from src.schemas import CreateUpdateProject


def create_one_project(db: Session, project: CreateUpdateProject):
    db_project = models.Project(name=project.name, description=project.description)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_all_projects(db: Session):
    return db.query(models.Project).all()


def get_project_info(db: Session, project_id: int):
    return (
        db.query(models.Project).filter(models.Project.project_id == project_id).first()
    )


def update_project_info(db: Session, project_id: int, project: CreateUpdateProject):
    project_to_update = (
        db.query(models.Project).filter(models.Project.project_id == project_id).first()
    )
    if project_to_update:
        project_to_update.name = project.name
        project_to_update.description = project.description
        db.commit()
        db.refresh(project_to_update)
    return project_to_update


def delete_specific_project(db: Session, project_id: int):
    project_to_delete = (
        db.query(models.Project).filter(models.Project.project_id == project_id).first()
    )
    if project_to_delete is None:
        return None
    db.delete(project_to_delete)
    db.commit()
    return project_to_delete
