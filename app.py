"""
WSCC Investigation Management System - Streamlit Version (COMPLETE)
Main application file with ALL features implemented
Version 2.0 - Complete Implementation
"""

import streamlit as st
from datetime import datetime, timedelta
import uuid
import json
import base64
from io import BytesIO
import pandas as pd
from database import Database
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Page configuration
st.set_page_config(
    page_title="WSCC Investigation Management",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"  # Collapse sidebar for horizontal menu
)

# Initialize database
@st.cache_resource
def get_database():
    """Initialize and cache database connection"""
    return Database()

db = get_database()

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'
if 'current_case_id' not in st.session_state:
    st.session_state.current_case_id = None
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'
if 'editing_case' not in st.session_state:
    st.session_state.editing_case = False

# Custom CSS matching master project (WSCC Official Theme)
st.markdown("""
    <style>
    /* Import Inter font to match master project */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* WSCC Official Colors (Light Theme) */
    :root {
        --primary-color: #2c5282;
        --primary-dark: #1a365d;
        --primary-light: #4299e1;
        --primary-lighter: #90cdf4;
        --primary-lightest: #bee3f8;
        --wscc-blue-bg: #ebf8ff;
        --wscc-blue-border: #90cdf4;
        --success-color: #38a169;
        --warning-color: #d69e2e;
        --danger-color: #e53e3e;
        --info-color: #3182ce;
        --text-primary: #2d3748;
        --text-secondary: #4a5568;
        --border-color: #e2e8f0;
        --bg-white: #ffffff;
        --bg-gray: #f7fafc;
    }

    /* Apply Inter font globally */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    /* Main header styling (matching master project) */
    .main-header {
        font-size: 2.2rem;
        font-weight: 600;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }

    /* Stat cards - Light Theme */
    .stat-card {
        background: linear-gradient(135deg, var(--wscc-blue-bg) 0%, #ffffff 100%);
        border: 2px solid var(--wscc-blue-border);
        padding: 1.5rem;
        border-radius: 12px;
        color: var(--primary-color);
        text-align: center;
        box-shadow: 0 2px 4px rgba(44, 82, 130, 0.1);
        transition: all 0.3s ease;
    }

    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(44, 82, 130, 0.15);
        border-color: var(--primary-color);
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        color: var(--primary-color);
    }

    .stat-label {
        font-size: 0.875rem;
        margin-top: 0.5rem;
        font-weight: 500;
        color: var(--text-secondary);
    }

    /* Priority colors (matching master project) */
    .priority-high {
        color: var(--danger-color);
        font-weight: 600;
    }

    .priority-medium {
        color: var(--warning-color);
        font-weight: 600;
    }

    .priority-low {
        color: var(--success-color);
        font-weight: 600;
    }

    /* Timeline styling - Light Theme */
    .timeline-event {
        border-left: 4px solid var(--primary-light);
        padding-left: 1rem;
        margin-bottom: 1rem;
        background: var(--wscc-blue-bg);
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        border: 1px solid var(--wscc-blue-border);
        border-left: 4px solid var(--primary-light);
    }

    .timeline-event:hover {
        background: white;
        border-left-color: var(--primary-color);
        box-shadow: 0 2px 4px rgba(44, 82, 130, 0.1);
    }

    /* Button styling - Light Theme */
    .stButton>button {
        background-color: var(--primary-color);
        color: white;
        border: 2px solid transparent;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(44, 82, 130, 0.1);
    }

    .stButton>button:hover {
        background-color: var(--primary-dark);
        box-shadow: 0 4px 8px rgba(44, 82, 130, 0.2);
        transform: translateY(-1px);
    }

    /* Secondary button style */
    .stButton>button[kind="secondary"] {
        background-color: white;
        color: var(--primary-color);
        border: 2px solid var(--wscc-blue-border);
    }

    .stButton>button[kind="secondary"]:hover {
        background-color: var(--wscc-blue-bg);
        border-color: var(--primary-color);
    }

    /* Sidebar styling - Light Theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, var(--bg-gray) 100%);
        border-right: 2px solid var(--wscc-blue-border);
    }

    /* Success/Warning/Error messages - Light Theme */
    .stSuccess {
        background: linear-gradient(135deg, #d4edda 0%, #f1f9f4 100%) !important;
        color: #155724 !important;
        border-left: 5px solid var(--success-color) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }

    .stWarning {
        background: linear-gradient(135deg, #fff3cd 0%, #fffbf0 100%) !important;
        color: #856404 !important;
        border-left: 5px solid var(--warning-color) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }

    .stError {
        background: linear-gradient(135deg, #f8d7da 0%, #fef5f6 100%) !important;
        color: #721c24 !important;
        border-left: 5px solid var(--danger-color) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }

    .stInfo {
        background: linear-gradient(135deg, var(--wscc-blue-bg) 0%, #ffffff 100%) !important;
        color: var(--primary-color) !important;
        border-left: 5px solid var(--primary-light) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }

    /* Card styling - Light Theme */
    .case-card, .officer-card {
        background: linear-gradient(135deg, white 0%, var(--bg-gray) 100%);
        border: 2px solid var(--wscc-blue-border);
        border-radius: 12px;
        padding: 1.25rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(44, 82, 130, 0.05);
    }

    .case-card:hover, .officer-card:hover {
        box-shadow: 0 8px 16px rgba(44, 82, 130, 0.12);
        border-color: var(--primary-color);
        transform: translateY(-2px);
    }

    /* Professional header bar */
    .wscc-header {
        background: linear-gradient(135deg, #2c5f8d 0%, #1e3a5f 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .wscc-header h1 {
        margin: 0;
        font-size: 1.75rem;
        font-weight: 600;
    }

    .wscc-header p {
        margin: 0.25rem 0 0 0;
        opacity: 0.95;
        font-size: 0.875rem;
    }

    /* Horizontal Navigation Bar - Light Theme */
    .horizontal-nav {
        background: linear-gradient(180deg, #ffffff 0%, #f7fafc 100%);
        border-bottom: 3px solid var(--primary-color);
        padding: 0;
        margin: 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        position: sticky;
        top: 0;
        z-index: 1000;
        margin-bottom: 2rem;
    }

    .nav-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 2rem;
        max-width: 100%;
    }

    .nav-brand {
        color: var(--primary-color);
        font-weight: 700;
        font-size: 1.4rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .nav-brand-subtitle {
        font-size: 0.75rem;
        opacity: 0.8;
        font-weight: 400;
        color: var(--text-secondary);
    }

    .nav-menu {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }

    .nav-stats {
        display: flex;
        gap: 1.5rem;
        color: var(--text-primary);
        font-size: 0.85rem;
    }

    .nav-stat-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background: var(--wscc-blue-bg);
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border: 1px solid var(--wscc-blue-border);
    }

    .nav-stat-number {
        font-weight: 700;
        font-size: 1.2rem;
        color: var(--primary-color);
    }

    /* Hide default Streamlit header */
    header[data-testid="stHeader"] {
        display: none;
    }

    /* Boxed layout - centered container */
    .main .block-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 1rem 2rem;
        background: white;
        box-shadow: 0 0 20px rgba(44, 82, 130, 0.08);
        border-radius: 12px;
        margin-top: 1rem;
        margin-bottom: 2rem;
    }

    /* Global body background */
    .stApp {
        background: linear-gradient(180deg, #f7fafc 0%, var(--wscc-blue-bg) 100%);
    }
    </style>
""", unsafe_allow_html=True)

# Horizontal Navigation Bar
stats = db.get_statistics()
current_page = st.session_state.current_page

