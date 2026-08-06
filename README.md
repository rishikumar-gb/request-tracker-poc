# Real-Time Request Tracker & Dispatch Console
### Architectural Evaluation & Proof of Concept Repository

This repository contains the evaluation engineering submission for the Real-Time Request Tracker and Dispatch Console. It is structured into two iterative architectural releases (`v1` and `v2`) to demonstrate software evolution from an agile single-file prototype into an enterprise-ready, modular three-tier web application.

---

## Repository Structure & Version Comparison

```
request-tracker-poc/
│── v1/               # Iteration 1: Foundation Single-File Monolithic Prototype
│── v2/               # Iteration 2: Enterprise Modular Three-Tier Architecture
├── .gitignore        # Version control exclusion policies
└── README.md         # Repository general documentation
```

### [v1 Architecture (Foundation Monolifit Prototype)](./v1)
* **Design Philosophy:** Optimized for rapid prototyping and zero-configuration setups.
* **Structure:** All relational SQLite commands, background RESTful API networking, and responsive Streamlit presentation views are bundled directly into a single script (`app.py`).
* **Core Capabilities:** Tracks standard operational workflow states (`Pending`, `Approved`, `Rejected`), real-time metric scorecards, and inline status modification.

### [v2 Architecture (Enterprise Three-Tier Modular Application)](./v2)
* **Design Philosophy:** Optimized for strict separation of concerns, long-term maintainability, robust cybersecurity defenses, and enterprise scalability.
* **Structure:** Decoupled into independent tiers: Data Engine (`database.py`), Backend API Daemon (`backend.py`), and dedicated Presentation Components (`frontend/` package, orchestrated by `main.py`).
* **Core Capabilities:**
  * **Ordered 7-State Workflow:** Tracks records across an extended workflow lifecycle: `Unassigned` ➔ `In-Progress` ➔ `On-Hold` ➔ `Pending` ➔ `Resolved` ➔ `Closed` ➔ `Rejected`.
  * **Dual-Layer Security:** Frontend regular expressions actively intercept Cross-Site Scripting (XSS) and SQL Injection (SQLi) attack patterns before network transmission. The data tier executes exclusively parameter-bound SQL statements.
  * **Real-Time Date Synchronization:** Dynamically calculates chronological elapsed time ("Days Open") directly from historical submission timestamps without static data caching.
  * **Newest-First Chronological Ordering:** Automatically sorts all dashboard views and database queries by submission timestamps in descending order.
  * **Strict Table Pagination:** Displays exactly 10 records per page for optimal rendering performance across large datasets (500+ records).
  * **Intentional UI Layouts:** Separate webpages for Issue Submission and Live Dashboard navigation. Table view controls separate internal status dropdowns from external "Confirm Change" trigger buttons to prevent accidental workflow modifications.

---

## Technology Stack

* **Programming Language:** Pure Python 3 (using standard libraries for threading, JSON serialization, and HTTP protocols).
* **Frontend Presentation:** Streamlit (interactive UI design system with custom vanilla CSS injections and flexbox alignment rules).
* **Backend Networking:** Standalone RESTful JSON Server via Python built-in `ThreadingHTTPServer` hosted on isolated ports in background daemon threads.
* **Relational Database:** In-process SQLite3 (`requests.db`) with automatic table verification and sample data seeding.
* **Dependencies:** Zero heavy external application server or database software installation required—only Python and Streamlit.

---

## Getting Started & Execution Instructions

### 1. Prerequisites & Installation
Ensure Python 3.8+ is installed on your workstation, then install the sole UI library via pip:
```bash
pip install streamlit --upgrade
```

### 2. Launching the Modular Enterprise Application (v2 - Recommended)
1. Navigate directly into the `v2` directory:
   ```bash
   cd v2
   ```
2. Execute the application orchestrator:
   ```bash
   streamlit run main.py
   ```
   * The UI dashboard will open automatically in your browser at `http://localhost:8501`.
   * The backend REST API daemon server will bind automatically in the background to dedicated ports (`8100-8120`).

### 3. Launching the Initial Monolithic Prototype (v1)
1. Navigate directly into the `v1` directory:
   ```bash
   cd ../v1
   ```
2. Execute the self-contained script:
   ```bash
   streamlit run app.py
   ```

---

## Review & Testing Highlights for Evaluators

When assessing the **v2** implementation, we invite evaluators to verify the following design metrics:
1. **Security Validation:** Try typing malicious script payloads (such as `<script>alert(1);</script>`) or basic SQL injection strings into the `v2` Request Submission form to trigger instant threat interception warnings.
2. **Workflow State Persistence:** Navigate to the Live Dashboard tab, select any status option in an inline table dropdown, and click **"Confirm Change"** to verify instantaneous REST API interaction and permanent SQLite state transition.
3. **Pagination & Sort Verification:** Observe that all 500+ pre-seeded enterprise sample records render strictly sorted newest-timestamp first, divided cleanly across navigable 10-item table pages.


