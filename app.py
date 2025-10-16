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
from evidence_ui import render_evidence_page
from disclosure import generate_disclosure_package
from visual_analytics import render_visual_analytics
import plotly.graph_objects as go

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
        font-size: 1.8rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .nav-brand-subtitle {
        font-size: 0.9rem;
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

    /* Global body background - no image */
    .stApp {
        background-image: none;
        background-image: url('data:image/jpeg;base64,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');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
    }

    /* Centered boxed content container */
    .main .block-container {
        max-width: 75% !important;
        margin: 0 auto !important;
        background: rgb(255, 255, 255);
        padding: 2rem !important;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
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
    '📦 Evidence': 'Evidence',
    '🌐 Visuals': 'Visuals',
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
        <div class="stat-card" style="position: relative; overflow: hidden;">
            <div style="position: absolute; bottom: -20px; right: -20px; width: 180px; height: 180px; opacity: 0.15; z-index: 0; background-image: url('https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Flag_of_the_Northwest_Territories.svg/320px-Flag_of_the_Northwest_Territories.svg.png'); background-size: contain; background-repeat: no-repeat; background-position: center;"></div>
            <div class="stat-number" style="position: relative; z-index: 1;">{nwt_cases}</div>
            <div class="stat-label" style="position: relative; z-index: 1;">NWT Cases</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        nu_cases = stats.get('by_territory', {}).get('Nunavut', 0)
        st.markdown(f"""
        <div class="stat-card" style="position: relative; overflow: hidden;">
            <div style="position: absolute; bottom: -20px; right: -20px; width: 180px; height: 180px; opacity: 0.15; z-index: 0; background-image: url('https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Flag_of_Nunavut.svg/320px-Flag_of_Nunavut.svg.png'); background-size: contain; background-repeat: no-repeat; background-position: center;"></div>
            <div class="stat-number" style="position: relative; z-index: 1;">{nu_cases}</div>
            <div class="stat-label" style="position: relative; z-index: 1;">Nunavut Cases</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Statistical Analysis - Stock Dashboard Style
    st.subheader("Statistical Analysis and Metrics")
    st.caption("Real-time investigation metrics and trends")

    # Create 5 columns for thin vertical charts
    chart1, chart2, chart3, chart4, chart5 = st.columns(5)

    # Chart 1: Case Status
    with chart1:
        st.caption("STATUS")
        status_data = stats.get('by_status', {})
        if status_data:
            fig1 = go.Figure(data=[
                go.Bar(
                    x=list(status_data.keys()),
                    y=list(status_data.values()),
                    marker=dict(color='#2c5282', line=dict(width=0)),
                    width=0.4
                )
            ])
            fig1.update_layout(
                height=280,
                margin=dict(l=10, r=10, t=10, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=False,
                    title=None,
                    tickfont=dict(size=9)
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(200,200,200,0.2)',
                    title=None,
                    tickfont=dict(size=9)
                ),
                showlegend=False,
                hoverlabel=dict(bgcolor='#2c5282')
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No data")

    # Chart 2: Territory
    with chart2:
        st.caption("TERRITORY")
        territory_data = stats.get('by_territory', {})
        if territory_data:
            # Shorten names
            short_names = {'Northwest Territories': 'NWT', 'Nunavut': 'Nunavut'}
            territories = [short_names.get(k, k) for k in territory_data.keys()]

            fig2 = go.Figure(data=[
                go.Bar(
                    x=territories,
                    y=list(territory_data.values()),
                    marker=dict(color='#4299e1', line=dict(width=0)),
                    width=0.4
                )
            ])
            fig2.update_layout(
                height=280,
                margin=dict(l=10, r=10, t=10, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=False,
                    title=None,
                    tickfont=dict(size=9)
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(200,200,200,0.2)',
                    title=None,
                    tickfont=dict(size=9)
                ),
                showlegend=False,
                hoverlabel=dict(bgcolor='#4299e1')
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No data")

    # Chart 3: Priority
    with chart3:
        st.caption("PRIORITY")
        priority_data = stats.get('by_priority', {})
        if priority_data:
            priority_order = ['High', 'Medium', 'Low']
            priorities = [p for p in priority_order if p in priority_data]
            values = [priority_data[p] for p in priorities]
            colors = ['#ef4444', '#f59e0b', '#10b981'][:len(priorities)]

            fig3 = go.Figure(data=[
                go.Bar(
                    x=priorities,
                    y=values,
                    marker=dict(color=colors, line=dict(width=0)),
                    width=0.4
                )
            ])
            fig3.update_layout(
                height=280,
                margin=dict(l=10, r=10, t=10, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=False,
                    title=None,
                    tickfont=dict(size=9)
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(200,200,200,0.2)',
                    title=None,
                    tickfont=dict(size=9)
                ),
                showlegend=False,
                hoverlabel=dict(bgcolor='#f59e0b')
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No data")

    # Chart 4: Officer Workload
    with chart4:
        st.caption("WORKLOAD")
        officer_workload = {}
        for case in all_cases:
            if case['status'] in ['Open', 'Under Investigation']:
                officers = case.get('assigned_officers', [])
                if officers:
                    for officer_id in officers:
                        officer = db.get_officer_by_id(officer_id)
                        if officer:
                            # Use last name only
                            name = officer['name'].split()[-1] if ' ' in officer['name'] else officer['name']
                            officer_workload[name] = officer_workload.get(name, 0) + 1
                else:
                    officer_workload['Unassigned'] = officer_workload.get('Unassigned', 0) + 1

        if officer_workload:
            # Sort and take top 5
            sorted_workload = sorted(officer_workload.items(), key=lambda x: x[1], reverse=True)[:5]
            officers = [x[0] for x in sorted_workload]
            cases = [x[1] for x in sorted_workload]

            fig4 = go.Figure(data=[
                go.Bar(
                    x=officers,
                    y=cases,
                    marker=dict(color='#10b981', line=dict(width=0)),
                    width=0.4
                )
            ])
            fig4.update_layout(
                height=280,
                margin=dict(l=10, r=10, t=10, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=False,
                    title=None,
                    tickfont=dict(size=9)
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(200,200,200,0.2)',
                    title=None,
                    tickfont=dict(size=9)
                ),
                showlegend=False,
                hoverlabel=dict(bgcolor='#10b981')
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No data")

    # Chart 5: Monthly Trend
    with chart5:
        st.caption("TREND")
        if all_cases:
            case_dates = []
            for case in all_cases:
                if case.get('reported_date'):
                    try:
                        date = datetime.fromisoformat(case['reported_date'])
                        case_dates.append(date.date())
                    except:
                        pass

            if case_dates:
                from collections import Counter
                date_counts = Counter([f"{d.month:02d}" for d in case_dates])  # Just month
                sorted_dates = sorted(date_counts.items())
                months = [d[0] for d in sorted_dates[-6:]]  # Last 6 months
                counts = [d[1] for d in sorted_dates[-6:]]

                fig5 = go.Figure(data=[
                    go.Bar(
                        x=months,
                        y=counts,
                        marker=dict(color='#8b5cf6', line=dict(width=0)),
                        width=0.4
                    )
                ])
                fig5.update_layout(
                    height=280,
                    margin=dict(l=10, r=10, t=10, b=40),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(
                        showgrid=False,
                        title=None,
                        tickfont=dict(size=9)
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(200,200,200,0.2)',
                        title=None,
                        tickfont=dict(size=9)
                    ),
                    showlegend=False,
                    hoverlabel=dict(bgcolor='#8b5cf6')
                )
                st.plotly_chart(fig5, use_container_width=True)
            else:
                st.info("No data")
        else:
            st.info("No data")

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
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])

    with col1:
        search = st.text_input("🔍 Search cases...", placeholder="Search by case number, employer, worker...")

    with col2:
        territory_filter = st.selectbox("Territory", ["All", "Northwest Territories", "Nunavut"])

    with col3:
        status_filter = st.selectbox("Status", ["All", "Open", "Under Investigation", "Closed"])

    with col4:
        # View toggle
        if 'case_view_mode' not in st.session_state:
            st.session_state.case_view_mode = 'cards'

        view_icon = "📋" if st.session_state.case_view_mode == "cards" else "🃏"
        view_label = "List View" if st.session_state.case_view_mode == "cards" else "Card View"

        if st.button(f"{view_icon} {view_label}", use_container_width=True):
            st.session_state.case_view_mode = "list" if st.session_state.case_view_mode == "cards" else "cards"
            st.rerun()

    with col5:
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
        # CARD VIEW
        if st.session_state.case_view_mode == "cards":
            # Display in 3 columns
            cols_per_row = 3
            for i in range(0, len(cases), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(cases):
                        case = cases[i + j]
                        with col:
                            # Priority color mapping
                            priority_colors = {
                                "High": "#ef4444",
                                "Medium": "#f59e0b",
                                "Low": "#10b981"
                            }
                            priority_color = priority_colors.get(case['priority'], "#6b7280")

                            # Status color mapping
                            status_colors = {
                                "Open": "#3b82f6",
                                "Under Investigation": "#f59e0b",
                                "Closed": "#6b7280"
                            }
                            status_color = status_colors.get(case['status'], "#6b7280")

                            # Territory icon
                            territory_icon = "🏔️" if case['territory'] == "Northwest Territories" else "❄️"

                            # Create card using container with custom styling
                            card_html = f"""
                            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); position: relative; overflow: hidden;">
                                <div style="position: absolute; top: 10px; right: 10px; background: {priority_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">{case['priority']}</div>
                                <div style="color: white; font-weight: 700; font-size: 1.25rem; margin-bottom: 0.5rem;">{case['case_number']}</div>
                                <div style="color: rgba(255,255,255,0.9); font-size: 0.9rem; margin-bottom: 0.25rem;">🏢 {case['employer']}</div>
                                <div style="color: rgba(255,255,255,0.8); font-size: 0.85rem; margin-bottom: 0.5rem;">👤 {case['worker']}</div>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2);">
                                    <div style="color: rgba(255,255,255,0.9); font-size: 0.8rem;">{territory_icon} {case['territory'][:3]}</div>
                                    <div style="background: {status_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 15px; font-size: 0.75rem;">{case['status']}</div>
                                </div>
                            </div>
                            """
                            st.markdown(card_html, unsafe_allow_html=True)

                            # Action buttons
                            btn_col1, btn_col2 = st.columns(2)
                            with btn_col1:
                                if st.button("👁️ View", key=f"view_card_{case['id']}", use_container_width=True):
                                    st.session_state.current_case_id = case['id']
                                    st.session_state.show_case_details = True
                                    st.rerun()
                            with btn_col2:
                                if st.button("🗑️ Delete", key=f"delete_card_{case['id']}", use_container_width=True):
                                    st.session_state.delete_case_id = case['id']
                                    st.rerun()

        # LIST VIEW
        else:
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
                        if st.button("View", key=f"view_list_{case['id']}"):
                            st.session_state.current_case_id = case['id']
                            st.session_state.show_case_details = True
                            st.rerun()

                    with col6:
                        if st.button("🗑️", key=f"delete_list_{case['id']}"):
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
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

        with col1:
            st.markdown(f"### {case['case_number']}")

        with col2:
            if st.button("📁 Disclosure", use_container_width=True, help="Generate Court Disclosure Package"):
                # Generate disclosure package
                exhibits = db.get_exhibits_by_case(case['id'])
                html_content = generate_disclosure_package(case, db, exhibits)

                # Open in new window
                import webbrowser
                import tempfile
                import os

                # Create temp file
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8') as f:
                    f.write(html_content)
                    temp_path = f.name

                # Open in browser
                webbrowser.open('file://' + os.path.realpath(temp_path))
                st.success("Disclosure package generated! Check your browser.")

        with col3:
            if st.button("✏️ Edit", use_container_width=True):
                st.session_state.editing_case = not st.session_state.get('editing_case', False)
                st.rerun()

        with col4:
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
    """Generate clean, professional HTML report optimized for printing"""

    # Calculate statistics
    active_cases = [c for c in cases if c['status'] in ['Open', 'Under Investigation']]
    closed_cases = [c for c in cases if c['status'] == 'Closed']

    # Status breakdown
    status_breakdown = {}
    for case in cases:
        status = case['status']
        status_breakdown[status] = status_breakdown.get(status, 0) + 1

    # Priority breakdown
    priority_breakdown = {}
    for case in cases:
        priority = case['priority']
        priority_breakdown[priority] = priority_breakdown.get(priority, 0) + 1

    # Generate unique report ID
    now = datetime.now()
    report_id = f"WSCC-{territory.upper().replace(' ', '')}-{now.strftime('%Y%m%d')}"

    # Generate clean HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WSCC Investigation Report - {territory}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        @page {{ size: letter; margin: 1in; }}

        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: white;
        }}

        .header {{
            text-align: center;
            border-bottom: 3px solid #2c5282;
            padding-bottom: 1rem;
            margin-bottom: 2rem;
        }}

        .header h1 {{
            color: #2c5282;
            font-size: 24pt;
            margin: 0 0 0.5rem 0;
        }}

        .header p {{
            color: #666;
            font-size: 11pt;
            margin: 0.25rem 0;
        }}

        .report-meta {{
            background: #f8f9fa;
            border-left: 4px solid #2c5282;
            padding: 1rem;
            margin-bottom: 2rem;
        }}

        .report-meta p {{
            margin: 0.25rem 0;
            font-size: 10pt;
        }}

        h2 {{
            color: #2c5282;
            font-size: 14pt;
            margin: 1.5rem 0 0.75rem 0;
            padding-bottom: 0.25rem;
            border-bottom: 2px solid #2c5282;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin: 1rem 0 2rem 0;
        }}

        .stat-box {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-left: 3px solid #2c5282;
            padding: 0.75rem;
            text-align: center;
        }}

        .stat-number {{
            font-size: 24pt;
            font-weight: 600;
            color: #2c5282;
        }}

        .stat-label {{
            font-size: 9pt;
            color: #666;
            text-transform: uppercase;
            margin-top: 0.25rem;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 10pt;
        }}

        thead {{
            background: #2c5282;
            color: white;
        }}

        th {{
            padding: 0.75rem;
            text-align: left;
            font-weight: 600;
        }}

        td {{
            padding: 0.75rem;
            border-bottom: 1px solid #dee2e6;
        }}

        tbody tr:nth-child(even) {{
            background: #f8f9fa;
        }}

        .footer {{
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 2px solid #2c5282;
            text-align: center;
            font-size: 9pt;
            color: #666;
        }}

        .no-print {{
            position: fixed;
            bottom: 20px;
            right: 20px;
        }}

        .btn-print {{
            padding: 12px 24px;
            background: #2c5282;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11pt;
        }}

        .btn-print:hover {{
            background: #1e3a5f;
        }}

        @media print {{
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Workers' Safety & Compensation Commission</h1>
        <p>{territory}</p>
        <p>Investigation Report</p>
    </div>

    <div class="report-meta">
        <p><strong>Report ID:</strong> {report_id}</p>
        <p><strong>Generated:</strong> {now.strftime('%B %d, %Y at %H:%M')}</p>
        <p><strong>Territory:</strong> {territory}</p>
        <p><strong>Total Cases:</strong> {len(cases)}</p>
    </div>

    <h2>Summary Statistics</h2>
    <div class="stats">
        <div class="stat-box">
            <div class="stat-number">{len(cases)}</div>
            <div class="stat-label">Total Cases</div>
        </div>
        <div class="stat-box">
            <div class="stat-number">{len(active_cases)}</div>
            <div class="stat-label">Active Cases</div>
        </div>
        <div class="stat-box">
            <div class="stat-number">{len(closed_cases)}</div>
            <div class="stat-label">Closed Cases</div>
        </div>
        <div class="stat-box">
            <div class="stat-number">{priority_breakdown.get('High', 0)}</div>
            <div class="stat-label">High Priority</div>
        </div>
    </div>

    <h2>Case Status Breakdown</h2>
    <table>
        <thead>
            <tr>
                <th>Status</th>
                <th>Count</th>
            </tr>
        </thead>
        <tbody>
"""

    # Add status rows
    for status, count in sorted(status_breakdown.items(), key=lambda x: x[1], reverse=True):
        html += f"""
            <tr>
                <td>{status}</td>
                <td>{count}</td>
            </tr>
"""

    html += """
        </tbody>
    </table>

    <h2>Priority Distribution</h2>
    <table>
        <thead>
            <tr>
                <th>Priority</th>
                <th>Count</th>
            </tr>
        </thead>
        <tbody>
"""

    # Add priority rows
    priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
    for priority in sorted(priority_breakdown.keys(), key=lambda x: priority_order.get(x, 999)):
        html += f"""
            <tr>
                <td>{priority}</td>
                <td>{priority_breakdown[priority]}</td>
            </tr>
"""

    html += f"""
        </tbody>
    </table>

    <h2>Active Cases</h2>
    {'<table>' if active_cases else '<p>No active cases</p>'}
"""

    if active_cases:
        html += """
        <thead>
            <tr>
                <th>Case Number</th>
                <th>Employer</th>
                <th>Worker</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Incident Date</th>
            </tr>
        </thead>
        <tbody>
"""
        for case in active_cases:
            html += f"""
            <tr>
                <td><strong>{case['case_number']}</strong></td>
                <td>{case['employer']}</td>
                <td>{case['worker']}</td>
                <td>{case['status']}</td>
                <td>{case['priority']}</td>
                <td>{case['incident_date']}</td>
            </tr>
"""
        html += """
        </tbody>
    </table>
"""

    html += f"""
    <h2>Closed Cases</h2>
    {'<table>' if closed_cases else '<p>No closed cases</p>'}
"""

    if closed_cases:
        html += """
        <thead>
            <tr>
                <th>Case Number</th>
                <th>Employer</th>
                <th>Worker</th>
                <th>Incident Date</th>
            </tr>
        </thead>
        <tbody>
"""
        for case in closed_cases:
            html += f"""
            <tr>
                <td><strong>{case['case_number']}</strong></td>
                <td>{case['employer']}</td>
                <td>{case['worker']}</td>
                <td>{case['incident_date']}</td>
            </tr>
"""
        html += """
        </tbody>
    </table>
"""

    html += f"""
    <div class="footer">
        <p><strong>Workers' Safety & Compensation Commission</strong></p>
        <p>Government of the Northwest Territories</p>
        <p>Report ID: {report_id} | Generated: {now.strftime('%B %d, %Y')}</p>
        <p style="margin-top: 0.5rem; font-style: italic;">This report is confidential and intended for official use only.</p>
    </div>

    <div class="no-print">
        <button onclick="window.print()" class="btn-print">Print / Save PDF</button>
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
    elif st.session_state.current_page == 'Evidence':
        render_evidence_page(db)
    elif st.session_state.current_page == 'Visuals':
        render_visual_analytics(db)
    elif st.session_state.current_page == 'Officers':
        render_officers()
    elif st.session_state.current_page == 'Reports':
        render_reports()
    elif st.session_state.current_page == 'Settings':
        render_settings()

if __name__ == "__main__":
    main()
