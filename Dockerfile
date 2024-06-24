FROM python:3.9

#Set working directory
WORKDIR /app

# Copy the Pipfile and Pipfile.lock
COPY dependencies/Pipfile dependencies/Pipfile.lock ./

# Install pipenv
RUN pip install pipenv

# Install dependencies
RUN pipenv install --deploy --ignore-pipfile

#Copy of the local dir to the working dir
COPY . .

ENV PYTHONPATH=/app


ENTRYPOINT ["pipenv", "run"]

#Cmd to run app within the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]