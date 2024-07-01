from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ProjectParticipant(Base):
    __tablename__ = "project_participants"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id"))

    # relationships
    project = relationship("Project", back_populates="project_participants")
    user = relationship("User", back_populates="user_projects")


class Project(Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # relationships
    owner = relationship("User", back_populates="projects")
    participants = relationship(
        "User",
        secondary="project_participants",
        back_populates="projects",
        viewonly=True,
    )
    project_participants = relationship(
        "ProjectParticipant",
        back_populates="project",
        cascade="all, delete, delete-orphan",
    )
    documents = relationship(
        "Document", back_populates="project", cascade="all, delete, delete-orphan"
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)

    # relationships
    projects = relationship(
        "Project",
        secondary="project_participants",
        back_populates="participants",
        viewonly=True,
    )
    user_projects = relationship("ProjectParticipant", back_populates="user")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id", ondelete="CASCADE"))
    file_url = Column(String, index=True)
    filename = Column(String, index=True)

    project = relationship("Project", back_populates="documents")
