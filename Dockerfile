# Use an official Python runtime as a parent image
FROM python:3.12.2-slim-bullseye

# Set the working directory
WORKDIR /app


COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run Django
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "EmergencyBackend.wsgi:application"]

