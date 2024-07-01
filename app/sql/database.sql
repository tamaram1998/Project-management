-- Create table 'users'
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(100) NOT NULL
);

-- Create table 'projects'
CREATE TABLE projects (
    project_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id INT REFERENCES users(id)
);

-- Create table 'project_participants'
CREATE TABLE project_participants (
    id SERIAL PRIMARY KEY,
    project_id INT REFERENCES projects(project_id) ON DELETE CASCADE,
    user_id INT REFERENCES users(id)
);

-- Create table 'documents'
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    project_id INT REFERENCES projects(project_id) ON DELETE CASCADE,
    filename VARCHAR(100) NOT NULL,
    file_url VARCHAR(100) NOT NULL
);