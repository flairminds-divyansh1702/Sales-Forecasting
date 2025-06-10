# Use an official Python base image
FROM python:3.11
 
# Set the working directory
WORKDIR /app
 
# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy the FastAPI application
COPY . .
 
# Expose the FastAPI port
EXPOSE 8000
 
# Start the FastAPI app using Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]