# Create horizontal navigation
st.markdown(f"""
<div class="horizontal-nav">
    <div class="nav-container">
        <div class="nav-brand">
            <div>
                <div>🔍 WSCC Investigation Management</div>
                <div class="nav-brand-subtitle">Northwest Territories & Nunavut</div>
            </div>
        </div>
        <div class="nav-stats">
            <div class="nav-stat-item">
                <span>📊</span>
                <div>
                    <div class="nav-stat-number">{stats.get('total_cases', 0)}</div>
                    <div style="font-size: 0.7rem; opacity: 0.85;">Cases</div>
                </div>
            </div>
            <div class="nav-stat-item">
                <span>👥</span>
                <div>
                    <div class="nav-stat-number">{stats.get('active_officers', 0)}</div>
                    <div style="font-size: 0.7rem; opacity: 0.85;">Officers</div>
                </div>
            </div>
            <div class="nav-stat-item">
                <span style="font-size: 0.7rem; opacity: 0.7;">v2.0</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation menu buttons (horizontal)
pages = {
    '📊 Dashboard': 'Dashboard',
    '🔍 Smart Search': 'Search',
    '📁 Cases': 'Cases',
    '👥 Officers': 'Officers',
    '📄 Reports': 'Reports',
    '⚙️ Settings': 'Settings'
}

# Create horizontal menu with columns
cols = st.columns(len(pages))
for idx, (icon_label, page_name) in enumerate(pages.items()):
    with cols[idx]:
        # Highlight active page
        button_type = "primary" if current_page == page_name else "secondary"
        if st.button(icon_label, key=f"nav_{page_name}", use_container_width=True, type=button_type):
            st.session_state.current_page = page_name
            st.rerun()

st.markdown("---")

# ==================== PAGE: DASHBOARD ====================
def render_dashboard():
    """Render professional dashboard with charts for legal-grade presentation"""
    st.title("📊 Dashboard")
    st.caption("Overview of all investigation cases and statistics")

    # Get statistics
    stats = db.get_statistics()
    all_cases = db.get_all_cases()

    # Statistics cards (Light blue theme)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats.get('total_cases', 0)}</div>
            <div class="stat-label">Total Cases</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        open_cases = stats.get('by_status', {}).get('Open', 0) + stats.get('by_status', {}).get('Under Investigation', 0)
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{open_cases}</div>
            <div class="stat-label">Active Cases</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        nwt_cases = stats.get('by_territory', {}).get('Northwest Territories', 0)
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{nwt_cases}</div>
            <div class="stat-label">NWT Cases</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        nu_cases = stats.get('by_territory', {}).get('Nunavut', 0)
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{nu_cases}</div>
            <div class="stat-label">Nunavut Cases</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Professional Charts Section
    st.subheader("📈 Investigation Analytics")

    # Row 1: Status and Territory Charts
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("**Case Status Distribution**")
        status_data = stats.get('by_status', {})
        if status_data:
            # Create DataFrame for status chart
            status_df = pd.DataFrame({
                'Status': list(status_data.keys()),
                'Count': list(status_data.values())
            })
            # Use Streamlit's built-in bar chart with WSCC colors
            st.bar_chart(status_df.set_index('Status'), color='#2c5282')
        else:
            st.info("No data available")

    with chart_col2:
        st.markdown("**Territory Comparison**")
        territory_data = stats.get('by_territory', {})
        if territory_data:
            # Create DataFrame for territory chart
            territory_df = pd.DataFrame({
                'Territory': list(territory_data.keys()),
                'Cases': list(territory_data.values())
            })
            # Use bar chart
            st.bar_chart(territory_df.set_index('Territory'), color='#4299e1')
        else:
            st.info("No data available")

    # Row 2: Priority and Officer Workload
    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        st.markdown("**Priority Distribution**")
        priority_data = stats.get('by_priority', {})
        if priority_data:
            # Create DataFrame for priority chart
            priority_df = pd.DataFrame({
                'Priority': list(priority_data.keys()),
                'Count': list(priority_data.values())
            })
            # Sort by priority (High, Medium, Low)
            priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
            priority_df['sort_order'] = priority_df['Priority'].map(priority_order)
            priority_df = priority_df.sort_values('sort_order')
            st.bar_chart(priority_df.set_index('Priority')['Count'], color='#f59e0b')
        else:
            st.info("No data available")

    with chart_col4:
        st.markdown("**Officer Workload**")
        # Calculate officer workload
        officer_workload = {}
        for case in all_cases:
            if case['status'] in ['Open', 'Under Investigation']:
                officers = case.get('assigned_officers', [])
                if officers:
                    for officer_id in officers:
                        officer = db.get_officer_by_id(officer_id)
                        if officer:
                            name = officer['name']
                            officer_workload[name] = officer_workload.get(name, 0) + 1
                else:
                    officer_workload['Unassigned'] = officer_workload.get('Unassigned', 0) + 1

        if officer_workload:
            # Create DataFrame
            workload_df = pd.DataFrame({
                'Officer': list(officer_workload.keys()),
                'Active Cases': list(officer_workload.values())
            })
            # Sort by count
            workload_df = workload_df.sort_values('Active Cases', ascending=False).head(6)
            st.bar_chart(workload_df.set_index('Officer'), color='#10b981')
        else:
            st.info("No active cases assigned")

    st.markdown("---")

    # Row 3: Cases Over Time (Line Chart)
    st.markdown("**📅 Cases Over Time**")
    if all_cases:
        # Prepare data for time series
        case_dates = []
        for case in all_cases:
            if case.get('reported_date'):
                try:
                    date = datetime.fromisoformat(case['reported_date'])
                    case_dates.append(date.date())
                except:
                    pass

        if case_dates:
            # Count cases per month
            from collections import Counter
            date_counts = Counter([f"{d.year}-{d.month:02d}" for d in case_dates])
            sorted_dates = sorted(date_counts.items())

            # Create DataFrame
            timeline_df = pd.DataFrame({
                'Month': [d[0] for d in sorted_dates],
                'Cases Reported': [d[1] for d in sorted_dates]
            })
            st.line_chart(timeline_df.set_index('Month'), color='#2c5282')
        else:
            st.info("No date information available")
    else:
        st.info("No cases to display")

    st.markdown("---")

    # Recent cases
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📋 Recent Cases")
        recent_cases = db.get_all_cases()[:5]  # Get 5 most recent

        if recent_cases:
            for case in recent_cases:
                with st.container():
                    case_col1, case_col2, case_col3 = st.columns([3, 1, 1])

                    with case_col1:
                        st.markdown(f"**{case['case_number']}** - {case['employer']}")
                        st.caption(f"{case['worker']} | {case['territory']}")

                    with case_col2:
                        priority_class = f"priority-{case['priority'].lower()}"
                        st.markdown(f"<span class='{priority_class}'>{case['priority']}</span>", unsafe_allow_html=True)

                    with case_col3:
                        if st.button("View", key=f"view_{case['id']}"):
                            st.session_state.current_case_id = case['id']
                            st.session_state.current_page = 'Cases'
                            st.rerun()

                    st.markdown("---")
        else:
            st.info("No cases found. Add your first case!")

    with col2:
        st.subheader("⚖️ Case Metrics")

        # Calculate additional metrics
        if all_cases:
            # Average case duration for closed cases
            closed_cases = [c for c in all_cases if c['status'] == 'Closed']
            if closed_cases:
                st.metric("Closed Cases", len(closed_cases))

            # High priority cases
            high_priority = len([c for c in all_cases if c['priority'] == 'High'])
            st.metric("High Priority", high_priority, delta="Requires attention" if high_priority > 0 else None)

            # Cases with tasks
            cases_with_tasks = len([c for c in all_cases if c.get('tasks')])
            st.metric("Cases with Tasks", cases_with_tasks)

            # Cases with evidence
            cases_with_evidence = len([c for c in all_cases if c.get('evidence')])
            st.metric("Cases with Evidence", cases_with_evidence)
        else:
            st.info("No metrics available")

# ==================== PAGE: SMART SEARCH ====================
def render_search():
    """Render smart search page with semantic search and similar case finder"""
    st.title("🔍 Smart Search")
    st.caption("Search across all cases with natural language and find similar investigations")

    # Get all cases
    all_cases = db.get_all_cases()

    if not all_cases:
        st.info("No cases available to search. Add your first case to get started!")
        return

    # Create tabs for different search modes
    search_tabs = st.tabs(["🔎 Natural Language Search", "🎯 Similar Case Finder", "🏷️ Auto-Tag Cases"])

    # TAB 1: NATURAL LANGUAGE SEARCH
    with search_tabs[0]:
        st.subheader("Natural Language Search")
        st.caption("Search using plain language - the system understands context, not just keywords!")

        # Search input
        search_query = st.text_input(
            "What are you looking for?",
            placeholder="e.g., 'electrical incidents with serious injuries' or 'scaffolding falls in mining'",
            key="nl_search"
        )

        # Search options
        col1, col2, col3 = st.columns(3)
        with col1:
            search_scope = st.selectbox("Search in:", [
                "All Fields (Description, Reports, Timeline, Evidence)",
                "Description Only",
                "Reports Only",
                "Timeline Events",
                "Evidence & Photos"
            ])
        with col2:
            min_relevance = st.slider("Minimum Relevance %", 0, 100, 30)
        with col3:
            max_results = st.number_input("Max Results", 1, 50, 10)

        if st.button("🔍 Search", use_container_width=True) or search_query:
            if search_query:
                with st.spinner("Searching across all cases..."):
                    results = perform_semantic_search(
                        all_cases,
                        search_query,
                        search_scope,
                        min_relevance/100,
                        max_results
                    )

                    if results:
                        st.success(f"Found {len(results)} relevant cases!")

                        for case, score, matched_text in results:
                            relevance_pct = score * 100

                            # Color code relevance
                            if relevance_pct >= 70:
                                relevance_color = "#38a169"  # Green
                            elif relevance_pct >= 50:
                                relevance_color = "#d69e2e"  # Yellow
                            else:
                                relevance_color = "#e53e3e"  # Red

                            with st.expander(f"📋 {case['case_number']} - {case['employer']} ({relevance_pct:.0f}% match)", expanded=(relevance_pct >= 70)):
                                col1, col2 = st.columns([3, 1])

                                with col1:
                                    st.markdown(f"**Case:** {case['case_number']}")
                                    st.markdown(f"**Employer:** {case['employer']}")
                                    st.markdown(f"**Worker:** {case['worker']}")
                                    st.markdown(f"**Territory:** {case['territory']}")
                                    st.markdown(f"**Status:** {case['status']} | **Priority:** {case['priority']}")

                                with col2:
                                    st.markdown(f"""
                                    <div style="background: {relevance_color}20; padding: 1rem; border-radius: 8px; border-left: 4px solid {relevance_color};">
                                        <div style="font-size: 2rem; font-weight: 700; color: {relevance_color};">{relevance_pct:.0f}%</div>
                                        <div style="font-size: 0.75rem; opacity: 0.8;">Relevance</div>
                                    </div>
                                    """, unsafe_allow_html=True)

                                st.markdown("---")
                                st.markdown("**Matched Content:**")
                                st.info(matched_text[:500] + ("..." if len(matched_text) > 500 else ""))

                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("View Full Case", key=f"view_{case['id']}"):
                                        st.session_state.current_case_id = case['id']
                                        st.session_state.current_page = 'Cases'
                                        st.session_state.show_case_details = True
                                        st.rerun()

                                with col2:
                                    if st.button("Find Similar", key=f"similar_{case['id']}"):
                                        st.session_state.reference_case_id = case['id']
                                        st.session_state.switch_to_similar = True
                                        st.rerun()
                    else:
                        st.warning(f"No cases found matching '{search_query}' with relevance ≥ {min_relevance}%")
            else:
                st.info("Enter a search query to begin")

    # TAB 2: SIMILAR CASE FINDER
    with search_tabs[1]:
        st.subheader("Find Similar Cases")
        st.caption("Find cases similar to a reference case based on description, incidents, and patterns")

        # Select reference case
        case_options = {f"{c['case_number']} - {c['employer']}": c['id'] for c in all_cases}

        # Auto-select if coming from search results
        default_case = None
        if st.session_state.get('switch_to_similar') and st.session_state.get('reference_case_id'):
            ref_case = db.get_case_by_id(st.session_state.reference_case_id)
            if ref_case:
                default_case = f"{ref_case['case_number']} - {ref_case['employer']}"
            st.session_state.switch_to_similar = False

        reference_case_name = st.selectbox(
            "Select Reference Case:",
            options=list(case_options.keys()),
            index=list(case_options.keys()).index(default_case) if default_case in case_options.keys() else 0
        )

        reference_case_id = case_options[reference_case_name]
        reference_case = db.get_case_by_id(reference_case_id)

        col1, col2 = st.columns(2)
        with col1:
            num_similar = st.slider("Number of similar cases to find:", 1, 10, 5)
        with col2:
            similarity_threshold = st.slider("Minimum Similarity %:", 0, 100, 40)

        if st.button("🎯 Find Similar Cases", use_container_width=True):
            with st.spinner("Analyzing case similarities..."):
                similar_cases = find_similar_cases(
                    all_cases,
                    reference_case,
                    num_similar,
                    similarity_threshold/100
                )

                if similar_cases:
                    st.success(f"Found {len(similar_cases)} similar cases!")

                    st.markdown("---")
                    st.markdown("**Reference Case:**")
                    with st.container():
                        st.markdown(f"**{reference_case['case_number']}** - {reference_case['employer']}")
                        st.caption(f"{reference_case['description'][:200]}...")

                    st.markdown("---")
                    st.markdown("**Similar Cases:**")

                    for similar_case, similarity_score in similar_cases:
                        similarity_pct = similarity_score * 100

                        with st.expander(f"📋 {similar_case['case_number']} - {similar_case['employer']} ({similarity_pct:.0f}% similar)"):
                            col1, col2 = st.columns([3, 1])

                            with col1:
                                st.markdown(f"**Case:** {similar_case['case_number']}")
                                st.markdown(f"**Employer:** {similar_case['employer']}")
                                st.markdown(f"**Worker:** {similar_case['worker']}")
                                st.markdown(f"**Status:** {similar_case['status']} | **Priority:** {similar_case['priority']}")
                                st.markdown(f"**Description:** {similar_case['description']}")

                            with col2:
                                st.metric("Similarity", f"{similarity_pct:.0f}%")

                            if st.button("View Case", key=f"view_similar_{similar_case['id']}"):
                                st.session_state.current_case_id = similar_case['id']
                                st.session_state.current_page = 'Cases'
                                st.session_state.show_case_details = True
                                st.rerun()
                else:
                    st.warning(f"No similar cases found with similarity ≥ {similarity_threshold}%")

    # TAB 3: AUTO-TAG CASES
    with search_tabs[2]:
        st.subheader("Auto-Tag Cases")
        st.caption("Automatically extract keywords and tags from case descriptions")

        col1, col2 = st.columns(2)
        with col1:
            num_tags = st.slider("Number of tags per case:", 3, 10, 5)
        with col2:
            tag_cases_filter = st.selectbox("Tag which cases?", ["All Cases", "Open Only", "Under Investigation"])

        if st.button("🏷️ Generate Tags", use_container_width=True):
            with st.spinner("Extracting keywords and generating tags..."):
                # Filter cases
                cases_to_tag = all_cases
                if tag_cases_filter == "Open Only":
                    cases_to_tag = [c for c in all_cases if c['status'] == 'Open']
                elif tag_cases_filter == "Under Investigation":
                    cases_to_tag = [c for c in all_cases if c['status'] == 'Under Investigation']

                tags_by_case = generate_auto_tags(cases_to_tag, num_tags)

                st.success(f"Generated tags for {len(tags_by_case)} cases!")

                for case_id, tags in tags_by_case.items():
                    case = db.get_case_by_id(case_id)
                    if case:
                        with st.expander(f"📋 {case['case_number']} - {case['employer']}"):
                            st.markdown("**Auto-Generated Tags:**")
                            tag_html = " ".join([f"<span style='background: #2c5282; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; margin: 0.25rem; display: inline-block; font-size: 0.85rem;'>{tag}</span>" for tag in tags])
                            st.markdown(tag_html, unsafe_allow_html=True)

                            st.markdown("**Description:**")
                            st.caption(case['description'])


def perform_semantic_search(cases, query, scope, min_relevance, max_results):
    """Perform semantic search using TF-IDF vectorization"""
    # Prepare documents based on scope
    documents = []
    case_map = []

    for case in cases:
        doc_text = ""

        if "All Fields" in scope:
            doc_text = f"{case['description']} {case.get('employer', '')} {case.get('worker', '')}"
            # Add timeline events
            for event in case.get('timelines', []):
                doc_text += f" {event.get('description', '')}"
            # Add reports
            for report in case.get('reports', []):
                doc_text += f" {report.get('content', '')}"
            # Add evidence
            for evidence in case.get('evidence', []):
                doc_text += f" {evidence.get('description', '')}"
            # Add briefing note
            doc_text += f" {case.get('briefing_note', '')}"

        elif "Description Only" in scope:
            doc_text = case['description']

        elif "Reports Only" in scope:
            for report in case.get('reports', []):
                doc_text += f" {report.get('content', '')}"

        elif "Timeline Events" in scope:
            for event in case.get('timelines', []):
                doc_text += f" {event.get('description', '')}"

        elif "Evidence" in scope:
            for evidence in case.get('evidence', []):
                doc_text += f" {evidence.get('description', '')}"

        if doc_text.strip():
            documents.append(doc_text)
            case_map.append((case, doc_text))

    if not documents:
        return []

    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    try:
        tfidf_matrix = vectorizer.fit_transform(documents)

        # Transform query
        query_vec = vectorizer.transform([query])

        # Calculate cosine similarity
        similarities = cosine_similarity(query_vec, tfidf_matrix)[0]

        # Get results above threshold
        results = []
        for idx, score in enumerate(similarities):
            if score >= min_relevance:
                case, matched_text = case_map[idx]
                results.append((case, score, matched_text))

        # Sort by relevance and limit results
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:max_results]

    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return []


def find_similar_cases(all_cases, reference_case, num_similar, threshold):
    """Find cases similar to a reference case using TF-IDF"""
    # Prepare documents
    documents = []
    case_map = {}

    for case in all_cases:
        if case['id'] != reference_case['id']:  # Exclude reference case
            doc_text = f"{case['description']} {case.get('employer', '')} {case.get('worker', '')}"
            # Add timeline
            for event in case.get('timelines', []):
                doc_text += f" {event.get('description', '')}"

            documents.append(doc_text)
            case_map[len(documents) - 1] = case

    if not documents:
        return []

    # Add reference case
    ref_text = f"{reference_case['description']} {reference_case.get('employer', '')} {reference_case.get('worker', '')}"
    for event in reference_case.get('timelines', []):
        ref_text += f" {event.get('description', '')}"

    documents.append(ref_text)

    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
    try:
        tfidf_matrix = vectorizer.fit_transform(documents)

        # Reference is last document
        ref_vec = tfidf_matrix[-1]
        other_vecs = tfidf_matrix[:-1]

        # Calculate similarities
        similarities = cosine_similarity(ref_vec, other_vecs)[0]

        # Get similar cases
        similar_cases = []
        for idx, score in enumerate(similarities):
            if score >= threshold:
                similar_cases.append((case_map[idx], score))

        # Sort by similarity
        similar_cases.sort(key=lambda x: x[1], reverse=True)
        return similar_cases[:num_similar]

    except Exception as e:
        st.error(f"Similarity search error: {str(e)}")
        return []


def generate_auto_tags(cases, num_tags):
    """Generate automatic tags for cases using TF-IDF"""
    tags_by_case = {}

    # Common words to exclude
    stop_words = set(['case', 'incident', 'worker', 'employer', 'investigation', 'wscc', 'report', 'date'])

    for case in cases:
        text = case.get('description', '')

        if not text:
            continue

        # Extract potential tags using TF-IDF on single document
        try:
            vectorizer = TfidfVectorizer(stop_words='english', max_features=num_tags*2)
            tfidf = vectorizer.fit_transform([text])

            # Get feature names and scores
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf.toarray()[0]

            # Get top tags
            tag_indices = scores.argsort()[-num_tags:][::-1]
            tags = [feature_names[i].title() for i in tag_indices if feature_names[i] not in stop_words]

            # Add industry-specific tags
            text_lower = text.lower()
            if 'electric' in text_lower or 'electrical' in text_lower:
                tags.append('Electrical')
            if 'fall' in text_lower or 'falling' in text_lower:
                tags.append('Fall Hazard')
            if 'scaffold' in text_lower:
                tags.append('Scaffolding')
            if 'mining' in text_lower or 'mine' in text_lower:
                tags.append('Mining')
            if 'construction' in text_lower:
                tags.append('Construction')
            if 'ppe' in text_lower or 'protection equipment' in text_lower:
                tags.append('PPE')

            # Remove duplicates and limit
            tags = list(dict.fromkeys(tags))[:num_tags]

            tags_by_case[case['id']] = tags

        except:
            # Fallback: simple keyword extraction
            words = re.findall(r'\b[a-z]{4,}\b', text.lower())
            unique_words = list(dict.fromkeys(words))[:num_tags]
            tags_by_case[case['id']] = [w.title() for w in unique_words if w not in stop_words]

    return tags_by_case

# ==================== PAGE: CASES ====================
def render_cases():
    """Render cases page"""
    st.title("📁 Case Management")
    st.caption("Manage all investigation cases")

    # Action buttons
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        search = st.text_input("🔍 Search cases...", placeholder="Search by case number, employer, worker...")

    with col2:
        territory_filter = st.selectbox("Territory", ["All", "Northwest Territories", "Nunavut"])

    with col3:
        status_filter = st.selectbox("Status", ["All", "Open", "Under Investigation", "Closed"])

    with col4:
        if st.button("➕ Add New Case", use_container_width=True):
            st.session_state.show_add_case_form = True
            st.rerun()

    # Add case form
    if st.session_state.get('show_add_case_form', False):
        with st.expander("➕ Add New Case", expanded=True):
            with st.form("add_case_form"):
                col1, col2 = st.columns(2)

                with col1:
                    case_number = st.text_input("Case Number *", placeholder="WSCC-2024-XXX")
                    territory = st.selectbox("Territory *", ["Northwest Territories", "Nunavut"])
                    employer = st.text_input("Employer *", placeholder="Company name")
                    worker = st.text_input("Worker *", placeholder="Worker name")

                with col2:
                    incident_date = st.date_input("Incident Date")
                    reported_date = st.date_input("Reported Date")
                    status = st.selectbox("Status", ["Open", "Under Investigation", "Closed"])
                    priority = st.selectbox("Priority", ["Low", "Medium", "High"])

                description = st.text_area("Description", placeholder="Describe the incident...")

                officers = db.get_all_officers(active_only=True)
                officer_options = {f"{o['name']} ({o['role']})": o['id'] for o in officers}
                assigned_officers = st.multiselect("Assign Officers", options=list(officer_options.keys()))

                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("✅ Add Case", use_container_width=True)
                with col2:
                    cancel = st.form_submit_button("❌ Cancel", use_container_width=True)

                if submit:
                    if not case_number or not territory or not employer or not worker:
                        st.error("Please fill in all required fields (marked with *)")
                    else:
                        # Create new case
                        new_case = {
                            'id': f"case-{uuid.uuid4().hex[:8]}",
                            'case_number': case_number,
                            'territory': territory,
                            'employer': employer,
                            'worker': worker,
                            'incident_date': incident_date.isoformat() if incident_date else '',
                            'reported_date': reported_date.isoformat() if reported_date else '',
                            'status': status,
                            'priority': priority,
                            'description': description,
                            'assigned_officers': [officer_options[name] for name in assigned_officers],
                            'timelines': [],
                            'reports': [],
                            'tasks': [],
                            'evidence': [],
                            'photos': [],
                            'charges': [],
                            'court': {},
                            'conclusion': {},
                            'briefing_note': '',
                            'created_at': datetime.now().isoformat(),
                            'updated_at': datetime.now().isoformat()
                        }

                        try:
                            db.add_case(new_case)
                            st.success(f"✅ Case {case_number} added successfully!")
                            st.session_state.show_add_case_form = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error adding case: {str(e)}")

                if cancel:
                    st.session_state.show_add_case_form = False
                    st.rerun()

    st.markdown("---")

    # Get and filter cases
    cases = db.get_all_cases()

    # Apply filters
    if search:
        cases = [c for c in cases if
                search.lower() in c['case_number'].lower() or
                search.lower() in c['employer'].lower() or
                search.lower() in c['worker'].lower()]

    if territory_filter != "All":
        cases = [c for c in cases if c['territory'] == territory_filter]

    if status_filter != "All":
        cases = [c for c in cases if c['status'] == status_filter]

    # Display cases
    st.subheader(f"📊 {len(cases)} Cases Found")

    if cases:
        for case in cases:
            with st.container():
                col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 1, 1, 1, 1])

                with col1:
                    st.markdown(f"**{case['case_number']}**")
                    st.caption(f"{case['employer']} - {case['worker']}")

                with col2:
                    st.caption(case['territory'])

                with col3:
                    priority_class = f"priority-{case['priority'].lower()}"
                    st.markdown(f"<span class='{priority_class}'>{case['priority']}</span>", unsafe_allow_html=True)

                with col4:
                    st.caption(case['status'])

                with col5:
                    if st.button("View", key=f"view_case_{case['id']}"):
                        st.session_state.current_case_id = case['id']
                        st.session_state.show_case_details = True
                        st.rerun()

                with col6:
                    if st.button("🗑️", key=f"delete_case_{case['id']}"):
                        st.session_state.delete_case_id = case['id']
                        st.rerun()

                st.markdown("---")

        # Delete confirmation
        if st.session_state.get('delete_case_id'):
            case_to_delete = db.get_case_by_id(st.session_state.delete_case_id)
            st.warning(f"⚠️ Are you sure you want to delete case **{case_to_delete['case_number']}**?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, Delete", use_container_width=True):
                    db.delete_case(st.session_state.delete_case_id)
                    st.success("Case deleted successfully!")
                    st.session_state.delete_case_id = None
                    st.rerun()
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.delete_case_id = None
                    st.rerun()
    else:
        st.info("No cases found matching your filters.")

    # Case details view
    if st.session_state.get('show_case_details', False) and st.session_state.current_case_id:
        render_case_details()

def render_case_details():
    """Render detailed case view with ALL tabs fully implemented"""
    case = db.get_case_by_id(st.session_state.current_case_id)

    if not case:
        st.error("Case not found")
        return

    with st.expander(f"📋 Case Details: {case['case_number']}", expanded=True):
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.markdown(f"### {case['case_number']}")

        with col2:
            if st.button("✏️ Edit", use_container_width=True):
                st.session_state.editing_case = not st.session_state.get('editing_case', False)
                st.rerun()

        with col3:
            if st.button("❌ Close", use_container_width=True):
                st.session_state.show_case_details = False
                st.session_state.current_case_id = None
                st.session_state.editing_case = False
                st.rerun()

        # Tabs for different case sections
        tabs = st.tabs([
            "Overview", "Timeline", "Reports", "Tasks", "Evidence",
            "Photos", "Charges", "Court", "Conclusion", "Briefing Note"
        ])

        # TAB 0: OVERVIEW (with edit capability)
        with tabs[0]:
            if st.session_state.get('editing_case', False):
                # Edit mode
                with st.form("edit_case_form"):
                    col1, col2 = st.columns(2)

                    with col1:
                        case_number = st.text_input("Case Number", value=case['case_number'])
                        territory = st.selectbox("Territory", ["Northwest Territories", "Nunavut"],
                                                index=0 if case['territory'] == "Northwest Territories" else 1)
                        employer = st.text_input("Employer", value=case['employer'])
                        worker = st.text_input("Worker", value=case['worker'])

                    with col2:
                        incident_date = st.date_input("Incident Date",
                                                     value=datetime.fromisoformat(case['incident_date']) if case['incident_date'] else None)
                        reported_date = st.date_input("Reported Date",
                                                      value=datetime.fromisoformat(case['reported_date']) if case['reported_date'] else None)
                        status = st.selectbox("Status", ["Open", "Under Investigation", "Closed"],
                                            index=["Open", "Under Investigation", "Closed"].index(case['status']) if case['status'] in ["Open", "Under Investigation", "Closed"] else 0)
                        priority = st.selectbox("Priority", ["Low", "Medium", "High"],
                                              index=["Low", "Medium", "High"].index(case['priority']) if case['priority'] in ["Low", "Medium", "High"] else 1)

                    description = st.text_area("Description", value=case.get('description', ''))

                    officers = db.get_all_officers(active_only=True)
                    officer_options = {f"{o['name']} ({o['role']})": o['id'] for o in officers}
                    current_officers = [f"{db.get_officer_by_id(oid)['name']} ({db.get_officer_by_id(oid)['role']})"
                                       for oid in case.get('assigned_officers', []) if db.get_officer_by_id(oid)]
                    assigned_officers = st.multiselect("Assign Officers",
                                                      options=list(officer_options.keys()),
                                                      default=current_officers)

                    col1, col2 = st.columns(2)
                    with col1:
                        submit = st.form_submit_button("💾 Save Changes", use_container_width=True)
                    with col2:
                        cancel = st.form_submit_button("❌ Cancel", use_container_width=True)

                    if submit:
                        updates = {
                            'case_number': case_number,
                            'territory': territory,
                            'employer': employer,
                            'worker': worker,
                            'incident_date': incident_date.isoformat() if incident_date else '',
                            'reported_date': reported_date.isoformat() if reported_date else '',
                            'status': status,
                            'priority': priority,
                            'description': description,
                            'assigned_officers': [officer_options[name] for name in assigned_officers]
                        }

                        db.update_case(case['id'], updates)
                        st.success("✅ Case updated successfully!")
                        st.session_state.editing_case = False
                        st.rerun()

                    if cancel:
                        st.session_state.editing_case = False
                        st.rerun()
            else:
                # View mode
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Case Information:**")
                    st.write(f"**Case Number:** {case['case_number']}")
                    st.write(f"**Territory:** {case['territory']}")
                    st.write(f"**Status:** {case['status']}")
                    st.write(f"**Priority:** {case['priority']}")

                with col2:
                    st.markdown("**Involved Parties:**")
                    st.write(f"**Employer:** {case['employer']}")
                    st.write(f"**Worker:** {case['worker']}")
                    st.write(f"**Incident Date:** {case['incident_date']}")
                    st.write(f"**Reported Date:** {case['reported_date']}")

                st.markdown("**Description:**")
                st.write(case['description'])

                st.markdown("**Assigned Officers:**")
                if case.get('assigned_officers'):
                    for officer_id in case['assigned_officers']:
                        officer = db.get_officer_by_id(officer_id)
                        if officer:
                            st.write(f"- {officer['name']} ({officer['role']})")
                else:
                    st.info("No officers assigned")

        # TAB 1: TIMELINE
        with tabs[1]:
            st.subheader("📅 Timeline Events")

            # Add timeline event
            with st.form("add_timeline_event"):
                col1, col2 = st.columns([3, 1])

                with col1:
                    event_description = st.text_area("Event Description", placeholder="Describe what happened...")

                with col2:
                    event_date = st.date_input("Event Date")
                    event_type = st.selectbox("Event Type", [
                        "Investigation", "Interview", "Site Visit", "Evidence Collection",
                        "Report Filed", "Meeting", "Other"
                    ])

                if st.form_submit_button("➕ Add Event"):
                    if event_description:
                        timeline_event = {
                            'id': f"event-{uuid.uuid4().hex[:8]}",
                            'date': event_date.isoformat(),
                            'type': event_type,
                            'description': event_description,
                            'created_at': datetime.now().isoformat()
                        }

                        timelines = case.get('timelines', [])
                        timelines.append(timeline_event)
                        db.update_case(case['id'], {'timelines': timelines})

                        st.success("✅ Event added to timeline!")
                        st.rerun()

            st.markdown("---")

            # Display timeline events
            timelines = case.get('timelines', [])
            if timelines:
                # Sort by date
                sorted_timelines = sorted(timelines, key=lambda x: x['date'], reverse=True)

                for event in sorted_timelines:
                    st.markdown(f"""
                    <div class="timeline-event">
                        <strong>{event['date']}</strong> - <span style="color: #2c5282; font-weight: 600;">{event['type']}</span><br>
                        {event['description']}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No timeline events yet. Add the first event above.")

        # TAB 2: REPORTS
        with tabs[2]:
            st.subheader("📄 Investigation Reports")

            # Add report
            with st.form("add_report"):
                report_title = st.text_input("Report Title", placeholder="e.g., Initial Investigation Report")
                report_content = st.text_area("Report Content", height=200,
                                             placeholder="Enter report details...")
                report_type = st.selectbox("Report Type", [
                    "Initial Investigation", "Progress Report", "Final Report",
                    "Witness Statement", "Technical Analysis", "Other"
                ])

                if st.form_submit_button("➕ Add Report"):
                    if report_title and report_content:
                        report = {
                            'id': f"report-{uuid.uuid4().hex[:8]}",
                            'title': report_title,
                            'content': report_content,
                            'type': report_type,
                            'created_at': datetime.now().isoformat(),
                            'created_by': "Current User"  # Can be enhanced with user auth
                        }

                        reports = case.get('reports', [])
                        reports.append(report)
                        db.update_case(case['id'], {'reports': reports})

                        st.success("✅ Report added successfully!")
                        st.rerun()

            st.markdown("---")

            # Display reports
            reports = case.get('reports', [])
            if reports:
                for report in reports:
                    with st.expander(f"📋 {report['title']} - {report['type']}"):
                        st.caption(f"Created: {report['created_at']} by {report['created_by']}")
                        st.markdown(report['content'])
            else:
                st.info("No reports yet. Add the first report above.")

        # TAB 3: TASKS
        with tabs[3]:
            st.subheader("✅ Tasks")

            # Add task
            with st.form("add_task"):
                col1, col2 = st.columns([3, 1])

                with col1:
                    task_description = st.text_input("Task Description", placeholder="What needs to be done?")

                with col2:
                    task_due_date = st.date_input("Due Date")
                    task_status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])

                officers = db.get_all_officers(active_only=True)
                task_assigned_to = st.selectbox("Assign To", options=[f"{o['name']}" for o in officers])

                if st.form_submit_button("➕ Add Task"):
                    if task_description:
                        task = {
                            'id': f"task-{uuid.uuid4().hex[:8]}",
                            'description': task_description,
                            'due_date': task_due_date.isoformat(),
                            'status': task_status,
                            'assigned_to': task_assigned_to,
                            'created_at': datetime.now().isoformat()
                        }

                        tasks = case.get('tasks', [])
                        tasks.append(task)
                        db.update_case(case['id'], {'tasks': tasks})

                        st.success("✅ Task added successfully!")
                        st.rerun()

            st.markdown("---")

            # Display tasks
            tasks = case.get('tasks', [])
            if tasks:
                for task in tasks:
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        status_emoji = "✅" if task['status'] == "Completed" else "⏳" if task['status'] == "In Progress" else "📋"
                        st.write(f"{status_emoji} {task['description']}")
                        st.caption(f"Assigned to: {task['assigned_to']} | Due: {task['due_date']}")

                    with col2:
                        st.caption(task['status'])

                    with col3:
                        if st.button("Complete", key=f"complete_task_{task['id']}"):
                            # Update task status
                            for t in tasks:
                                if t['id'] == task['id']:
                                    t['status'] = "Completed"
                            db.update_case(case['id'], {'tasks': tasks})
                            st.rerun()

                    st.markdown("---")
            else:
                st.info("No tasks yet. Add the first task above.")

        # TAB 4: EVIDENCE
        with tabs[4]:
            st.subheader("🔍 Evidence Log")

            # Add evidence
            with st.form("add_evidence"):
                col1, col2 = st.columns(2)

                with col1:
                    evidence_type = st.selectbox("Evidence Type", [
                        "Physical", "Digital", "Documentary", "Testimonial", "Photographic", "Other"
                    ])
                    evidence_description = st.text_area("Description", placeholder="Describe the evidence...")

                with col2:
                    evidence_location = st.text_input("Location/Storage", placeholder="Where is it stored?")
                    evidence_collected_by = st.text_input("Collected By", placeholder="Officer name")
                    evidence_date = st.date_input("Collection Date")

                if st.form_submit_button("➕ Add Evidence"):
                    if evidence_description:
                        evidence = {
                            'id': f"evidence-{uuid.uuid4().hex[:8]}",
                            'type': evidence_type,
                            'description': evidence_description,
                            'location': evidence_location,
                            'collected_by': evidence_collected_by,
                            'collection_date': evidence_date.isoformat(),
                            'created_at': datetime.now().isoformat()
                        }

                        evidence_list = case.get('evidence', [])
                        evidence_list.append(evidence)
                        db.update_case(case['id'], {'evidence': evidence_list})

                        st.success("✅ Evidence logged successfully!")
                        st.rerun()

            st.markdown("---")

            # Display evidence
            evidence_list = case.get('evidence', [])
            if evidence_list:
                for evidence in evidence_list:
                    with st.expander(f"📦 {evidence['type']} Evidence - {evidence['collection_date']}"):
                        st.write(f"**Description:** {evidence['description']}")
                        st.write(f"**Location:** {evidence['location']}")
                        st.write(f"**Collected By:** {evidence['collected_by']}")
                        st.caption(f"Logged: {evidence['created_at']}")
            else:
                st.info("No evidence logged yet.")

        # TAB 5: PHOTOS
        with tabs[5]:
            st.subheader("📸 Photos")

            # Photo upload
            uploaded_file = st.file_uploader("Upload Photo", type=['jpg', 'jpeg', 'png'])
            if uploaded_file:
                col1, col2 = st.columns(2)

                with col1:
                    photo_description = st.text_input("Photo Description")

                with col2:
                    photo_location = st.text_input("Photo Location/Subject")

                if st.button("➕ Add Photo"):
                    if photo_description:
                        # Convert to base64
                        photo_bytes = uploaded_file.read()
                        photo_base64 = base64.b64encode(photo_bytes).decode()

                        photo = {
                            'id': f"photo-{uuid.uuid4().hex[:8]}",
                            'description': photo_description,
                            'location': photo_location,
                            'data': photo_base64,
                            'filename': uploaded_file.name,
                            'uploaded_at': datetime.now().isoformat()
                        }

                        photos = case.get('photos', [])
                        photos.append(photo)
                        db.update_case(case['id'], {'photos': photos})

                        st.success("✅ Photo added successfully!")
                        st.rerun()

            st.markdown("---")

            # Display photos
            photos = case.get('photos', [])
            if photos:
                cols = st.columns(3)
                for idx, photo in enumerate(photos):
                    with cols[idx % 3]:
                        # Decode base64 image
                        image_data = base64.b64decode(photo['data'])
                        st.image(image_data, caption=photo['description'], use_container_width=True)
                        st.caption(f"📍 {photo['location']}")
            else:
                st.info("No photos uploaded yet.")

        # TAB 6: CHARGES
        with tabs[6]:
            st.subheader("⚖️ Charges & Violations")

            # Add charge
            with st.form("add_charge"):
                col1, col2 = st.columns(2)

                with col1:
                    charge_type = st.selectbox("Violation Type", [
                        "Safety Regulation Violation", "Equipment Violation", "Training Violation",
                        "PPE Violation", "Procedural Violation", "Other"
                    ])
                    charge_description = st.text_area("Description")

                with col2:
                    charge_severity = st.selectbox("Severity", ["Minor", "Moderate", "Severe", "Critical"])
                    charge_fine = st.number_input("Fine Amount ($)", min_value=0.0, step=100.0)

                if st.form_submit_button("➕ Add Charge"):
                    if charge_description:
                        charge = {
                            'id': f"charge-{uuid.uuid4().hex[:8]}",
                            'type': charge_type,
                            'description': charge_description,
                            'severity': charge_severity,
                            'fine': charge_fine,
                            'created_at': datetime.now().isoformat()
                        }

                        charges = case.get('charges', [])
                        charges.append(charge)
                        db.update_case(case['id'], {'charges': charges})

                        st.success("✅ Charge added successfully!")
                        st.rerun()

            st.markdown("---")

            # Display charges
            charges = case.get('charges', [])
            if charges:
                total_fines = sum(c.get('fine', 0) for c in charges)
                st.metric("Total Fines", f"${total_fines:,.2f}")

                st.markdown("---")

                for charge in charges:
                    with st.expander(f"⚖️ {charge['type']} - {charge['severity']}"):
                        st.write(f"**Description:** {charge['description']}")
                        st.write(f"**Fine:** ${charge['fine']:,.2f}")
                        st.caption(f"Added: {charge['created_at']}")
            else:
                st.info("No charges filed yet.")

        # TAB 7: COURT
        with tabs[7]:
            st.subheader("🏛️ Court Proceedings")

            court_data = case.get('court', {})

            with st.form("court_info"):
                col1, col2 = st.columns(2)

                with col1:
                    court_case_number = st.text_input("Court Case Number", value=court_data.get('case_number', ''))
                    court_location = st.text_input("Court Location", value=court_data.get('location', ''))
                    judge_name = st.text_input("Judge Name", value=court_data.get('judge', ''))

                with col2:
                    hearing_date = st.date_input("Hearing Date",
                                                 value=datetime.fromisoformat(court_data['hearing_date']) if court_data.get('hearing_date') else None)
                    court_status = st.selectbox("Status", ["Pending", "Scheduled", "In Progress", "Completed"],
                                               index=["Pending", "Scheduled", "In Progress", "Completed"].index(court_data.get('status', 'Pending')) if court_data.get('status') in ["Pending", "Scheduled", "In Progress", "Completed"] else 0)

                court_notes = st.text_area("Court Notes", value=court_data.get('notes', ''), height=200)

                if st.form_submit_button("💾 Save Court Information"):
                    court_info = {
                        'case_number': court_case_number,
                        'location': court_location,
                        'judge': judge_name,
                        'hearing_date': hearing_date.isoformat() if hearing_date else '',
                        'status': court_status,
                        'notes': court_notes,
                        'updated_at': datetime.now().isoformat()
                    }

                    db.update_case(case['id'], {'court': court_info})
                    st.success("✅ Court information updated!")
                    st.rerun()

        # TAB 8: CONCLUSION
        with tabs[8]:
            st.subheader("📝 Case Conclusion")

            conclusion_data = case.get('conclusion', {})

            with st.form("conclusion_form"):
                col1, col2 = st.columns(2)

                with col1:
                    conclusion_status = st.selectbox("Final Status", ["Open", "Closed - Resolved", "Closed - Unresolved"],
                                                    index=["Open", "Closed - Resolved", "Closed - Unresolved"].index(conclusion_data.get('status', 'Open')) if conclusion_data.get('status') in ["Open", "Closed - Resolved", "Closed - Unresolved"] else 0)
                    closure_date = st.date_input("Closure Date",
                                                 value=datetime.fromisoformat(conclusion_data['closure_date']) if conclusion_data.get('closure_date') else None)

                with col2:
                    root_cause = st.text_input("Root Cause", value=conclusion_data.get('root_cause', ''))
                    preventive_measures = st.text_area("Preventive Measures", value=conclusion_data.get('preventive_measures', ''))

                final_findings = st.text_area("Final Findings", value=conclusion_data.get('final_findings', ''), height=200)
                recommendations = st.text_area("Recommendations", value=conclusion_data.get('recommendations', ''), height=150)

                if st.form_submit_button("💾 Save Conclusion"):
                    conclusion_info = {
                        'status': conclusion_status,
                        'closure_date': closure_date.isoformat() if closure_date else '',
                        'root_cause': root_cause,
                        'preventive_measures': preventive_measures,
                        'final_findings': final_findings,
                        'recommendations': recommendations,
                        'completed_by': "Current User",
                        'updated_at': datetime.now().isoformat()
                    }

                    db.update_case(case['id'], {'conclusion': conclusion_info})

                    # Also update case status
                    if conclusion_status.startswith("Closed"):
                        db.update_case(case['id'], {'status': 'Closed'})

                    st.success("✅ Case conclusion saved!")
                    st.rerun()

        # TAB 9: BRIEFING NOTE
        with tabs[9]:
            st.subheader("📋 Briefing Note (BN25-XXX)")

            if st.button("📝 Generate Briefing Note Template"):
                # Generate BN25 template
                bn_template = f"""
BRIEFING NOTE

To: [Executive Director/Commissioner]
From: [Investigation Officer Name]
Date: {datetime.now().strftime('%B %d, %Y')}
Subject: {case['case_number']} - {case['employer']}

ISSUE:
Investigation into workplace incident involving {case['worker']} at {case['employer']}, {case['territory']}.

BACKGROUND:
- Incident Date: {case['incident_date']}
- Reported Date: {case['reported_date']}
- Case Number: {case['case_number']}
- Priority: {case['priority']}

CURRENT SITUATION:
{case['description']}

ANALYSIS:
[Detailed analysis of investigation findings]

RECOMMENDATIONS:
[Investigation recommendations]

NEXT STEPS:
[Proposed next steps]

---
⚠️ REMINDER: De-identify all personal information before sharing this briefing note.
"""

                briefing_note = st.text_area("Briefing Note Content", value=case.get('briefing_note', bn_template), height=400)

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("💾 Save Briefing Note", use_container_width=True):
                        db.update_case(case['id'], {'briefing_note': briefing_note})
                        st.success("✅ Briefing note saved!")

                with col2:
                    if st.button("📥 Download as Text", use_container_width=True):
                        st.download_button(
                            label="⬇️ Download",
                            data=briefing_note,
                            file_name=f"BN25_{case['case_number']}_{datetime.now().strftime('%Y%m%d')}.txt",
                            mime="text/plain"
                        )
            else:
                if case.get('briefing_note'):
                    st.markdown("**Saved Briefing Note:**")
                    st.text_area("", value=case['briefing_note'], height=300, disabled=True)
                else:
                    st.info("Click 'Generate Briefing Note Template' to create a new briefing note.")

