#### intiate servers with these commands
-- Move the the "/mnt/d/GyanPrakashKuswaha/GenAI/InternOps" directory then activate virtual environment " source .venv/bin/activate"

1. uvicorn app.app:app --reload
2. redis-server
3. celery -A app.tasks.celery_app worker --loglevel=info