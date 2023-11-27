# Use an official Python runtime as a parent image
FROM python:latest

# Install Required System Tools
RUN apt-get update

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Define the command to run your application
CMD [ "python", "app.py" ]