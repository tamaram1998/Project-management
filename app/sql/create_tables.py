from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from src.database import Base, engine
import os


sql_file_path = "project_database.sql"

# create tables based on models
Base.metadata.create_all(bind=engine)

# open and execute script
with open(sql_file_path, 'r') as file:
    sql_commands = file.read()

# create a session and execute the script
session = Session(bind=engine)
session.execute(text(sql_commands))
session.commit()
session.close()
