#### intiate servers with these commands
-- Move the the "/mnt/d/GyanPrakashKuswaha/GenAI/InternOps" directory then activate virtual environment " source .venv/bin/activate"

1. uvicorn app.app:app --reload
2. redis-server
3. celery -A app.tasks.celery_app worker --loglevel=info


## Docker

- Build the docker image
`docker build -t {name of image(app name)}:{version} {location of docker file}`
` docker build -t py-app:1.0.0 ./app `

- port binding
`docker run -d -p {host port}:{container port}`
`docker run -d -p 8000:30`

## learn
```
FROM node:19-alpine

COPY requirments.txt /app/
COPY app /app/

WORKDIR /app

RUN npm install

CMD ["node", "app.py"]
```