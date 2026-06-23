# Use a small, official Python base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements first (Docker caches this layer separately,
# so it won't reinstall boto3 every time you change main.py)
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application code
COPY app/ .

# Run the app when the container starts
CMD ["python", "main.py"]
