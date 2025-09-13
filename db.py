# db.py
import pymysql

# ==========================
# Database Connection Config
# ==========================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",        # change to your MySQL username
    "password": "root", # change to your MySQL password
    "database": "workspace_reservation",
    "cursorclass": pymysql.cursors.DictCursor
}

# ==========================
# Connection Function
# ==========================
def get_connection():
    """Create and return a database connection."""
    return pymysql.connect(**DB_CONFIG)

# ==========================
# Query Helpers
# ==========================
def fetch_all(query, params=None):
    """Fetch all rows from a SELECT query."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    finally:
        conn.close()

def fetch_one(query, params=None):
    """Fetch a single row from a SELECT query."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()
    finally:
        conn.close()

def execute(query, params=None):
    """Execute INSERT, UPDATE, DELETE queries."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
        conn.commit()
        return True
    except Exception as e:
        print(f"Database error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def execute_return_id(query, params=None):
    """Execute INSERT and return last inserted ID."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Database error: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()
