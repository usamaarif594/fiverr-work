# Diabetes Disease Prediction System

This README provides instructions on how to set up and run the Diabetes Disease Prediction System using Docker.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Docker Container Setup](#docker-container-setup)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)

## Features
- **Diabetes Prediction**: Predicts if a person has diabetes based on input features.


## Installation

### Prerequisites
- Docker (download and install from [Docker Installation Guide](https://docs.docker.com/get-docker/))

### Set Up Your Project
1. Clone or create a directory containing your app files:
    - `app.py` (Streamlit application)
    - `saved_models/` (folder containing machine learning models)
    - `requirements.txt` (file listing the Python dependencies)
    - `Dockerfile` (Docker configuration)

### Dockerfile
Create a `Dockerfile` in your project directory with the following content:

```dockerfile
# Use a lightweight Python image
FROM python:3.10-slim

# Copy your project files into the Docker image
COPY . /sapp

# Set the working directory to /app
WORKDIR /sapp

# Install all required Python packages
RUN pip install -r requirements.txt

# Expose port 80 to the outside world
EXPOSE 80

# Create necessary directories for Streamlit
RUN mkdir ~/.streamlit
RUN cp config.toml ~/.streamlit/config.toml
RUN cp credentials.toml ~/.streamlit/credentials.toml

# Set the default command to run the app with Streamlit
ENTRYPOINT ["streamlit", "run"]

# Set the default app to app.py
CMD ["app.py"]

# Build the Docker Image

docker build -t disease-prediction-app .
# run docker container
docker run -p 80:80 disease-prediction-app

# Access the Application/
Open your web browser and go to http://127.0.0.1:80 or  http://0.0.0.0:80 to access the app.

# Stop the Container
# To stop the running container, first find the container ID
docker ps

# Then stop it with
docker stop <container_id>

# (Optional) Push Docker Image to Docker Hub
docker login
# Tag and push your image:
docker tag disease-prediction-app your-dockerhub-username/disease-prediction-app
docker push your-dockerhub-username/disease-prediction-app

# Running the App on Any Machine
docker pull your-dockerhub-username/disease-prediction-app
docker run -p 8501:80 your-dockerhub-username/disease-prediction-app

# Project Structure

.
├── Dockerfile                # Dockerfile to build the container
├── app.py                    # Main Streamlit app
├── requirements.txt          # Python dependencies
├── saved_models/             # Pre-trained machine learning models
│   ├── diabetes_model.sav
├── config.toml               # Streamlit configuration file
├── credentials.toml          # Streamlit credentials file
└── README.md                 # Project documentation


