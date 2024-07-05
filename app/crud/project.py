from sqlalchemy.orm import Session
from sqlalchemy import text


from app.schemas import CreateUpdateProject
from app.models import Document, Project, ProjectParticipant


# Create project with ownership
def create_project_with_owner(db: Session, project: CreateUpdateProject, owner_id: int):
    db_project = Project(
        name=project.name, description=project.description, owner_id=owner_id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


# List of projects with access
def get_all_projects_with_access(user_id: int, db: Session):
    # projects where the user is the owner
    owner_projects = db.query(Project).filter(Project.owner_id == user_id).all()
    # projects where the user is a participant
    participant_projects = (
        db.query(Project)
        .join(ProjectParticipant)
        .filter(ProjectParticipant.user_id == user_id)
        .all()
    )
    projects_with_access = owner_projects + participant_projects

    return projects_with_access


# List of projects info + documentation
def projects_info_with_docs(user_id: int, db: Session):
    projects_with_access = get_all_projects_with_access(user_id, db)
    projects_details_with_docs = []
    for project in projects_with_access:
        docs = (
            db.query(Document).filter(Document.project_id == project.project_id).all()
        )
        project_info = {
            "id": project.project_id,
            "name": project.name,
            "description": project.description,
            "documents": [{"filename": doc.filename} for doc in docs],
        }
        projects_details_with_docs.append(project_info)

    return projects_details_with_docs


# Get project by id with access
def get_project_by_id_with_access(project_id: int, user_id, db: Session):
    # Check if the user is the owner of the project
    owner_project = (
        db.query(Project)
        .filter(Project.owner_id == user_id, Project.project_id == project_id)
        .first()
    )
    if owner_project:
        return owner_project
    # Check if the user is a participant in the project
    participant_project = (
        db.query(Project)
        .join(ProjectParticipant)
        .filter(ProjectParticipant.user_id == user_id, Project.project_id == project_id)
        .first()
    )
    return participant_project


# Get specific project details
def get_project_info(project_id, user_id: int, db: Session):
    # project where the user has access
    project = get_project_by_id_with_access(project_id, user_id, db)
    # find the specific project
    if not project:
        return None
    return project


# Project with specified id
def get_project_by_id(db: Session, project_id: int):
    return db.query(Project).filter(Project.project_id == project_id).first()


# Update specific project details
def update_project_info(
    db: Session, project_id: int, project: CreateUpdateProject, user_id: int
):
    # TODO: Same as above
    project_to_update = get_project_by_id_with_access(project_id, user_id, db)
    if project_to_update:
        project_to_update.name = project.name
        project_to_update.description = project.description
        db.commit()
        db.refresh(project_to_update)
        return project_to_update
    return None


# Delete specific project from all tables
def delete_specific_project(db: Session, project_id: int, user_id: int):

    owner_project = (
        db.query(Project)
        .filter(Project.owner_id == user_id, Project.project_id == project_id)
        .first()
    )
    if not owner_project:
        return None

    # delete the project from the database
    db.delete(owner_project)
    db.commit()
    return owner_project
