"""
User Submission Input Form Webpage Module (v2 Architecture)
Renders the standalone input form webpage for submitting issue requests and queries.
Enforces strict security validation against SQL Injection (SQLi) and Cross-Site Scripting (XSS).
Defaults newly submitted issues strictly to 'Unassigned'.
"""

import re
import time
import streamlit as st

from frontend import api_client


def inspect_for_security_threats(text_string):
    """
    Validates user input against Cross-Site Scripting (XSS) and SQL Injection (SQLi) patterns.
    Returns (is_valid_bool, threat_type_string).
    """
    if not text_string:
        return True, ""
    
    # 1. Cross-Site Scripting (XSS) Detection
    xss_patterns = re.compile(
        r"(<script|javascript:|on\w+\s*=|<iframe|</script>|<object|<embed|<applet|<meta)",
        re.IGNORECASE
    )
    if xss_patterns.search(text_string):
        return False, "Cross-Site Scripting (XSS) script tags or event attributes detected"

    # 2. SQL Injection (SQLi) Detection
    sqli_patterns = re.compile(
        r"(\b(UNION(\s+ALL)?\s+SELECT|DROP\s+TABLE|DELETE\s+FROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET|ALTER\s+TABLE|EXEC(UTE)?\s*\(|INFORMATION_SCHEMA|SYSOBJECTS)\b|--|\bOR\b\s+[\w\'\"]+=[\w\'\"]+|\bAND\b\s+[\w\'\"]+=[\w\'\"]+)",
        re.IGNORECASE
    )
    if sqli_patterns.search(text_string):
        return False, "SQL Injection query tampering or command sequences detected"

    return True, ""


def render_input_form_page(api_base_url):
    """Renders the streamlined Issue Submission Form webpage, defaulting new entries to Unassigned without emojis."""
    st.markdown('<div class="section-card-header">Issue & Request Submission Form</div>', unsafe_allow_html=True)
    
    # Center-aligned polished card presentation layout
    col_left, col_main, col_right = st.columns([0.5, 3.5, 0.5])
    
    with col_main:
        with st.form(key="v2_streamlined_submission_form", clear_on_submit=True):
            form_title = st.text_input(
                label="Title of the Issue *", 
                max_chars=200, 
                placeholder="Enter a clear, concise title for your request or query..."
            )
            
            form_desc = st.text_area(
                label="Detailed Description *", 
                max_chars=2000, 
                height=180, 
                placeholder="Provide complete background details, technical contexts, or justification notes..."
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit_btn = st.form_submit_button("Submit Request", use_container_width=True)

        if submit_btn:
            # 1. Mandatory Input Existence Verification
            if not form_title or not form_title.strip():
                st.warning("Validation Failed: Please enter a valid Title for the issue before submitting.")
                return
            if not form_desc or not form_desc.strip():
                st.warning("Validation Failed: Please enter a Description for the issue before submitting.")
                return
            
            # 2. Frontend Security Validation (SQLi & XSS Prevention)
            title_ok, title_threat = inspect_for_security_threats(form_title)
            if not title_ok:
                st.error(f"Security Intervention (Title Field): Submission rejected because {title_threat}.")
                return

            desc_ok, desc_threat = inspect_for_security_threats(form_desc)
            if not desc_ok:
                st.error(f"Security Intervention (Description Field): Submission rejected because {desc_threat}.")
                return

            # 3. Network API Submission
            with st.spinner("Processing security verification and dispatching request to backend API..."):
                # Default status of an issue when created must be Unassigned as mandated
                success, msg = api_client.submit_new_request(
                    api_base_url, 
                    title=form_title.strip(), 
                    description=form_desc.strip(), 
                    status="Unassigned"
                )
                
            if success:
                st.success(f"Success! Request titled '{form_title.strip()}' has passed security scrutiny and is stored in SQLite as 'Unassigned'!")
                st.info("Tip: Use the toggle selector at the top of the page to navigate to the Consolidated Real-Time Dashboard to inspect your entry.")
                time.sleep(1.2)
                st.rerun()
            else:
                st.error(f"Backend API Communication Error: {msg}")
