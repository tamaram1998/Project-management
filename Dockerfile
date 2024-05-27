FROM python:3.9

#Set working directory
WORKDIR /app

#Copy the dependencies to the work dir
COPY dependencies/requirements.txt .

#Install dependencies
RUN pip install -r requirements.txt

#Copy of the local dir to the working dir
COPY . .

ENV PYTHONPATH=/app

#Cmd to run app within the container
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]