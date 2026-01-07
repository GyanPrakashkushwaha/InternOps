#### intiate servers with these commands

1. uvicorn app.app:app --reload
2. redis-server
3. celery -A app.tasks.celery_app worker --loglevel=info