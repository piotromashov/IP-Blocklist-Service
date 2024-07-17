# Use a lightweight Python image
FROM python:3.8-alpine

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the application files
COPY ./app /app

# Command to run the script
CMD ["python", "main.py"]
