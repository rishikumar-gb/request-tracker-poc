"""
Real-Time Request Tracker & Dispatch Console
Full-Stack Application using Streamlit (Frontend), Python (Backend RESTful API), and SQLite (Database).
"""

import os
import time
import json
import sqlite3
import threading
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from http.server import BaseHTTPRequestHandler
try:
    from http.server import ThreadingHTTPServer as HTTPServerClass
except ImportError:
    from http.server import HTTPServer as HTTPServerClass

import streamlit as st

# =====================================================================
# CONFIGURATION & GLOBAL CONSTANTS
# =====================================================================

st.set_page_config(
    page_title="Real-Time Request Tracker",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requests.db")
STATUS_OPTIONS = ["pending", "approved", "rejected"]

# =====================================================================
# DATABASE TIER (SQLite Operations)
# =====================================================================

def get_db_connection():
    """Returns a connection to the SQLite database with robust error handling."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"[DB Error] Connection failed: {e}")
        return None

def init_db():
    """Initializes the SQLite database and creates the 'requests' table if it does not exist."""
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS requests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL,
                        status TEXT NOT NULL CHECK(status IN ('pending', 'approved', 'rejected')),
                        createdAt TEXT NOT NULL
                    )
                """)
            return True
    except sqlite3.Error as e:
        print(f"[DB Error] Failed to initialize table: {e}")
        return False
    except Exception as e:
        print(f"[DB Error] Unexpected error during init: {e}")
        return False
    finally:
        if conn:
            conn.close()

