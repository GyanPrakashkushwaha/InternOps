
### 🛠️ Prerequisites

Before you start, make sure you are in your project root folder and have installed your dependencies locally:

```bash
# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install the dependencies
pip install -r requirements.txt

```

---

### 💻 Terminal 1: The Database (PostgreSQL)

Instead of installing Postgres on your Windows/Mac/Linux system (which is messy), we will use Docker just to run the database server.

Run this command to start a Postgres container that listens on your **localhost port 5432**:

```bash
docker run --name debug-postgres --rm -it -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=internops postgres:15-alpine

```

* **What this does:** It spins up Postgres and maps it to your machine's port. The logs will show here.
* **Note:** If you stop this, the data disappears (because we didn't add a volume). That is usually fine for debugging.

---

### 📮 Terminal 2: The Broker (Redis)

Similarly, we need Redis running so Celery can talk to it.

```bash
docker run --name debug-redis --rm -it -p 6379:6379 redis:7-alpine

```

* **What this does:** Starts Redis on **localhost port 6379**.

---

### 👷 Terminal 3: The Worker (Celery)

Now we run your actual Python code. This worker will connect to the Redis and Postgres we just started (because your code defaults to `localhost` now!).

Make sure you are in the project root folder.

```bash
# Linux / Mac
celery -A app.tasks.celery_app worker --loglevel=info

# Windows (Celery sometimes freezes on Windows, use 'solo' pool)
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo

```

---

### 🌐 Terminal 4: The Web App (FastAPI)

Finally, run your API server with "hot reload" enabled.

```bash
uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload

```

---
