
### 1. The "Daily Driver" Commands

These are the commands you'll use 90% of the time to start and stop your work.

* **Start everything (and see logs):**
```bash
docker-compose up

```


* *What it does:* Creates containers (if they don't exist) and starts them. It locks your terminal to show you the logs.
* *Note:* Press `Ctrl + C` to stop.


* **Start everything (in background/detached mode):**
```bash
docker-compose up -d

```


* *What it does:* Starts everything in the background and gives you your terminal back immediately.


* **Stop and remove containers:**
```bash
docker-compose down

```


* *What it does:* Gracefully stops the containers and removes them. Your database data stays safe because of the "volume" we defined.


* **Rebuild after changing requirements:**
```bash
docker-compose up --build

```


* *Why use it:* If you change `requirements.txt` or `Dockerfile`, standard `docker-compose up` won't notice. This forces Docker to rebuild the image.



---

### 2. Debugging & Logs

When something goes wrong, you need to see what's happening inside.

* **View logs for all services (follow mode):**
```bash
docker-compose logs -f

```


* `-f` means "follow" (keep streaming live updates).


* **View logs for a specific service:**
```bash
docker-compose logs -f web
docker-compose logs -f worker

```


* *Use case:* Your API is working, but the background task failed? Check only the `worker` logs.



---

### 3. "Going Inside" the Containers

Sometimes you need to enter the container to run scripts or check files manually.

* **Open a shell inside your Web container:**
```bash
docker-compose exec web bash

```


* *What it does:* It's like SSH-ing into the container. You are now "inside" the Linux environment of your app.
* *Try this:* Once inside, type `ls -la` to see your files or `python` to open a Python shell.
* *Exit:* Type `exit` to leave.



---

### 4. Database Interaction (PostgreSQL)

Since you can't access the database file directly on your laptop easily, you use the container tools.

* **Connect to the Database CLI:**
```bash
docker-compose exec -it db(docker image name) psql -U postgres -d internops

```


* *Breakdown:*
* `exec db`: Execute a command inside the `db` service.
* `psql`: The PostgreSQL command-line tool.
* `-U postgres`: Login as user "postgres".
* `-d internops`: Connect to the "internops" database.




* **SQL Commands to try (once inside):**
```sql
\dt                       -- List all tables
SELECT * FROM analysis_results; -- See your resume analysis data
\q                        -- Quit/Exit

```



---

### 5. Redis Interaction

Want to see if your tasks are actually getting queued?

* **Connect to Redis CLI:**
```bash
docker-compose exec redis redis-cli

```


* **Redis Commands to try:**
```bash
PING        # Should reply "PONG"
KEYS * # Show all keys (cache, celery tasks, etc.)
FLUSHALL    # DANGER: Clears the entire cache/queue (Good for resetting)
exit        # Quit

```



---

### 6. Cleanup (The Janitor)

Docker images take up space. Occasionally, you want to clean up unused junk.

* **Clean up unused Docker objects:**
```bash
docker system prune

```


* *Warning:* This deletes stopped containers and unused networks. It asks for confirmation.