# ==================== PAGE: OFFICERS ====================
def render_officers():
    """Render officers page with edit/delete"""
    st.title("👥 Officer Management")
    st.caption("Manage investigation officers and assignments")

    col1, col2 = st.columns([3, 1])

    with col1:
        search = st.text_input("🔍 Search officers...", placeholder="Search by name or role...")

    with col2:
        if st.button("➕ Add New Officer", use_container_width=True):
            st.session_state.show_add_officer_form = True
            st.rerun()

    # Add officer form (same as before)
    if st.session_state.get('show_add_officer_form', False):
        with st.expander("➕ Add New Officer", expanded=True):
            with st.form("add_officer_form"):
                col1, col2 = st.columns(2)

                with col1:
                    name = st.text_input("Name *", placeholder="Full name")
                    role = st.text_input("Role *", placeholder="e.g., Senior Investigator")
                    work_location = st.text_input("Work Location", placeholder="City")

                with col2:
                    experience = st.text_input("Experience", placeholder="e.g., 5 years")
                    specialization = st.text_input("Specialization", placeholder="Area of expertise")
                    contact = st.text_input("Contact", placeholder="Email or phone")

                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("✅ Add Officer", use_container_width=True)
                with col2:
                    cancel = st.form_submit_button("❌ Cancel", use_container_width=True)

                if submit:
                    if not name or not role:
                        st.error("Please fill in all required fields (marked with *)")
                    else:
                        new_officer = {
                            'id': f"officer-{uuid.uuid4().hex[:8]}",
                            'name': name,
                            'role': role,
                            'work_location': work_location,
                            'experience': experience,
                            'specialization': specialization,
                            'contact': contact,
                            'active': 1,
                            'created_at': datetime.now().isoformat(),
                            'updated_at': datetime.now().isoformat()
                        }

                        try:
                            db.add_officer(new_officer)
                            st.success(f"✅ Officer {name} added successfully!")
                            st.session_state.show_add_officer_form = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error adding officer: {str(e)}")

                if cancel:
                    st.session_state.show_add_officer_form = False
                    st.rerun()

    st.markdown("---")

    # Get and display officers
    officers = db.get_all_officers()

    # Apply search filter
    if search:
        officers = [o for o in officers if
                   search.lower() in o['name'].lower() or
                   search.lower() in o['role'].lower()]

    st.subheader(f"👥 {len(officers)} Officers")

    if officers:
        for officer in officers:
            with st.expander(f"👤 {officer['name']} - {officer['role']}"):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**Name:** {officer['name']}")
                    st.write(f"**Role:** {officer['role']}")
                    st.write(f"**Location:** {officer.get('work_location', 'N/A')}")
                    st.write(f"**Experience:** {officer.get('experience', 'N/A')}")
                    st.write(f"**Specialization:** {officer.get('specialization', 'N/A')}")
                    st.write(f"**Contact:** {officer.get('contact', 'N/A')}")

                with col2:
                    if officer['active']:
                        st.success("✅ Active")
                    else:
                        st.error("❌ Inactive")

                    if st.button("✏️ Edit", key=f"edit_officer_{officer['id']}"):
                        st.session_state.editing_officer_id = officer['id']
                        st.rerun()

                    if officer['active'] and st.button("🚫 Deactivate", key=f"deactivate_{officer['id']}"):
                        db.delete_officer(officer['id'])
                        st.success(f"Officer {officer['name']} deactivated!")
                        st.rerun()

                # Edit form
                if st.session_state.get('editing_officer_id') == officer['id']:
                    st.markdown("---")
                    st.markdown("**Edit Officer:**")

                    with st.form(f"edit_officer_form_{officer['id']}"):
                        col1, col2 = st.columns(2)

                        with col1:
                            name = st.text_input("Name", value=officer['name'])
                            role = st.text_input("Role", value=officer['role'])
                            work_location = st.text_input("Work Location", value=officer.get('work_location', ''))

                        with col2:
                            experience = st.text_input("Experience", value=officer.get('experience', ''))
                            specialization = st.text_input("Specialization", value=officer.get('specialization', ''))
                            contact = st.text_input("Contact", value=officer.get('contact', ''))

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Save", use_container_width=True):
                                updates = {
                                    'name': name,
                                    'role': role,
                                    'work_location': work_location,
                                    'experience': experience,
                                    'specialization': specialization,
                                    'contact': contact
                                }
                                db.update_officer(officer['id'], updates)
                                st.success("✅ Officer updated!")
                                st.session_state.editing_officer_id = None
                                st.rerun()

                        with col2:
                            if st.form_submit_button("❌ Cancel", use_container_width=True):
                                st.session_state.editing_officer_id = None
                                st.rerun()
    else:
        st.info("No officers found.")

