"""
Database Tier for Request Tracker (v2 Architecture)
Handles SQLite database connection, lightweight table schema initialization,
real-time dynamic elapsed-time calculation for Days Open, and parameter-bound CRUD SQL queries.
Strictly decoupled from HTTP networking and UI presentation layers.
"""

import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requests.db")

# Strict operational status workflow sequence as mandated
STATUS_OPTIONS = ["Unassigned", "In-Progress", "On-Hold", "Pending", "Resolved", "Closed", "Rejected"]


def get_db_connection():
    """Returns an active connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"[Database Tier Error] Connection failed: {e}")
        return None


def init_db():
    """Lightweight initialization of the SQLite database schema without repetitive seeding or test runtime overhead."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL,
                    createdAt TEXT NOT NULL,
                    daysSinceCreated INTEGER DEFAULT 0
                )
            """)
        return True
    except Exception as e:
        print(f"[Database Tier Error] Failed to initialize schema: {e}")
        return False
    finally:
        conn.close()


def insert_request_db(title, description, status, created_at):
    """Inserts a new request entry into the 'requests' table and returns the primary key ID."""
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            with conn:
                cursor = conn.cursor()
                # Default status of a newly created issue must be Unassigned
                st_clean = status.strip().title()
                if st_clean in ["Approved", "approved"]:
                    st_clean = "Resolved"
                if st_clean not in STATUS_OPTIONS:
                    st_clean = "Unassigned"
                cursor.execute(
                    """
                    INSERT INTO requests (title, description, status, createdAt, daysSinceCreated)
                    VALUES (?, ?, ?, ?, 0)
                    """,
                    (title.strip(), description.strip(), st_clean, str(created_at))
                )
                return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"[Database Tier Error] Failed to insert request record: {e}")
        return None
    except Exception as e:
        print(f"[Database Tier Error] Unexpected fault during insertion: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_all_requests_db():
    """
    Dynamically calculates Days Open for all records strictly from createdAt timestamps,
    and returns all entries sorted strictly newest first (ordered chronologically descending).
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            # Retrieve all records sorted newest first by createdAt timestamp descending
            cursor.execute("SELECT id, title, description, status, createdAt, daysSinceCreated FROM requests ORDER BY datetime(createdAt) DESC, id DESC")
            rows = cursor.fetchall()
            
            now_time = datetime.now()
            results = []
            updates_to_run = []
            
            for row in rows:
                r = dict(row)
                try:
                    dt_created = datetime.strptime(str(r["createdAt"]), "%Y-%m-%d %H:%M:%S")
                    computed_days = max(0, (now_time - dt_created).days)
                    r["daysSinceCreated"] = computed_days
                    if str(r.get("status")).strip().title() in ["Approved", "approved"]:
                        r["status"] = "Resolved"
                    if computed_days != row["daysSinceCreated"] or r["status"] != row["status"]:
                        updates_to_run.append((computed_days, r["status"], r["id"]))
                except Exception:
                    pass
                results.append(r)
                
            # Asynchronous-safe bulk update of elapsed days if any deviations occurred
            if updates_to_run:
                try:
                    with conn:
                        cursor.executemany("UPDATE requests SET daysSinceCreated = ?, status = ? WHERE id = ?", updates_to_run)
                except Exception:
                    pass
                    
            return results
    except sqlite3.Error as e:
        print(f"[Database Tier Error] Failed to fetch request records: {e}")
        return []
    except Exception as e:
        print(f"[Database Tier Error] Unexpected fault during fetch operation: {e}")
        return []
    finally:
        if conn:
            conn.close()
    return []


def update_request_status_db(req_id, new_status):
    """Updates the status field of a specific request ID in SQLite from any value to any other valid workflow state."""
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            with conn:
                cursor = conn.cursor()
                st_clean = new_status.strip().title()
                if st_clean in ["Approved", "approved"]:
                    st_clean = "Resolved"
                cursor.execute(
                    "UPDATE requests SET status = ? WHERE id = ?",
                    (st_clean, int(req_id))
                )
                return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"[Database Tier Error] Failed to update request status: {e}")
        return False
    except Exception as e:
        print(f"[Database Tier Error] Unexpected fault during status update: {e}")
        return False
    finally:
        if conn:
            conn.close()

