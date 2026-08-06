# Real-Time Request Tracker (v2 Architecture)
### Enterprise Modular Full-Stack Application

This directory contains the production-ready release of the Request Tracker application. It evolves the single-file prototype (`v1`) into a clean, decoupled three-tier architecture with robust security controls, accurate real-time data calculations, and polished presentation layouts.

---

## Architecture & File Structure
The codebase is cleanly divided into Data, Backend API, and Frontend UI tiers:

```
v2/
│── main.py                   # App Entrypoint & Webpage View Router
│── database.py               # Data Tier: SQLite3 DB & Elapsed Time Calculation
│── backend.py                # Backend Tier: RESTful JSON API Daemon Server
├── frontend/                 # Presentation Tier: Decoupled Client Components
│    ├── __init__.py          
│    ├── api_client.py        # HTTP Client Wrapper (urllib.request)
│    ├── input_form.py        # Issue Submission Page & XSS/SQLi Validation
│    ├── dashboard.py         # Live Dashboard, Tabs, & Table Pagination
│    └── styles.py            # Vanilla CSS Styling & Centered Table Rules
```

* **Data Layer (`database.py`):** SQLite database engine running parameter-bound CRUD queries and computing real-time elapsed days directly from timestamps.
* **REST API Layer (`backend.py`):** Standalone HTTP server hosted in a background daemon thread on dedicated ports (`8100-8120`). Exposes endpoints for reading, creating, and updating issue records.
* **Frontend Layer (`frontend/`):** Streamlit presentation tier that communicates with the database exclusively via network HTTP requests to the REST API.

---

## Key Features
* **7-State Workflow:** Supports unrestricted state transitions across an ordered enterprise workflow sequence:
  `Unassigned` ➔ `In-Progress` ➔ `On-Hold` ➔ `Pending` ➔ `Resolved` ➔ `Closed` ➔ `Rejected`
* **Dual-Layer Security:** Frontend regular expressions intercept Cross-Site Scripting (XSS) and SQL Injection (SQLi) patterns before transmission. The database tier strictly executes parameter-bound SQL tuples (`VALUES (?, ?, ?)`).
* **Real-Time Date Synchronization:** Dynamically calculates "Days Open" directly from submission timestamps on every request, avoiding outdated static integer caching.
* **Sorted Newest First:** All records are ordered descending by timestamp so newest entries always appear at the top.
* **Table Pagination:** Displays exactly 10 records per page for optimal browser performance.
* **Intentional UX Controls:** A top toggle button switches between the Input Form and Live Dashboard. In the table view, status dropdowns remain inside the row while the "Confirm Change" button sits outside to prevent accidental modifications.

---

## How to Run Locally

1. **Install Dependencies:**
   ```bash
   pip install streamlit
   ```

2. **Navigate to Directory:**
   ```bash
   cd "c:/dev/Coding assessment/v2"
   ```

3. **Start Application:**
   ```bash
   streamlit run main.py
   ```
   The UI will launch at `http://localhost:8501` and connect automatically to the background REST server running on port `8100+`.

---

## Quick Testing Guide
1. **Submit an Issue:** On the **Request Submission Form Page**, create a new request and note that its status defaults automatically to **`Unassigned`**.
2. **Test Security Controls:** Try entering `<script>alert('test')</script>` or a SQL injection query into the form fields to see immediate threat interception.
3. **Transition Statuses:** Switch to the **Consolidated Live Dashboard Page**, change an item's dropdown status, and click **"Confirm Change"** to permanently update the record in SQLite.
