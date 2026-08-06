"""
Backend RESTful API Server Tier for Request Tracker (v2 Architecture)
Handles HTTP routing (GET, POST, PATCH endpoints), JSON data serializing/deserializing, 
business payload validation supporting transitioning between any of the 7 ordered workflow states,
and daemon thread hosting on dedicated port 8100+.
Strictly decoupled from Streamlit UI presentation elements.
"""

import json
import threading
import urllib.parse
from datetime import datetime
from http.server import BaseHTTPRequestHandler
try:
    from http.server import ThreadingHTTPServer as HTTPServerClass
except ImportError:
    from http.server import HTTPServer as HTTPServerClass

import database
from database import STATUS_OPTIONS


def normalize_status(val):
    val_str = str(val).strip().title()
    if val_str in ["Approved", "approved"]:
        val_str = "Resolved"
    for opt in STATUS_OPTIONS:
        if opt.lower() == val_str.lower():
            return opt
    return val_str


class RequestTrackerRESTHandler(BaseHTTPRequestHandler):
    """Custom RESTful HTTP request handler supporting GET, POST, and PATCH endpoints."""

    def log_message(self, format, *args):
        # Silence routine console logging for clean interface presentation
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
            print(f"[Backend API Server Error] Failed to send HTTP response: {e}")

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_json_response(200, {"status": "ok"})

    def do_GET(self):
        """Handle GET endpoints, primarily retrieving all requests with synchronized Days Open values."""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            if parsed_path.path in ["/api/requests", "/api/requests/"]:
                records = database.get_all_requests_db()
                self.send_json_response(200, {"status": "success", "data": records, "count": len(records)})
            elif parsed_path.path == "/api/health":
                self.send_json_response(200, {"status": "healthy", "service": "Request Tracker v2 REST API", "supported_statuses": STATUS_OPTIONS})
            else:
                self.send_json_response(404, {"status": "error", "message": "REST endpoint not found."})
        except Exception as e:
            self.send_json_response(500, {"status": "error", "message": f"Internal server fault: {e}"})

    def do_POST(self):
        """Handle POST endpoints for validating and persisting new incoming requests."""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            if parsed_path.path in ["/api/requests", "/api/requests/"]:
                content_length = int(self.headers.get("Content-Length", 0))
                raw_body = self.rfile.read(content_length).decode("utf-8")
                payload = json.loads(raw_body) if raw_body else {}

                # Business Logic Data Validation
                title = str(payload.get("title", "")).strip()
                description = str(payload.get("description", "")).strip()
                
                # The default status of an issue when it's created must be Unassigned
                status = normalize_status(payload.get("status", "Unassigned"))

                if not title:
                    self.send_json_response(400, {"status": "error", "message": "Validation failed: Title cannot be empty."})
                    return
                if not description:
                    self.send_json_response(400, {"status": "error", "message": "Validation failed: Description cannot be empty."})
                    return
                if status not in STATUS_OPTIONS:
                    self.send_json_response(400, {"status": "error", "message": f"Validation failed: Status must be one of {STATUS_OPTIONS}."})
                    return

                # Automated timestamp generation using Python datetime library
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Delegate database insertion to Database Tier
                new_id = database.insert_request_db(title, description, status, created_at)
                if new_id is not None:
                    response_data = {
                        "status": "success",
                        "message": "Request record validated and stored in SQLite successfully with default status Unassigned.",
                        "data": {
                            "id": new_id,
                            "title": title,
                            "description": description,
                            "status": status,
                            "createdAt": created_at,
                            "daysSinceCreated": 0
                        }
                    }
                    self.send_json_response(201, response_data)
                else:
                    self.send_json_response(500, {"status": "error", "message": "Database insertion failure."})
            else:
                self.send_json_response(404, {"status": "error", "message": "Endpoint not found."})
        except json.JSONDecodeError:
            self.send_json_response(400, {"status": "error", "message": "Invalid JSON structure in POST body."})
        except Exception as e:
            self.send_json_response(500, {"status": "error", "message": f"Internal server processing fault: {e}"})

    def do_PATCH(self):
        """Handle PATCH endpoints allowing transitions from any valid workflow status to any other valid workflow status."""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path_segments = [seg for seg in parsed_path.path.split("/") if seg]
            
            # Match URI format: /api/requests/<id>
            if len(path_segments) >= 3 and path_segments[0] == "api" and path_segments[1] == "requests":
                try:
                    target_id = int(path_segments[2])
                except ValueError:
                    self.send_json_response(400, {"status": "error", "message": "Invalid ID format in URI parameter."})
                    return

                content_length = int(self.headers.get("Content-Length", 0))
                raw_body = self.rfile.read(content_length).decode("utf-8")
                payload = json.loads(raw_body) if raw_body else {}
                
                new_status = normalize_status(payload.get("status", ""))
                if new_status not in STATUS_OPTIONS:
                    self.send_json_response(400, {"status": "error", "message": f"Validation failed: Status must be one of {STATUS_OPTIONS}."})
                    return

                # Delegate unrestricted workflow transition directly to Database Tier SQLite table
                updated = database.update_request_status_db(target_id, new_status)
                if updated:
                    self.send_json_response(200, {"status": "success", "message": f"Status confirmed and transitioned in SQLite database to '{new_status}' successfully."})
                else:
                    self.send_json_response(404, {"status": "error", "message": "Request ID not found in database."})
            else:
                self.send_json_response(404, {"status": "error", "message": "Endpoint signature not recognized."})
        except json.JSONDecodeError:
            self.send_json_response(400, {"status": "error", "message": "Invalid JSON payload."})
        except Exception as e:
            self.send_json_response(500, {"status": "error", "message": f"Internal server execution fault: {e}"})


def launch_api_server():
    """Initializes SQLite schema and boots the background daemon REST server on port 8100+."""
    database.init_db()
    
    # Propose standard port bindings for v2 starting at 8100 to prevent port collisions with legacy v1 app
    for port in range(8100, 8120):
        try:
            server = HTTPServerClass(("0.0.0.0", port), RequestTrackerRESTHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            print(f"[Backend Tier] REST API Server booted successfully at http://localhost:{port}")
            return True, f"http://localhost:{port}"
        except OSError:
            continue
        except Exception as e:
            print(f"[Server Init Error on port {port}]: {e}")
            continue
            
    try:
        # Fallback dynamic OS port allocation
        server = HTTPServerClass(("0.0.0.0", 0), RequestTrackerRESTHandler)
        allocated_port = server.server_port
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        print(f"[Backend Tier] REST API Server booted on ephemeral port at http://localhost:{allocated_port}")
        return True, f"http://localhost:{allocated_port}"
    except Exception as e:
        return False, f"Server boot failure: {e}"
