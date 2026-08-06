"""
Frontend Styling & Design System Module (v2 Architecture)
Encapsulates all CSS rule injections, typography settings, rigorous cell and header centering rules,
dropdown text centering, colored status cells, status badges for all 7 states (renaming Approved to Resolved),
and removal of header divider lines.
Strictly zero emojis across all elements.
"""

import streamlit as st


def inject_custom_styles():
    """Injects aesthetic CSS for centered table elements, dropdown text centering, and removes header divider lines."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
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
        
        /* White centered headers matching standard page typography WITHOUT bottom lines */
        .section-card-header {
            font-family: inherit;
            font-size: 1.7rem;
            font-weight: 700;
            color: #FFFFFF !important; /* Pure white text color */
            margin-top: 0.5rem;
            margin-bottom: 1.5rem;
            display: flex;
            justify-content: center;
            text-align: center;
            border-bottom: none !important;
            padding-bottom: 0.2rem;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        }
        
        /* Center navigation tab list across the dashboard */
        div[data-baseweb="tab-list"] {
            justify-content: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.15);
            margin-bottom: 1.2rem;
        }

        /* STRICT CENTERING: Enforce center alignment across all table header attribute names and data cell items */
        div[data-testid="stVerticalBlock"] > div[style*="border"] div[data-testid="column"] {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
        }
        
        div[data-testid="stVerticalBlock"] > div[style*="border"] div[data-testid="stMarkdownContainer"] {
            text-align: center !important;
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }

        .table-header-box {
            display: flex;
            justify-content: center;
            align-items: center;
            text-align: center;
            font-weight: 700;
            font-size: 0.98rem;
            color: #FFFFFF;
            padding: 6px 2px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            width: 100%;
        }

        .table-cell-content {
            display: flex;
            justify-content: center;
            align-items: center;
            text-align: center;
            height: 100%;
            width: 100%;
            padding: 6px 2px;
            font-size: 0.95rem;
            color: #F8FAFC;
            line-height: 1.4;
            word-break: break-word;
        }

        /* Mark the status cells in a distinct vibrant color and ensure strictly centered text inside dropdowns */
        div[data-testid="stSelectbox"] > div {
            background: linear-gradient(135deg, #0E7490 0%, #0369A1 100%) !important;
            border: 2px solid #38BDF8 !important;
            border-radius: 6px !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
            box-shadow: 0 2px 8px rgba(56, 189, 248, 0.3);
        }
        
        /* Strictly center text inside the status selectbox dropdown on all Streamlit variants */
        div[data-testid="stSelectbox"] div[data-baseweb="select"] *,
        div[data-testid="stSelectbox"] div[role="combobox"] *,
        div[data-testid="stSelectbox"] div[role="combobox"],
        div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
            text-align: center !important;
            justify-content: center !important;
            align-items: center !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }

        /* Table row container border styling for structured table aesthetics */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {
            border: 1.5px solid #64748B !important;
            background-color: #0F172A !important;
            border-radius: 8px !important;
            padding: 10px 14px !important;
            margin-bottom: 6px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }

        /* Status Badges with illumination effect matching ordered workflow states */
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
            text-align: center;
        }
        .badge-unassigned { background-color: #F1F5F9; color: #475569; border: 1px solid #E2E8F0; }
        .badge-in-progress { background-color: #DBEAFE; color: #1D4ED8; border: 1px solid #BFDBFE; }
        .badge-on-hold { background-color: #FFEDD5; color: #C2410C; border: 1px solid #FED7AA; }
        .badge-pending { background-color: #FEF3C7; color: #B45309; border: 1px solid #FDE68A; }
        .badge-resolved { background-color: #D1FAE5; color: #047857; border: 1px solid #A7F3D0; }
        .badge-closed { background-color: #E9D5FF; color: #6B21A8; border: 1px solid #D8B4FE; }
        .badge-rejected { background-color: #FEE2E2; color: #B91C1C; border: 1px solid #FECACA; }
        
        /* Executive Dashboard Metric KPI Cards */
        .kpi-card {
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(148, 163, 184, 0.3);
            padding: 1.0rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            backdrop-filter: blur(8px);
            margin: 0 auto;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(255, 255, 255, 0.15);
            border-color: rgba(255, 255, 255, 0.4);
        }
        .kpi-num {
            font-family: inherit;
            font-size: 2.0rem;
            font-weight: 700;
            color: #FFFFFF;
            margin: 0;
            text-align: center;
        }
        .kpi-label {
            font-size: 0.82rem;
            color: #CBD5E1;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-top: 4px;
            text-align: center;
        }
        
        /* Polished form styling */
        div[data-testid="stForm"] {
            border: 1px solid rgba(148, 163, 184, 0.25);
            border-radius: 12px;
            padding: 1.6rem;
            background: rgba(15, 23, 42, 0.4);
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.2);
        }
        </style>
    """, unsafe_allow_html=True)


def render_badge(status):
    """Returns styled HTML span elements representing request statuses without emojis."""
    status_clean = status.lower().strip().replace(" ", "-")
    if status_clean == "unassigned":
        return '<div style="text-align: center;"><span class="badge badge-unassigned">Unassigned</span></div>'
    elif status_clean == "in-progress":
        return '<div style="text-align: center;"><span class="badge badge-in-progress">In-Progress</span></div>'
    elif status_clean == "on-hold":
        return '<div style="text-align: center;"><span class="badge badge-on-hold">On-Hold</span></div>'
    elif status_clean == "pending":
        return '<div style="text-align: center;"><span class="badge badge-pending">Pending</span></div>'
    elif status_clean in ["resolved", "approved"]:
        return '<div style="text-align: center;"><span class="badge badge-resolved">Resolved</span></div>'
    elif status_clean == "closed":
        return '<div style="text-align: center;"><span class="badge badge-closed">Closed</span></div>'
    elif status_clean == "rejected":
        return '<div style="text-align: center;"><span class="badge badge-rejected">Rejected</span></div>'
    return f'<div style="text-align: center;"><span>{status}</span></div>'

