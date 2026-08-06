"""
Consolidated Real-Time Dashboard Webpage Module (v2 Architecture)
Renders the dedicated dashboard webpage featuring ordered KPI metric summaries across all 7 workflow states, 
rigorously centered attribute names and cell items, distinctly colored status cells with centered text, 
and external confirmation buttons located outside the table boundary next to every entry.
Displays issues sorted strictly as newest first and allows unrestricted status transitions between any values.
Paginated strictly at 10 records per page without emojis.
"""

import time
from datetime import datetime
import streamlit as st

from frontend import api_client
from database import STATUS_OPTIONS


def render_dashboard_page(api_base_url):
    """Renders the centered Consolidated Real-Time Dashboard webpage, displaying entries newest first following mandated status order without emojis."""
    st.markdown('<div class="section-card-header">Consolidated Real-Time Dashboard</div>', unsafe_allow_html=True)

    fetch_ok, requests_data = api_client.fetch_all_requests(api_base_url)
    if not fetch_ok:
        st.error(f"Failed to fetch records from backend API: {requests_data}")
        return

    if isinstance(requests_data, list) and requests_data:
        # Guarantee strict chronological sorting: newest first (descending by createdAt timestamp, then ID)
        requests_data.sort(
            key=lambda r: (str(r.get("createdAt", "")), int(r.get("id", 0))), 
            reverse=True
        )

    # Executive KPI Metric Summary Boxes covering Total + 7 Operational Statuses in exact mandated order:
    # Unassigned, In-Progress, On-Hold, Pending, Resolved, Closed, Rejected.
    total_count = len(requests_data) if isinstance(requests_data, list) else 0
    
    def count_for_status(st_name):
        if not total_count:
            return 0
        return sum(1 for r in requests_data if str(r.get("status", "")).strip().title() == st_name)

    kpi_r1 = st.columns(4)
    with kpi_r1[0]:
        st.markdown(f'<div class="kpi-card"><div class="kpi-num">{total_count}</div><div class="kpi-label">Total Recorded</div></div>', unsafe_allow_html=True)
    with kpi_r1[1]:
        st.markdown(f'<div class="kpi-card"><div class="kpi-num" style="color:#94A3B8;">{count_for_status("Unassigned")}</div><div class="kpi-label">Unassigned</div></div>', unsafe_allow_html=True)
    with kpi_r1[2]:
        st.markdown(f'<div class="kpi-card"><div class="kpi-num" style="color:#3B82F6;">{count_for_status("In-Progress")}</div><div class="kpi-label">In-Progress</div></div>', unsafe_allow_html=True)
    with kpi_r1[3]:
        st.markdown(f'<div class="kpi-card"><div class="kpi-num" style="color:#F97316;">{count_for_status("On-Hold")}</div><div class="kpi-label">On-Hold</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    
    kpi_r2 = st.columns(4)
    with kpi_r2[0]:
        st.markdown(f'<div class="kpi-card"><div class="kpi-num" style="color:#F59E0B;">{count_for_status("Pending")}</div><div class="kpi-label">Pending</div></div>', unsafe_allow_html=True)
    with kpi_r2[1]:
        st.markdown(f'<div class="kpi-card"><div class="kpi-num" style="color:#10B981;">{count_for_status("Resolved")}</div><div class="kpi-label">Resolved</div></div>', unsafe_allow_html=True)
    with kpi_r2[2]:
        st.markdown(f'<div class="kpi-card"><div class="kpi-num" style="color:#A855F7;">{count_for_status("Closed")}</div><div class="kpi-label">Closed</div></div>', unsafe_allow_html=True)
    with kpi_r2[3]:
        st.markdown(f'<div class="kpi-card"><div class="kpi-num" style="color:#EF4444;">{count_for_status("Rejected")}</div><div class="kpi-label">Rejected</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not requests_data:
        st.markdown('<div style="text-align: center; color: #94A3B8; font-weight: 500; padding: 2rem;">Dashboard Empty: No request records found in the database. Use the toggle switch to submit your first entry!</div>', unsafe_allow_html=True)
        return

    # Organized View: Tabs grouped by current status across all 7 states in required order
    tab_titles = ["All Requests (Grouped)"] + [f"{s} ({count_for_status(s)})" for s in STATUS_OPTIONS]
    all_tabs = st.tabs(tab_titles)

    def render_structured_table_rows(data_subset, tab_key_prefix):
        if not data_subset:
            st.markdown('<div style="text-align: center; color: #94A3B8; padding: 1.5rem;">No request entries available in this category.</div>', unsafe_allow_html=True)
            return

        # Lightning-fast pagination system configured strictly for 10 entries per page
        items_per_page = 10
        total_items = len(data_subset)
        total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)

        if total_pages > 1:
            page_c1, page_c2, page_c3 = st.columns([1.5, 2, 1.5])
            with page_c2:
                page_number = st.number_input(
                    f"Navigate Table Pages (Showing 10 entries per page across {total_pages} total pages):",
                    min_value=1,
                    max_value=total_pages,
                    value=1,
                    step=1,
                    key=f"page_sel_{tab_key_prefix}"
                )
        else:
            page_number = 1

        start_idx = (page_number - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        current_page_items = data_subset[start_idx:end_idx]

        st.markdown(
            f'<div style="text-align: center; color: #94A3B8; font-size: 0.9rem; margin-bottom: 14px;">Displaying records {start_idx + 1} to {end_idx} of {total_items} total entries in category (10 items per page, sorted newest first)</div>',
            unsafe_allow_html=True
        )

        # Uniform Table Attribute Header Section: Matching container borders across Table (8.5) and Action area (1.5)
        col_tbl_hdr, col_btn_hdr = st.columns([8.5, 1.5], gap="medium")
        with col_tbl_hdr:
            with st.container(border=True):
                h_id, h_title, h_desc, h_created, h_days, h_status = st.columns([0.8, 2.2, 3.0, 1.6, 1.2, 1.7])
                with h_id: st.markdown('<div class="table-header-box">ID</div>', unsafe_allow_html=True)
                with h_title: st.markdown('<div class="table-header-box">Title</div>', unsafe_allow_html=True)
                with h_desc: st.markdown('<div class="table-header-box">Description</div>', unsafe_allow_html=True)
                with h_created: st.markdown('<div class="table-header-box">Created At</div>', unsafe_allow_html=True)
                with h_days: st.markdown('<div class="table-header-box">Days Open</div>', unsafe_allow_html=True)
                with h_status: st.markdown('<div class="table-header-box">Status</div>', unsafe_allow_html=True)
        with col_btn_hdr:
            with st.container(border=True):
                st.markdown('<div class="table-header-box" style="color: #38BDF8;">Action</div>', unsafe_allow_html=True)

        # Render rows: Table cells inside border box on left (8.5), external Confirm button on right (1.5)
        for req in current_page_items:
            r_id = req["id"]
            r_title = req["title"]
            r_desc = req["description"]
            r_created = req["createdAt"]
            r_status_raw = str(req.get("status", "Unassigned")).strip().title()
            r_status = r_status_raw if r_status_raw in STATUS_OPTIONS else "Unassigned"

            # Dynamic real-time fallback verification to guarantee Days Open matches createdAt timestamp exactly
            try:
                dt_obj = datetime.strptime(str(r_created), "%Y-%m-%d %H:%M:%S")
                r_days = max(0, (datetime.now() - dt_obj).days)
            except Exception:
                r_days = req.get("daysSinceCreated", 0)

            col_tbl_row, col_btn_row = st.columns([8.5, 1.5], gap="medium")

            # INSIDE TABLE BORDER AREA: Centered attributes & distinctly colored status cell with centered text
            with col_tbl_row:
                with st.container(border=True):
                    c_id, c_title, c_desc, c_created, c_days, c_status = st.columns([0.8, 2.2, 3.0, 1.6, 1.2, 1.7])
                    
                    with c_id:
                        st.markdown(f'<div class="table-cell-content" style="font-weight: 700;">#{r_id}</div>', unsafe_allow_html=True)
                    with c_title:
                        st.markdown(f'<div class="table-cell-content">{r_title}</div>', unsafe_allow_html=True)
                    with c_desc:
                        if len(r_desc) > 120:
                            with st.expander("Read Description"):
                                st.markdown(f'<div class="table-cell-content">{r_desc}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="table-cell-content">{r_desc}</div>', unsafe_allow_html=True)
                    with c_created:
                        st.markdown(f'<div class="table-cell-content" style="color: #CBD5E1; font-size: 0.88rem;">{r_created}</div>', unsafe_allow_html=True)
                    with c_days:
                        day_label = "day" if r_days == 1 else "days"
                        st.markdown(f'<div class="table-cell-content" style="color: #38BDF8; font-weight: 600;">{r_days} {day_label}</div>', unsafe_allow_html=True)
                    with c_status:
                        curr_idx = STATUS_OPTIONS.index(r_status) if r_status in STATUS_OPTIONS else 0
                        selected_status = st.selectbox(
                            label=f"Status selector for #{r_id}",
                            options=STATUS_OPTIONS,
                            index=curr_idx,
                            key=f"sel_{r_id}_{tab_key_prefix}",
                            label_visibility="collapsed"
                        )

            # OUTSIDE TABLE BOUNDARY AREA: Confirmation button next to every entry allowing unrestricted state transitions
            with col_btn_row:
                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                confirm_btn = st.button(
                    label="Confirm Change",
                    key=f"btn_cfm_{r_id}_{tab_key_prefix}",
                    use_container_width=True,
                    type="primary"
                )

            if confirm_btn:
                if selected_status == r_status:
                    st.info(f"Request #{r_id} is currently in state '{selected_status}'. Please pick a new status from the colored dropdown cell first before confirming.")
                else:
                    with st.spinner(f"Confirming transition for Request #{r_id} to '{selected_status}'..."):
                        success, message = api_client.update_request_status(api_base_url, r_id, selected_status)
                    if success:
                        st.success(f"Confirmed! Request #{r_id} status transitioned from '{r_status}' to '{selected_status}'!")
                        time.sleep(0.6)
                        st.rerun()
                    else:
                        st.error(f"Failed to confirm status update for Request #{r_id}: {message}")

    # Tab 0: All Requests grouped across the 7 statuses in mandated order
    with all_tabs[0]:
        for st_group in STATUS_OPTIONS:
            group_items = [r for r in requests_data if str(r.get("status", "")).strip().title() == st_group]
            if group_items:
                st.markdown(f'<div style="text-align: center; font-size: 1.3rem; font-weight: 700; color: #FFFFFF; margin-top: 20px; margin-bottom: 12px; text-transform: uppercase;">Status Group: {st_group} ({len(group_items)})</div>', unsafe_allow_html=True)
                render_structured_table_rows(group_items, tab_key_prefix=f"all_{st_group.lower().replace(' ', '_')}")
                st.markdown("<br>", unsafe_allow_html=True)

    # Tabs 1 to 7: Individual dedicated tabs for each operational state in exact required order
    for idx, st_val in enumerate(STATUS_OPTIONS, start=1):
        with all_tabs[idx]:
            subset = [r for r in requests_data if str(r.get("status", "")).strip().title() == st_val]
            render_structured_table_rows(subset, tab_key_prefix=f"tab_{st_val.lower().replace(' ', '_')}")

