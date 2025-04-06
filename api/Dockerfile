 # Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables to prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure Python output is sent straight to terminal without buffering
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if needed (e.g., for mysql connector build)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*
# Often not needed for mysql-connector-python unless specific build issues arise

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable for the Flask app (optional, can be set in docker-compose)
# ENV FLASK_APP=app.py

# Run app.py when the container launches
# Use gunicorn for production later: CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
CMD ["python", "app.py"]
