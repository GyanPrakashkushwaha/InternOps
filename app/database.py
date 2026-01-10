
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

DB_CREATION_QUERY = """
            ALTER DATABASE internops SET TIMEZONE TO 'Asia/Kolkata';
            
            CREATE TABLE IF NOT EXISTS analysis (
                id INT PRIMARY KEY,
                hash_key TEXT NOT NULL,
                job_description TEXT,
                resume_text TEXT,
                mode TEXT, 
                created_at TIMESTAMPZ NOT NULL DEFAULT NOW()
            );
            
            
            
            
            CREATE TABLE 
        """

def get_db_connection():
    conn = None
    try:
        db_params = {
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "password"),
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5430"),
            "database": os.getenv("DB_NAME", "internops")
        }
        print(db_params)
        conn = psycopg2.connect(**db_params)
    except Exception as e:
        raise RuntimeError(f"DB connection failed: {e}")
    return conn

def init_db():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        if not conn:
            raise RuntimeError("Database connection is None")

        cur = conn.cursor()
        cur.execute()
        conn.commit()
    except Exception:
        raise
    finally:
        if cur: cur.close()
        if conn: conn.close()

# if __name__ == "__main__":
#     conn = get_db_connection()
#     cur = conn.cursor()
#     query = "SELECT * FROM me"
#     cur.execute(query)
#     print(cur.fetchall())
#     cur.close()
#     conn.close()