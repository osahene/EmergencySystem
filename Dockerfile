# Use an official Python runtime as a parent image
FROM python:3.12.2-slim-bullseye

# Install required system dependencies for WeasyPrint
RUN apt-get update && apt-get install -y \
    libpango1.0-dev \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libglib2.0-dev \
    libpango-1.0-0 \
    && apt-get clean

# Set the working directory
WORKDIR /app


COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run Django
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "EmergencyBackend.wsgi:application"]

