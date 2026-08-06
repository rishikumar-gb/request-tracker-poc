"""
Frontend API Networking Client Module (v2 Architecture)
Provides structured client wrappers (GET, POST, PATCH) utilizing urllib.request 
to communicate with the background Python REST API server.
"""

import json
import urllib.request
import urllib.parse
import urllib.error


def fetch_all_requests(base_url):
    """Fetches all request records from the REST API GET endpoint."""
    try:
        req = urllib.request.Request(f"{base_url}/api/requests", method="GET")
        with urllib.request.urlopen(req, timeout=5.0) as response:
            data = json.loads(response.read().decode('utf-8'))
            return True, data.get("data", [])
    except Exception as e:
        return False, f"API Communication Failure (GET /api/requests): {e}"


def submit_new_request(base_url, title, description, status):
    """Submits a new request payload via the REST API POST endpoint."""
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


def update_request_status(base_url, request_id, new_status):
    """Updates record status via the REST API PATCH endpoint."""
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
