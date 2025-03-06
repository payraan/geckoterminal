FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Copy only requirements file first to leverage Docker cache
COPY requirements.txt .

# Install system dependencies and Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8089

# Use port 8089
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8089"]
