# Use an official Python runtime as a parent image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Set the working directory in the container
WORKDIR /app

# Copy the application files to the working directory
COPY ./app /app
COPY ./requirements.txt /app/requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
