#!/bin/bash

# 1. Start Celery Worker in the background
# The '&' at the end runs it as a background process so the script continues
celery -A app.tasks.celery_app worker --loglevel=info &

# 2. Start FastAPI server in the foreground
# This keeps the container alive and listening on the port Render expects
uvicorn app.app:app --host 0.0.0.0 --port 8000