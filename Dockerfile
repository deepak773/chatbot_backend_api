# Use the official Python image as a base
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the app directory and other files into the container
COPY ./app /app/app
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables (for Cloud Run compatibility)
ENV PORT=8080
ENV PYTHONPATH=/app

# Expose the Cloud Run port
EXPOSE 8080

# Run the FastAPI app using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
