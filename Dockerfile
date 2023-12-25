# Use an official Python runtime as a parent image
FROM python:3.10 AS base
LABEL authors="deadly"

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r optional_requirements.txt

# Rename the configuration file
RUN mv config-example.json config.json
RUN mv secrets-example.toml secrets.toml

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV FLASK_APP=blueprints/__init__.py:create_app
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8000

# Run app.py when the container launches
CMD ["python", "-m", "flask", "run"]
