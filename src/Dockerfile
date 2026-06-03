# 1. Use a lightweight official Python image as a base
FROM python:3.11-slim

# 2. Configure critical environment variables for Python within containers
# Prevent Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Prevent Python from buffering logs, allowing you to see errors in Cloud Logging immediately.
ENV PYTHONUNBUFFERED=1

# 3. Install operating system dependencies (Required if you are using SQL Server or specific drivers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Set the working directory inside the container
WORKDIR /app

# 5. First, copy only the requirements file
# This takes advantage of Docker's layer caching; if you don't change the libraries, they aren't reinstalled on every build.
COPY src/requirements.txt .

# 6. Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 7. Copy all the project source code to the container
COPY . .

# 8. Expose the default port used by Cloud Run (8080)
EXPOSE 8080

# 9. API execution command using Uvicorn
# The PORT environment variable (required by GCP) is used and bound to 0.0.0.0
CMD ["sh", "-c", "uvicorn src.transactionality.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
