# Real-Time Request Tracker (v1 Architecture)
### Lightweight Full-Stack Monolithic Prototype

This directory contains the initial prototype of the Request Tracker application, engineered as a lightweight, full-stack application contained entirely within a single Python executable script (`app.py`).

---

## Tech Stack & Architecture
* **Frontend:** Interactive web interface built with Streamlit.
* **Backend API:** Standalone RESTful JSON server using Python's built-in `http.server`, running in a background daemon thread.
* **Database:** In-process SQLite database (`requests.db`) using parameter-bound SQL statements.
* **Architecture:** Unified single-file design (`app.py`) for rapid prototyping without external database management software or bulky web frameworks.

---

## Features
* **Single-File Execution:** All database, backend routing, and UI presentation logic run from one file.
* **Core Status Tracking:** Manages operational requests across three standard states: `Pending`, `Approved`, and `Rejected`.
* **Interactive Dashboard:** Includes metric counters, tabbed filters, and inline dropdown menus for status updates.

---

## How to Run Locally

1. **Install Dependencies:**
   ```bash
   pip install streamlit
   ```

2. **Navigate to Directory:**
   ```bash
   cd "c:/dev/Coding assessment/v1"
   ```

3. **Start Application:**
   ```bash
   streamlit run app.py
   ```
   The Streamlit app will launch at `http://localhost:8501`, and the background REST API will automatically boot on port `8000`.

---

## Project Notice
For the enterprise-ready release featuring a modular three-tier architecture, comprehensive XSS/SQLi security barriers, a 7-state workflow, real-time date math, and strict table pagination, please check out the **`v2/`** directory.