# ==================== PAGE: REPORTS ====================
def render_reports():
    """Render reports page with actual report generation"""
    st.title("📄 Reports & Export")
    st.caption("Generate reports and export data")

    st.subheader("📊 Generate Territory Reports")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📄 NWT Report", use_container_width=True):
            cases = [c for c in db.get_all_cases() if c['territory'] == 'Northwest Territories']
            if cases:
                # Generate report
                report_html = generate_territory_report("Northwest Territories", cases)
                st.download_button(
                    label="⬇️ Download NWT Report",
                    data=report_html,
                    file_name=f"NWT_Report_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html"
                )
                st.success(f"✅ NWT Report generated! ({len(cases)} cases)")
            else:
                st.warning("No NWT cases found")

    with col2:
        if st.button("📄 Nunavut Report", use_container_width=True):
            cases = [c for c in db.get_all_cases() if c['territory'] == 'Nunavut']
            if cases:
                report_html = generate_territory_report("Nunavut", cases)
                st.download_button(
                    label="⬇️ Download Nunavut Report",
                    data=report_html,
                    file_name=f"Nunavut_Report_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html"
                )
                st.success(f"✅ Nunavut Report generated! ({len(cases)} cases)")
            else:
                st.warning("No Nunavut cases found")

    with col3:
        if st.button("📄 Combined Report", use_container_width=True):
            cases = db.get_all_cases()
            if cases:
                report_html = generate_territory_report("All Territories", cases)
                st.download_button(
                    label="⬇️ Download Combined Report",
                    data=report_html,
                    file_name=f"Combined_Report_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html"
                )
                st.success(f"✅ Combined Report generated! ({len(cases)} cases)")
            else:
                st.warning("No cases found")

    st.markdown("---")

    st.subheader("💾 Data Export/Import")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Export Data:**")

        # JSON Export
        if st.button("📥 Export to JSON", use_container_width=True):
            data = db.export_to_json()
            json_str = json.dumps(data, indent=2)
            st.download_button(
                label="⬇️ Download JSON",
                data=json_str,
                file_name=f"wscc_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

        # CSV Export
        if st.button("📥 Export to CSV", use_container_width=True):
            cases = db.get_all_cases()
            if cases:
                # Create DataFrame
                df_data = []
                for case in cases:
                    df_data.append({
                        'Case Number': case['case_number'],
                        'Territory': case['territory'],
                        'Employer': case['employer'],
                        'Worker': case['worker'],
                        'Incident Date': case['incident_date'],
                        'Status': case['status'],
                        'Priority': case['priority'],
                        'Description': case['description']
                    })

                df = pd.DataFrame(df_data)
                csv = df.to_csv(index=False)

                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv,
                    file_name=f"wscc_cases_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    with col2:
        st.markdown("**Import Data:**")
        uploaded_file = st.file_uploader("📤 Upload JSON file", type=['json'])

        if uploaded_file:
            try:
                data = json.load(uploaded_file)

                st.write(f"**File contains:**")
                st.write(f"- {len(data.get('cases', []))} cases")
                st.write(f"- {len(data.get('officers', []))} officers")

                if st.button("✅ Import Data", use_container_width=True):
                    db.import_from_json(data)
                    st.success("✅ Data imported successfully!")
                    st.rerun()

            except Exception as e:
                st.error(f"Error importing data: {str(e)}")

def generate_territory_report(territory, cases):
    """Generate professional HTML report matching master project style"""

    # Calculate statistics
    active_cases = [c for c in cases if c['status'] in ['Open', 'Under Investigation']]
    closed_cases = [c for c in cases if c['status'] == 'Closed']

    # Status breakdown
    status_breakdown = {}
    for case in active_cases:
        status = case['status']
        status_breakdown[status] = status_breakdown.get(status, 0) + 1

    # Priority breakdown
    priority_breakdown = {}
    for case in cases:
        priority = case['priority']
        priority_breakdown[priority] = priority_breakdown.get(priority, 0) + 1

    # Officer workload
    officer_workload = {}
    for case in active_cases:
        officers = case.get('assigned_officers', [])
        if officers:
            for officer_id in officers:
                officer = db.get_officer_by_id(officer_id)
                if officer:
                    name = officer['name']
                    officer_workload[name] = officer_workload.get(name, 0) + 1
        else:
            officer_workload['Unassigned'] = officer_workload.get('Unassigned', 0) + 1

    # Generate unique report ID
    now = datetime.now()
    report_id = f"WSCC-{territory.upper().replace(' ', '')}-{now.strftime('%Y%m')}"
    month_name = now.strftime('%B')
    year = now.strftime('%Y')

    # Helper function to create bar chart
    def create_bar_chart(data, label_text="Value"):
        if not data:
            return '<p>No data available</p>'

        max_count = max(data.values()) if data.values() else 1
        bars_html = ""
        for label, count in sorted(data.items(), key=lambda x: x[1], reverse=True)[:6]:
            percentage = (count / max_count) * 100
            bars_html += f"""
                <div class="bar-item">
                    <div class="bar-label">{label}</div>
                    <div class="bar-wrapper">
                        <div class="bar-fill" style="width: {percentage}%">{count}</div>
                    </div>
                </div>
            """
        return bars_html

    # Generate HTML
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WSCC Investigation Report - {territory} - {month_name} {year}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        @page {{
            size: letter;
            margin: 0.75in;
        }}

        body {{
            font-family: 'Calibri', 'Segoe UI', 'Arial', sans-serif;
            line-height: 1.6;
            color: #1a1a1a;
            background: #ffffff;
        }}

        .report-container {{
            max-width: 8.5in;
            margin: 0 auto;
            background: white;
        }}

        /* Cover Page */
        .cover-page {{
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            page-break-after: always;
            background: #1a2332;
        }}

        .cover-header {{
            background: #1a2332;
            color: white;
            padding: 2.5rem 3rem;
            border-bottom: 6px solid #5eead4;
            box-shadow: 0 4px 24px rgba(94, 234, 212, 0.15);
        }}

        .wscc-badge {{
            display: flex;
            align-items: center;
            gap: 1.5rem;
            margin-bottom: 1.5rem;
        }}

        .wscc-shield {{
            width: 80px;
            height: 80px;
            background: rgba(255, 255, 255, 0.15);
            border: 3px solid rgba(94, 234, 212, 0.8);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            color: #5eead4;
            box-shadow: 0 4px 12px rgba(94, 234, 212, 0.3);
        }}

        .wscc-title h1 {{
            font-size: 1.75rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            margin-bottom: 0.25rem;
        }}

        .wscc-title .subtitle {{
            font-size: 1rem;
            opacity: 0.95;
            font-weight: 400;
            letter-spacing: 1px;
        }}

        .report-title-section {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 3rem;
            text-align: center;
        }}

        .report-title {{
            font-size: 2.75rem;
            font-weight: 700;
            color: white;
            margin-bottom: 1rem;
            line-height: 1.2;
        }}

        .report-subtitle {{
            font-size: 1.5rem;
            color: #5eead4;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }}

        .report-period {{
            font-size: 1.75rem;
            color: #90cdf4;
            margin-bottom: 3rem;
            font-weight: 400;
        }}

        .report-metadata {{
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            padding: 2rem;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }}

        .metadata-row {{
            display: flex;
            padding: 0.75rem 0;
            border-bottom: 1px solid #e2e8f0;
        }}

        .metadata-row:last-child {{
            border-bottom: none;
        }}

        .metadata-label {{
            font-weight: 600;
            color: #4a5568;
            width: 140px;
            flex-shrink: 0;
        }}

        .metadata-value {{
            color: #1a2332;
            font-weight: 500;
        }}

        .classification-badge {{
            display: inline-block;
            padding: 0.5rem 1.5rem;
            background: #2c5282;
            color: white;
            border-radius: 4px;
            font-weight: 700;
            letter-spacing: 1px;
            box-shadow: 0 2px 8px rgba(94, 234, 212, 0.3);
        }}

        .cover-footer {{
            padding: 2rem 3rem;
            background: #f8f9fa;
            border-top: 1px solid #e2e8f0;
            text-align: center;
        }}

        .confidentiality-notice {{
            background: #fff3e0;
            border-left: 4px solid #f59e0b;
            padding: 1rem 1.5rem;
            margin-bottom: 1rem;
            font-size: 0.875rem;
            color: #78350f;
            line-height: 1.6;
        }}

        .government-acknowledgment {{
            font-size: 0.75rem;
            color: #6c757d;
            font-style: italic;
        }}

        /* Content Page */
        .content-page {{
            padding: 2rem 3rem;
        }}

        .executive-summary {{
            background: linear-gradient(135deg, rgba(26, 35, 50, 0.03) 0%, rgba(30, 58, 95, 0.05) 100%);
            border: 2px solid rgba(94, 234, 212, 0.2);
            border-left: 6px solid #5eead4;
            padding: 2rem;
            margin-bottom: 2rem;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(94, 234, 212, 0.1);
        }}

        .executive-summary h2 {{
            color: #1a2332;
            margin-bottom: 1rem;
            font-size: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .executive-summary h2 i {{
            color: #5eead4;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-bottom: 2rem;
        }}

        .stat-card {{
            background: white;
            border: 2px solid rgba(94, 234, 212, 0.15);
            padding: 1.25rem;
            border-radius: 6px;
            text-align: center;
            box-shadow: 0 2px 6px rgba(94, 234, 212, 0.05);
        }}

        .stat-card.primary {{
            border-left: 5px solid #5eead4;
        }}

        .stat-card.warning {{
            border-left: 5px solid #f59e0b;
            background: #fffbeb;
        }}

        .stat-card.danger {{
            border-left: 5px solid #ef4444;
            background: #fef2f2;
        }}

        .stat-card.success {{
            border-left: 5px solid #10b981;
            background: #f0fdf4;
        }}

        .stat-value {{
            font-size: 2rem;
            font-weight: 700;
            color: #1a2332;
            margin-bottom: 0.5rem;
            line-height: 1;
        }}

        .stat-label {{
            font-size: 0.75rem;
            color: #4a5568;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}

        .section {{
            margin-bottom: 2.5rem;
            page-break-inside: avoid;
        }}

        .section-title {{
            font-size: 1.5rem;
            color: #1a2332;
            border-bottom: 3px solid #5eead4;
            padding-bottom: 0.75rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}

        .section-title i {{
            color: #5eead4;
        }}

        .chart-container {{
            background: white;
            border: 2px solid rgba(94, 234, 212, 0.15);
            padding: 1.5rem;
            border-radius: 6px;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 6px rgba(94, 234, 212, 0.05);
        }}

        .chart-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #1a2332;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #5eead4;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .chart-title i {{
            color: #5eead4;
        }}

        .bar-chart {{
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
        }}

        .bar-item {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}

        .bar-label {{
            min-width: 120px;
            font-size: 0.8rem;
            font-weight: 500;
            color: #4a5568;
        }}

        .bar-wrapper {{
            flex: 1;
            background: #e9ecef;
            border-radius: 4px;
            height: 24px;
            position: relative;
            overflow: hidden;
        }}

        .bar-fill {{
            background: linear-gradient(90deg, #2c5282 0%, #4299e1 100%);
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 6px;
            color: white;
            font-weight: 600;
            font-size: 0.75rem;
            transition: width 0.5s ease;
            box-shadow: 0 2px 6px rgba(94, 234, 212, 0.2);
        }}

        .two-column-charts {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin-bottom: 1.25rem;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
            background: white;
            border: 2px solid rgba(94, 234, 212, 0.15);
            border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 2px 6px rgba(94, 234, 212, 0.05);
        }}

        thead {{
            background: #1a2332;
            color: white;
            box-shadow: 0 2px 8px rgba(94, 234, 212, 0.1);
        }}

        th {{
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            font-size: 0.875rem;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}

        td {{
            padding: 0.875rem 1rem;
            border-bottom: 1px solid #e2e8f0;
            font-size: 0.9rem;
        }}

        tbody tr:nth-child(even) {{
            background: #f8f9fa;
        }}

        tbody tr:hover {{
            background: rgba(94, 234, 212, 0.05);
        }}

        .status-badge {{
            display: inline-block;
            padding: 0.35rem 0.875rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }}

        .status-active {{
            background: #fff3e0;
            color: #e65100;
            border: 1px solid #ffb74d;
        }}

        .status-closed {{
            background: #e8f5e9;
            color: #2e7d32;
            border: 1px solid #66bb6a;
        }}

        .report-footer {{
            margin-top: 3rem;
            padding: 2rem 3rem;
            background: linear-gradient(135deg, rgba(26, 35, 50, 0.03) 0%, rgba(30, 58, 95, 0.05) 100%);
            border-top: 4px solid #5eead4;
            text-align: center;
            box-shadow: 0 -2px 8px rgba(94, 234, 212, 0.1);
        }}

        .footer-logo {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #1a2332;
            margin-bottom: 1rem;
        }}

        .footer-logo i {{
            color: #5eead4;
        }}

        .footer-text {{
            color: #6c757d;
            font-size: 0.875rem;
            margin-bottom: 0.5rem;
        }}

        .footer-confidential {{
            background: #fff3e0;
            border: 1px solid #f59e0b;
            padding: 0.75rem;
            border-radius: 4px;
            margin-top: 1rem;
            font-size: 0.8rem;
            color: #78350f;
            font-weight: 600;
        }}

        .no-print {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 1000;
            display: flex;
            gap: 12px;
        }}

        .no-print button {{
            padding: 16px 32px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 600;
            transition: all 0.3s;
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .btn-print {{
            background: #2c5282;
            color: white;
        }}

        .btn-print:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(44, 82, 130, 0.4);
        }}

        .btn-close {{
            background: white;
            color: #4a5568;
            border: 2px solid #e2e8f0;
        }}

        .btn-close:hover {{
            background: #f8f9fa;
            transform: translateY(-2px);
        }}

        @media print {{
            body {{ padding: 0; background: white; }}
            .report-container {{ box-shadow: none; max-width: 100%; }}
            .no-print {{ display: none !important; }}
            .cover-page {{ page-break-after: always; }}
            .section {{ page-break-inside: avoid; }}
            table {{ page-break-inside: avoid; }}
            .two-column-charts {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <!-- Cover Page -->
        <div class="cover-page">
            <div class="cover-header">
                <div class="wscc-badge">
                    <div class="wscc-shield">
                        <i class="fas fa-shield-alt"></i>
                    </div>
                    <div class="wscc-title">
                        <h1>Workers' Safety & Compensation Commission</h1>
                        <div class="subtitle">{territory if territory != 'All Territories' else 'Northwest Territories & Nunavut'}</div>
                    </div>
                </div>
            </div>

            <div class="report-title-section">
                <div class="report-title">INVESTIGATION REPORT</div>
                <div class="report-subtitle">{territory + ' Territory' if territory != 'All Territories' else 'Combined Territory Analysis'}</div>
                <div class="report-period">{month_name} {year}</div>

                <div class="report-metadata">
                    <div class="metadata-row">
                        <div class="metadata-label">Report ID:</div>
                        <div class="metadata-value">{report_id}</div>
                    </div>
                    <div class="metadata-row">
                        <div class="metadata-label">Generated:</div>
                        <div class="metadata-value">{now.strftime('%B %d, %Y')}</div>
                    </div>
                    <div class="metadata-row">
                        <div class="metadata-label">Time:</div>
                        <div class="metadata-value">{now.strftime('%H:%M')}</div>
                    </div>
                    <div class="metadata-row">
                        <div class="metadata-label">Territory:</div>
                        <div class="metadata-value">{territory}</div>
                    </div>
                    <div class="metadata-row">
                        <div class="metadata-label">Classification:</div>
                        <div class="metadata-value">
                            <span class="classification-badge">OFFICIAL</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="cover-footer">
                <div class="confidentiality-notice">
                    <strong><i class="fas fa-exclamation-triangle"></i> CONFIDENTIALITY NOTICE</strong><br>
                    This document contains confidential information intended for official use only. The information contained herein is protected under applicable privacy legislation and must not be disclosed to unauthorized individuals. Distribution is restricted to authorized WSCC personnel and relevant government officials.
                </div>
                <div class="government-acknowledgment">
                    Prepared by the Workers' Safety & Compensation Commission<br>
                    Government of the Northwest Territories
                </div>
            </div>
        </div>

        <!-- Content Pages -->
        <div class="content-page">
            <!-- Executive Summary -->
            <div class="executive-summary">
                <h2><i class="fas fa-clipboard-list"></i> Executive Summary</h2>
                <p>This report provides a comprehensive overview of workplace safety investigations conducted by the Workers' Safety & Compensation Commission for the {territory} territory during {month_name} {year}. The report includes analysis of active and closed cases, officer workload distribution, incident trends, and compliance status.</p>
            </div>

            <!-- Key Statistics -->
            <div class="section">
                <h2 class="section-title"><i class="fas fa-chart-bar"></i> Key Statistics</h2>
                <div class="stats-grid">
                    <div class="stat-card primary">
                        <div class="stat-value">{len(cases)}</div>
                        <div class="stat-label">Total Cases</div>
                    </div>
                    <div class="stat-card primary">
                        <div class="stat-value">{len(active_cases)}</div>
                        <div class="stat-label">Active Cases</div>
                    </div>
                    <div class="stat-card success">
                        <div class="stat-value">{len(closed_cases)}</div>
                        <div class="stat-label">Closed Cases</div>
                    </div>
                    <div class="stat-card primary">
                        <div class="stat-value">{priority_breakdown.get('High', 0)}</div>
                        <div class="stat-label">High Priority</div>
                    </div>
                </div>
            </div>

            <!-- Analytics Section -->
            <div class="section">
                <h2 class="section-title"><i class="fas fa-chart-pie"></i> Investigation Analytics</h2>

                <div class="two-column-charts">
                    <div class="chart-container">
                        <div class="chart-title"><i class="fas fa-tasks"></i> Case Status Breakdown</div>
                        <div class="bar-chart">
                            {create_bar_chart(status_breakdown)}
                        </div>
                    </div>

                    <div class="chart-container">
                        <div class="chart-title"><i class="fas fa-user-tie"></i> Officer Workload</div>
                        <div class="bar-chart">
                            {create_bar_chart(officer_workload)}
                        </div>
                    </div>
                </div>

                <div class="chart-container">
                    <div class="chart-title"><i class="fas fa-chart-bar"></i> Priority Distribution</div>
                    <div class="bar-chart">
                        {create_bar_chart(priority_breakdown)}
                    </div>
                </div>
            </div>

            <div style="page-break-after: always;"></div>

            <!-- Active Cases Section -->
            <div class="section">
                <h2 class="section-title"><i class="fas fa-folder-open"></i> Active Cases</h2>
                {'<table>' if active_cases else '<p>No active cases</p>'}
                    {'<thead><tr><th>Case Number</th><th>Employer</th><th>Worker</th><th>Territory</th><th>Status</th><th>Priority</th><th>Incident Date</th></tr></thead>' if active_cases else ''}
                    {'<tbody>' if active_cases else ''}
"""

    # Add active cases rows
    for case in active_cases:
        html += f"""
                        <tr>
                            <td><strong>{case['case_number']}</strong></td>
                            <td>{case['employer']}</td>
                            <td>{case['worker']}</td>
                            <td>{case['territory']}</td>
                            <td><span class="status-badge status-active">{case['status']}</span></td>
                            <td>{case['priority']}</td>
                            <td>{case['incident_date']}</td>
                        </tr>
"""

    html += f"""
                    {'</tbody></table>' if active_cases else ''}
            </div>

            <!-- Closed Cases Section -->
            <div class="section">
                <h2 class="section-title"><i class="fas fa-check-circle"></i> Closed Cases</h2>
                {'<table>' if closed_cases else '<p>No closed cases</p>'}
                    {'<thead><tr><th>Case Number</th><th>Employer</th><th>Worker</th><th>Territory</th><th>Incident Date</th><th>Status</th></tr></thead>' if closed_cases else ''}
                    {'<tbody>' if closed_cases else ''}
"""

    # Add closed cases rows
    for case in closed_cases:
        html += f"""
                        <tr>
                            <td><strong>{case['case_number']}</strong></td>
                            <td>{case['employer']}</td>
                            <td>{case['worker']}</td>
                            <td>{case['territory']}</td>
                            <td>{case['incident_date']}</td>
                            <td><span class="status-badge status-closed">{case['status']}</span></td>
                        </tr>
"""

    html += f"""
                    {'</tbody></table>' if closed_cases else ''}
            </div>

            <!-- Report Footer -->
            <div class="report-footer">
                <div class="footer-logo">
                    <i class="fas fa-shield-alt"></i> WORKERS' SAFETY & COMPENSATION COMMISSION
                </div>
                <div class="footer-text">
                    <strong>Report ID:</strong> {report_id} |
                    <strong>Generated:</strong> {now.strftime('%B %d, %Y at %H:%M')}
                </div>
                <div class="footer-text">
                    Government of the Northwest Territories
                </div>
                <div class="footer-confidential">
                    <i class="fas fa-lock"></i> This report is confidential and intended for official use only. Unauthorized disclosure is prohibited.
                </div>
            </div>
        </div>
    </div>

    <!-- Print Controls -->
    <div class="no-print">
        <button onclick="window.print()" class="btn-print">
            <i class="fas fa-print"></i> Print / Save PDF
        </button>
        <button onclick="window.close()" class="btn-close">
            <i class="fas fa-times"></i> Close
        </button>
    </div>
</body>
</html>
    """

    return html

# ==================== PAGE: SETTINGS ====================
def render_settings():
    """Render settings page"""
    st.title("⚙️ Settings")
    st.caption("System settings and information")

    st.subheader("📊 Database Information")

    stats = db.get_statistics()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Cases", stats.get('total_cases', 0))

    with col2:
        st.metric("Active Officers", stats.get('active_officers', 0))

    with col3:
        st.metric("Database Type", "SQLite")

    st.markdown("---")

    st.subheader("🗑️ Data Management")

    st.warning("⚠️ Danger Zone: These actions cannot be undone!")

    if st.button("🗑️ Clear All Demo Data"):
        st.error("This feature is disabled for safety. To clear data, delete the wscc_data.db file.")

    st.markdown("---")

    st.subheader("ℹ️ About")
    st.info("""
    **WSCC Investigation Management System**
    Version 2.0 - Complete Implementation

    Workers' Safety & Compensation Commission
    Northwest Territories & Nunavut

    Built with Streamlit + SQLite
    All features implemented

    **Features:**
    - Complete Case Management (CRUD)
    - Timeline Events
    - Investigation Reports
    - Task Management
    - Evidence Logging
    - Photo Management
    - Charges & Violations
    - Court Proceedings
    - Case Conclusion
    - BN25-XXX Briefing Notes
    - Officer Management
    - Territory Reports (NWT, Nunavut, Combined)
    - Data Export (JSON, CSV)
    - Data Import (JSON)
    """)

# ==================== MAIN ROUTING ====================
def main():
    """Main application router"""

    # Route to appropriate page
    if st.session_state.current_page == 'Dashboard':
        render_dashboard()
    elif st.session_state.current_page == 'Search':
        render_search()
    elif st.session_state.current_page == 'Cases':
        render_cases()
    elif st.session_state.current_page == 'Officers':
        render_officers()
    elif st.session_state.current_page == 'Reports':
        render_reports()
    elif st.session_state.current_page == 'Settings':
        render_settings()

if __name__ == "__main__":
    main()
