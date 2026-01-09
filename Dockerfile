
# 1. Base Image: Use an official lightweight Python runtime
# We use 'slim' to keep the image size small
FROM python:3.10-slim

# 2. Set Environment Variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to disc
# PYTHONUNBUFFERED: Ensures logs are flushed directly to the terminal (useful for debugging)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Install System Dependencies
# We need 'gcc' and 'libpq-dev' because we are using 'psycopg2' (PostgreSQL driver)
# It needs these to compile C extensions
# RUN apt-get update \
#     && apt-get install -y --no-install-recommends gcc libpq-dev \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# 5. Install Python Dependencies
# We copy requirements.txt first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the Application Code
# This copies everything from the current folder to /app inside the container
COPY . .

# 7. Default Command
# This command runs the FastAPI server by default. 
# We can override this later to run the Celery worker instead.
CMD [ "uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]

