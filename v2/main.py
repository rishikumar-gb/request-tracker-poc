"""
Main Application Entrypoint & Orchestrator (v2 Architecture)
Links all modular tiers together: SQLite database layer, Python RESTful API backend server, 
and Streamlit presentation view components. 
Includes top webpage navigation toggle switch between Input Form and Consolidated Dashboard.
"""

import importlib
import streamlit as st

import database
import backend
from frontend import styles
from frontend import input_form
from frontend import dashboard


# =====================================================================
# STREAMLIT PAGE CONFIGURATION
# =====================================================================
st.set_page_config(
    page_title="Request Tracker Console",
    layout="wide",
    initial_sidebar_state="collapsed"
)


@st.cache_resource(show_spinner=False)
def bootstrap_backend_api():
    """Starts the SQLite Database schema & RESTful HTTP API server once per app instance on dedicated port 8100+."""
    importlib.reload(database)
    importlib.reload(backend)
    return backend.launch_api_server()


def main():
    try:
        # Step 1: Inject design styling system and cursor overrides
        styles.inject_custom_styles()
        
        # Step 2: Boot backend API tier in daemon thread on dedicated port 8100+
        server_ok, server_url_or_err = bootstrap_backend_api()
        if not server_ok:
            st.error(f"Critical System Service Error: Unable to launch backend REST API server. Details: {server_url_or_err}")
            return

        api_base_url = server_url_or_err

        # =====================================================================
        # TOP NAVIGATION TOGGLE SWITCH (Webpage Router)
        # =====================================================================
        view_toggle = st.radio(
            label="Page Navigation Toggle",
            options=["Request Submission Form Page", "Consolidated Live Dashboard Page"],
            index=0,
            horizontal=True,
            label_visibility="collapsed",
            help="Toggle between the standalone Request Submission Form webpage and the Consolidated Live Dashboard webpage."
        )

        st.markdown("<hr style='margin: 8px 0px 20px 0px; border: 0; border-top: 1.5px solid #CBD5E1;'/>", unsafe_allow_html=True)

        # =====================================================================
        # WEBPAGE VIEW ROUTING & RENDERING
        # =====================================================================
        if view_toggle == "Request Submission Form Page":
            input_form.render_input_form_page(api_base_url)
        elif view_toggle == "Consolidated Live Dashboard Page":
            dashboard.render_dashboard_page(api_base_url)

    except Exception as general_err:
        st.error(f"Application Orchestration Fault: {general_err}")
        st.caption("Please inspect terminal traceback log for detailed diagnostic information.")


if __name__ == "__main__":
    main()