def insert_request_db(title, description, status, created_at):
    """Inserts a new request into the 'requests' table and returns the autoincremented ID."""
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO requests (title, description, status, createdAt)
                    VALUES (?, ?, ?, ?)
                    """,
                    (title.strip(), description.strip(), status, str(created_at))
                )
                return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"[DB Error] Failed to insert request: {e}")
        return None
    except Exception as e:
        print(f"[DB Error] Unexpected error during insertion: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_all_requests_db():
    """Retrieves all records from the 'requests' table ordered by latest first."""
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, description, status, createdAt FROM requests ORDER BY id DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error as e:
        print(f"[DB Error] Failed to fetch requests: {e}")
        return []
    except Exception as e:
        print(f"[DB Error] Unexpected error during fetch: {e}")
        return []
    finally:
        if conn:
            conn.close()
    return []

def update_request_status_db(req_id, new_status):
    """Updates the status attribute of a specific request ID."""
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE requests SET status = ? WHERE id = ?",
                    (new_status, int(req_id))
                )
                return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"[DB Error] Failed to update status: {e}")
        return False
    except Exception as e:
        print(f"[DB Error] Unexpected error during status update: {e}")
        return False
    finally:
        if conn:
            conn.close()

# =====================================================================
# BACKEND TIER (RESTful API Server & Request Handler)
# =====================================================================

class RequestTrackerRESTHandler(BaseHTTPRequestHandler):
    """Custom RESTful HTTP request handler supporting GET, POST, and PATCH endpoints."""

    def log_message(self, format, *args):
        # Silence routine console logging for clean UI output
        pass

    def send_json_response(self, status_code, data_dict):
        try:
            response_bytes = json.dumps(data_dict).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response_bytes)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            self.wfile.write(response_bytes)
        except Exception as e:
            print(f"[API Server Error] Failed to send HTTP response: {e}")

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_json_response(200, {"status": "ok"})

    def do_GET(self):
        """Handle GET endpoints, primarily retrieving all requests."""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            if parsed_path.path in ["/api/requests", "/api/requests/"]:
                data = get_all_requests_db()
                self.send_json_response(200, {"status": "success", "data": data, "count": len(data)})
            elif parsed_path.path == "/api/health":
                self.send_json_response(200, {"status": "healthy", "service": "Request Tracker API"})
            else:
                self.send_json_response(404, {"status": "error", "message": "REST endpoint not found."})
        except Exception as e:
            self.send_json_response(500, {"status": "error", "message": f"Internal server error: {e}"})

    def do_POST(self):
        """Handle POST endpoints for creating a new request."""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            if parsed_path.path in ["/api/requests", "/api/requests/"]:
                content_length = int(self.headers.get('Content-Length', 0))
                raw_body = self.rfile.read(content_length).decode('utf-8')
                payload = json.loads(raw_body) if raw_body else {}

                # Basic Data Validation
                title = str(payload.get("title", "")).strip()
                description = str(payload.get("description", "")).strip()
                status = str(payload.get("status", "pending")).strip().lower()

                if not title:
                    self.send_json_response(400, {"status": "error", "message": "Validation failed: Title cannot be empty."})
                    return
                if not description:
                    self.send_json_response(400, {"status": "error", "message": "Validation failed: Description cannot be empty."})
                    return
                if status not in STATUS_OPTIONS:
                    self.send_json_response(400, {"status": "error", "message": f"Validation failed: Status must be one of {STATUS_OPTIONS}."})
                    return

                # Timestamp generation using datetime library
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Insert into Database
                new_id = insert_request_db(title, description, status, created_at)
                if new_id is not None:
                    response_data = {
                        "status": "success",
                        "message": "Request created successfully via backend API.",
                        "data": {
                            "id": new_id,
                            "title": title,
                            "description": description,
                            "status": status,
                            "createdAt": created_at
                        }
                    }
                    self.send_json_response(201, response_data)
                else:
                    self.send_json_response(500, {"status": "error", "message": "Database insertion failure."})
            else:
                self.send_json_response(404, {"status": "error", "message": "Endpoint not found."})
        except json.JSONDecodeError:
            self.send_json_response(400, {"status": "error", "message": "Invalid JSON payload in POST body."})
        except Exception as e:
            self.send_json_response(500, {"status": "error", "message": f"Internal server error: {e}"})

    def do_PATCH(self):
        """Handle PATCH endpoints for updating request status dynamically."""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path_segments = [seg for seg in parsed_path.path.split("/") if seg]
            
            # Expected pattern: /api/requests/<id>
            if len(path_segments) >= 3 and path_segments[0] == "api" and path_segments[1] == "requests":
                try:
                    target_id = int(path_segments[2])
                except ValueError:
                    self.send_json_response(400, {"status": "error", "message": "Invalid ID format in URI parameter."})
                    return

                content_length = int(self.headers.get('Content-Length', 0))
                raw_body = self.rfile.read(content_length).decode('utf-8')
                payload = json.loads(raw_body) if raw_body else {}
                
                new_status = str(payload.get("status", "")).strip().lower()
                if new_status not in STATUS_OPTIONS:
                    self.send_json_response(400, {"status": "error", "message": f"Validation failed: Status must be one of {STATUS_OPTIONS}."})
                    return

                updated = update_request_status_db(target_id, new_status)
                if updated:
                    self.send_json_response(200, {"status": "success", "message": f"Status updated to '{new_status}' successfully."})
                else:
                    self.send_json_response(404, {"status": "error", "message": "Request ID not found or status already set."})
            else:
                self.send_json_response(404, {"status": "error", "message": "Endpoint not found."})
        except json.JSONDecodeError:
            self.send_json_response(400, {"status": "error", "message": "Invalid JSON payload."})
        except Exception as e:
            self.send_json_response(500, {"status": "error", "message": f"Internal server error: {e}"})


@st.cache_resource
def start_backend_api():
    """Starts the RESTful HTTP API server in a background daemon thread."""
    init_db()  # Initialize SQLite schema before serving API
    
    # Try binding to standard ports, fallback to ephemeral if needed
    for port in range(8000, 8020):
        try:
            server = HTTPServerClass(("0.0.0.0", port), RequestTrackerRESTHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            return f"http://localhost:{port}"
        except OSError:
            continue
        except Exception as e:
            print(f"[API Server Init Error on port {port}]: {e}")
            continue
            
    try:
        # Fallback dynamic OS port allocation
        server = HTTPServerClass(("0.0.0.0", 0), RequestTrackerRESTHandler)
        port = server.server_port
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return f"http://localhost:{port}"
    except Exception as e:
        st.error(f"Failed to start Backend REST API Server: {e}")
        return None

# =====================================================================
# API CLIENT WRAPPERS (Frontend to Backend Integration via REST)
# =====================================================================

def api_fetch_all_requests(base_url):
    """Fetches all request records from the REST API GET endpoint."""
    try:
        req = urllib.request.Request(f"{base_url}/api/requests", method="GET")
        with urllib.request.urlopen(req, timeout=5.0) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get("data", [])
    except Exception as e:
        st.error(f"API Communication Failure (GET /api/requests): {e}")
        return []

def api_submit_new_request(base_url, title, description, status):
    """Submits a new request via the REST API POST endpoint."""
    try:
        payload = json.dumps({
            "title": title,
            "description": description,
            "status": status
        }).encode("utf-8")
        
        req = urllib.request.Request(
            f"{base_url}/api/requests",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5.0) as response:
            result = json.loads(response.read().decode('utf-8'))
            return True, result.get("message", "Created successfully.")
    except urllib.error.HTTPError as err:
        try:
            err_details = json.loads(err.read().decode('utf-8'))
            return False, err_details.get("message", str(err))
        except Exception:
            return False, f"HTTP Error {err.code}: {err.reason}"
    except Exception as e:
        return False, f"API Communication Failure (POST /api/requests): {e}"

def api_update_request_status(base_url, request_id, new_status):
    """Updates request status via the REST API PATCH endpoint."""
    try:
        payload = json.dumps({"status": new_status}).encode("utf-8")
        req = urllib.request.Request(
            f"{base_url}/api/requests/{request_id}",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="PATCH"
        )
        with urllib.request.urlopen(req, timeout=5.0) as response:
            result = json.loads(response.read().decode('utf-8'))
            return True, result.get("message", "Updated successfully.")
    except urllib.error.HTTPError as err:
        try:
            err_details = json.loads(err.read().decode('utf-8'))
            return False, err_details.get("message", str(err))
        except Exception:
            return False, f"HTTP Error {err.code}: {err.reason}"
    except Exception as e:
        return False, f"API Communication Failure (PATCH /api/requests/{request_id}): {e}"

# =====================================================================
# FRONTEND UI (Streamlit Styling & Layout)
# =====================================================================

def inject_custom_styles():
    """Injects high-aesthetic CSS for modern typography, gradients, micro-animations, and mouse cursor overrides."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@400;500;600&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* Override Streamlit selectbox default text cursor (I-beam) to standard arrow pointer when hovering over dropdowns */
        div[data-testid="stSelectbox"],
        div[data-testid="stSelectbox"] *,
        div[data-baseweb="select"],
        div[data-baseweb="select"] *,
        div[data-baseweb="select"] input,
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] div,
        ul[data-baseweb="menu"],
        ul[data-baseweb="menu"] *,
        li[role="option"],
        li[role="option"] * {
            cursor: default !important;
        }
        
        .hero-banner {
            background: linear-gradient(135deg, #1E1B4B 0%, #312E81 40%, #4338CA 100%);
            padding: 2.2rem 2.5rem;
            border-radius: 16px;
            color: white;
            box-shadow: 0 10px 25px -5px rgba(67, 56, 202, 0.3);
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }
        
        .hero-title {
            font-family: 'Outfit', sans-serif;
            font-size: 2.4rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            color: #F8FAFC;
            letter-spacing: -0.02em;
        }
        
        .hero-subtitle {
            font-size: 1.05rem;
            color: #C7D2FE;
            max-width: 700px;
            line-height: 1.5;
            margin-bottom: 1.2rem;
        }
        
        .api-pill {
            display: inline-flex;
            align-items: center;
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid #34D399;
            color: #6EE7B7;
            padding: 5px 14px;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
            box-shadow: 0 0 15px rgba(52, 211, 153, 0.2);
        }
        
        .section-card-header {
            font-family: 'Outfit', sans-serif;
            font-size: 1.4rem;
            font-weight: 600;
            color: #0F172A;
            margin-top: 1.8rem;
            margin-bottom: 1.2rem;
            display: flex;
            align-items: center;
            border-bottom: 2px solid #E2E8F0;
            padding-bottom: 0.6rem;
        }
        
        /* Status Badges with subtle illumination */
        .badge {
            display: inline-block;
            padding: 5px 14px;
            border-radius: 9999px;
            font-size: 0.82rem;
            font-weight: 600;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            transition: all 0.2s ease;
        }
        .badge-pending {
            background-color: #FEF3C7;
            color: #B45309;
            border: 1px solid #FDE68A;
        }
        .badge-approved {
            background-color: #D1FAE5;
            color: #047857;
            border: 1px solid #A7F3D0;
        }
        .badge-rejected {
            background-color: #FEE2E2;
            color: #B91C1C;
            border: 1px solid #FECACA;
        }
        
        .kpi-card {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            padding: 1.2rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
        }
        .kpi-num {
            font-family: 'Outfit', sans-serif;
            font-size: 2.2rem;
            font-weight: 700;
            color: #1E293B;
            margin: 0;
        }
        .kpi-label {
            font-size: 0.88rem;
            color: #64748B;
            font-weight: 500;
            text-transform: uppercase;
            margin-top: 4px;
        }
        </style>
    """, unsafe_allow_html=True)

def render_badge(status):
    status_clean = status.lower().strip()
    if status_clean == "pending":
        return '<span class="badge badge-pending">Pending</span>'
    elif status_clean == "approved":
        return '<span class="badge badge-approved">Approved</span>'
    elif status_clean == "rejected":
        return '<span class="badge badge-rejected">Rejected</span>'
    return f"<span>{status}</span>"

def main():
    try:
        inject_custom_styles()
        
        # Initialize and start background REST API server
        api_base_url = start_backend_api()
        if not api_base_url:
            st.error("Critical Service Error: Unable to launch background RESTful API server.")
            return

        # Top Hero Header
        st.markdown(f"""
            <div class="hero-banner">
                <div class="hero-title">Real-Time Request Tracker & Dispatch Console</div>
                <div class="hero-subtitle">
                    Full-Stack Proof of Concept integrated with Streamlit Frontend, Python RESTful HTTP API Backend, 
                    and SQLite Persistent Database Tier.
                </div>
                <div class="api-pill">REST API Server Active & Online at {api_base_url}</div>
            </div>
        """, unsafe_allow_html=True)

        # =====================================================================
        # SECTION 1: USER INPUT FORM
        # =====================================================================
        st.markdown('<div class="section-card-header">Section 1: Submit a New Request or Query</div>', unsafe_allow_html=True)

        with st.form(key="request_submission_form", clear_on_submit=True):
            col1, col2 = st.columns([1.2, 2.8], gap="large")
            
            with col1:
                st.markdown("#### **System Attributes**")
                # Showing ID and createdAt as requested in the form fields specification
                st.text_input(
                    "Request ID (autoincrement)", 
                    value="[Auto-generated by SQLite]", 
                    disabled=True, 
                    help="The unique primary key ID is autoincremented directly by the SQLite database upon successful API insertion."
                )
                
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.text_input(
                    "createdAt (Timestamp)", 
                    value=f"{current_timestamp} (Captured Now)", 
                    disabled=True, 
                    help="Captured dynamically using Python's datetime library during POST request processing."
                )
                
                form_status = st.selectbox(
                    "Status (Initial State)", 
                    options=STATUS_OPTIONS, 
                    index=0,
                    help="Select the starting status of your request."
                )
                
            with col2:
                st.markdown("#### **Request Details**")
                form_title = st.text_input("Title of the Request *", placeholder="e.g., Hardware Access Request, API Endpoint Provisioning...")
                form_desc = st.text_area("Detailed Description *", placeholder="Provide explicit background details, justifications, or technical query requirements...", height=172)

            submit_btn = st.form_submit_button("Transmit Request via REST API", use_container_width=True)

        if submit_btn:
            # Basic client-side data validation before API dispatch
            if not form_title or not form_title.strip():
                st.warning("Validation Failed: Please enter a valid Title for the request.")
            elif not form_desc or not form_desc.strip():
                st.warning("Validation Failed: Please enter a detailed Description.")
            else:
                with st.spinner("Dispatching payload to REST API endpoint..."):
                    success, msg = api_submit_new_request(
                        api_base_url, 
                        title=form_title, 
                        description=form_desc, 
                        status=form_status
                    )
                if success:
                    st.success(f"Success! Request titled '{form_title.strip()}' processed by backend API and stored in SQLite!")
                    time.sleep(0.6)
                    st.rerun()
                else:
                    st.error(f"Backend Error: {msg}")

        # =====================================================================
        # SECTION 2: CONSOLIDATED DASHBOARD & TABLE VIEW
        # =====================================================================
        st.markdown('<div class="section-card-header">Section 2: Consolidated Real-Time Dashboard</div>', unsafe_allow_html=True)

        # Fetch live data via backend API
        requests_data = api_fetch_all_requests(api_base_url)

        # Executive KPI Cards
        total_count = len(requests_data)
        pending_count = sum(1 for r in requests_data if r["status"] == "pending")
        approved_count = sum(1 for r in requests_data if r["status"] == "approved")
        rejected_count = sum(1 for r in requests_data if r["status"] == "rejected")

        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        with kpi_col1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-num">{total_count}</div><div class="kpi-label">Total Recorded</div></div>', unsafe_allow_html=True)
        with kpi_col2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-num" style="color:#D97706;">{pending_count}</div><div class="kpi-label">Pending</div></div>', unsafe_allow_html=True)
        with kpi_col3:
            st.markdown(f'<div class="kpi-card"><div class="kpi-num" style="color:#059669;">{approved_count}</div><div class="kpi-label">Approved</div></div>', unsafe_allow_html=True)
        with kpi_col4:
            st.markdown(f'<div class="kpi-card"><div class="kpi-num" style="color:#DC2626;">{rejected_count}</div><div class="kpi-label">Rejected</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if not requests_data:
            st.info("Dashboard Empty: No requests found in the database. Use the submission form above to transmit your first entry!")
            return

        # Organized View: Tabs grouped by current status as specified in the prompt
        tab_all, tab_pending, tab_approved, tab_rejected = st.tabs([
            f"All Requests (Grouped by Status)",
            f"Pending ({pending_count})",
            f"Approved ({approved_count})",
            f"Rejected ({rejected_count})"
        ])

        def render_request_rows(data_subset, tab_key):
            if not data_subset:
                st.caption("No request entries available in this category.")
                return

            # Table Header
            c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 2.5, 3.5, 2.2, 1.8, 2.2, 1.3])
            with c1: st.markdown("**ID**")
            with c2: st.markdown("**Title**")
            with c3: st.markdown("**Description**")
            with c4: st.markdown("**createdAt**")
            with c5: st.markdown("**Status Badge**")
            with c6: st.markdown("**Change Status**")
            with c7: st.markdown("**Action**")

            st.markdown("<hr style='margin: 6px 0px; border: 0; border-top: 2px solid #CBD5E1;'/>", unsafe_allow_html=True)

            for req in data_subset:
                r_id = req["id"]
                r_title = req["title"]
                r_desc = req["description"]
                r_created = req["createdAt"]
                r_status = req["status"]

                col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 2.5, 3.5, 2.2, 1.8, 2.2, 1.3])
                
                with col1:
                    st.markdown(f"**#{r_id}**")
                with col2:
                    st.write(r_title)
                with col3:
                    if len(r_desc) > 140:
                        with st.expander(r_desc[:140] + "... (Read more)"):
                            st.write(r_desc)
                    else:
                        st.write(r_desc)
                with col4:
                    st.caption(f"{r_created}")
                with col5:
                    st.markdown(render_badge(r_status), unsafe_allow_html=True)
                with col6:
                    curr_idx = STATUS_OPTIONS.index(r_status) if r_status in STATUS_OPTIONS else 0
                    selected_status = st.selectbox(
                        label=f"Status dropdown for Request #{r_id}",
                        options=STATUS_OPTIONS,
                        index=curr_idx,
                        key=f"status_sel_{r_id}_{tab_key}",
                        label_visibility="collapsed"
                    )
                with col7:
                    up_btn = st.button("Apply", key=f"btn_up_{r_id}_{tab_key}", use_container_width=True)

                if up_btn:
                    if selected_status == r_status:
                        st.info(f"Request #{r_id} is already in state '{selected_status}'.")
                    else:
                        success, message = api_update_request_status(api_base_url, r_id, selected_status)
                        if success:
                            st.success(f"Request #{r_id} dynamically updated to {selected_status}!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(f"Failed to update status: {message}")

                st.markdown("<hr style='margin: 4px 0px; border: 0; border-top: 1px solid #F1F5F9;'/>", unsafe_allow_html=True)

        with tab_all:
            # Grouping entries explicitly by status within the main tab to ensure neat organization
            for st_group in STATUS_OPTIONS:
                group_items = [r for r in requests_data if r["status"] == st_group]
                if group_items:
                    st.markdown(f"### Status Group: **{st_group.upper()}** ({len(group_items)})")
                    render_request_rows(group_items, tab_key=f"all_{st_group}")
                    st.markdown("<br>", unsafe_allow_html=True)

        with tab_pending:
            render_request_rows([r for r in requests_data if r["status"] == "pending"], tab_key="pending_only")

        with tab_approved:
            render_request_rows([r for r in requests_data if r["status"] == "approved"], tab_key="approved_only")

        with tab_rejected:
            render_request_rows([r for r in requests_data if r["status"] == "rejected"], tab_key="rejected_only")

    except Exception as e:
        st.error(f"Unexpected Application Error: {e}")
        st.caption("Please inspect the console or backend log for additional traceback details.")

if __name__ == "__main__":
    main()
