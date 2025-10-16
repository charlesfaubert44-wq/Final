"""
WSCC Investigation Management System - Streamlit Version
Main application file with navigation and page routing
"""

import streamlit as st
from datetime import datetime
import uuid
from database import Database

# Page configuration
st.set_page_config(
    page_title="WSCC Investigation Management",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
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

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #5eead4;
        margin-bottom: 1rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    .case-card {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: white;
    }
    .priority-high {
        color: #ef4444;
        font-weight: 600;
    }
    .priority-medium {
        color: #f59e0b;
        font-weight: 600;
    }
    .priority-low {
        color: #10b981;
        font-weight: 600;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    .status-open {
        background-color: #dbeafe;
        color: #1e40af;
    }
    .status-investigation {
        background-color: #fef3c7;
        color: #92400e;
    }
    .status-closed {
        background-color: #d1fae5;
        color: #065f46;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("### 🔍 WSCC Portal")
    st.markdown("---")

    # Navigation menu
    pages = {
        '📊 Dashboard': 'Dashboard',
        '📁 Cases': 'Cases',
        '👥 Officers': 'Officers',
        '📄 Reports': 'Reports',
        '⚙️ Settings': 'Settings'
    }

    for icon_label, page_name in pages.items():
        if st.button(icon_label, key=f"nav_{page_name}", use_container_width=True):
            st.session_state.current_page = page_name
            st.rerun()

    st.markdown("---")
    st.markdown("**Current Page:**")
    st.info(st.session_state.current_page)

    st.markdown("---")
    st.markdown("**Quick Stats:**")
    stats = db.get_statistics()
    st.metric("Total Cases", stats.get('total_cases', 0))
    st.metric("Active Officers", stats.get('active_officers', 0))

# ==================== PAGE: DASHBOARD ====================
def render_dashboard():
    """Render dashboard page"""
    st.markdown('<h1 class="main-header">🔍 WSCC Investigation Management</h1>', unsafe_allow_html=True)
    st.markdown("**Workers' Safety & Compensation Commission**")
    st.markdown("---")

    # Get statistics
    stats = db.get_statistics()

    # Statistics cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <div class="stat-number">{stats.get('total_cases', 0)}</div>
            <div class="stat-label">Total Cases</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        open_cases = stats.get('by_status', {}).get('Open', 0) + stats.get('by_status', {}).get('Under Investigation', 0)
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="stat-number">{open_cases}</div>
            <div class="stat-label">Active Cases</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        nwt_cases = stats.get('by_territory', {}).get('Northwest Territories', 0)
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="stat-number">{nwt_cases}</div>
            <div class="stat-label">NWT Cases</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        nu_cases = stats.get('by_territory', {}).get('Nunavut', 0)
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <div class="stat-number">{nu_cases}</div>
            <div class="stat-label">Nunavut Cases</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Recent cases
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📋 Recent Cases")
        cases = db.get_all_cases()[:5]  # Get 5 most recent

        if cases:
            for case in cases:
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
        st.subheader("📊 Case Status")
        status_data = stats.get('by_status', {})

        for status, count in status_data.items():
            st.metric(status, count)

        st.markdown("---")

        st.subheader("🎯 Priority")
        priority_data = stats.get('by_priority', {})

        for priority, count in priority_data.items():
            priority_class = f"priority-{priority.lower()}"
            st.markdown(f"<span class='{priority_class}'>{priority}: {count}</span>", unsafe_allow_html=True)

# ==================== PAGE: CASES ====================
def render_cases():
    """Render cases page"""
    st.markdown('<h1 class="main-header">📁 Case Management</h1>', unsafe_allow_html=True)

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
                col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])

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

                st.markdown("---")
    else:
        st.info("No cases found matching your filters.")

    # Case details view
    if st.session_state.get('show_case_details', False) and st.session_state.current_case_id:
        render_case_details()

def render_case_details():
    """Render detailed case view"""
    case = db.get_case_by_id(st.session_state.current_case_id)

    if not case:
        st.error("Case not found")
        return

    with st.expander(f"📋 Case Details: {case['case_number']}", expanded=True):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"### {case['case_number']}")

        with col2:
            if st.button("❌ Close", use_container_width=True):
                st.session_state.show_case_details = False
                st.session_state.current_case_id = None
                st.rerun()

        # Tabs for different case sections
        tabs = st.tabs([
            "Overview", "Timeline", "Reports", "Tasks", "Evidence",
            "Photos", "Charges", "Court", "Conclusion", "Briefing Note"
        ])

        with tabs[0]:  # Overview
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

        with tabs[1]:  # Timeline
            st.subheader("📅 Timeline Events")
            st.info("Timeline feature - Add events, milestones, and updates")

        with tabs[2]:  # Reports
            st.subheader("📄 Investigation Reports")
            st.info("Reports feature - Generate and manage investigation reports")

        with tabs[3]:  # Tasks
            st.subheader("✅ Tasks")
            st.info("Task management - Assign and track investigation tasks")

        with tabs[4]:  # Evidence
            st.subheader("🔍 Evidence Log")
            st.info("Evidence management - Document physical and digital evidence")

        with tabs[5]:  # Photos
            st.subheader("📸 Photos")
            st.info("Photo management - Upload and manage incident photos")

        with tabs[6]:  # Charges
            st.subheader("⚖️ Charges")
            st.info("Charges and violations - Document regulatory violations")

        with tabs[7]:  # Court
            st.subheader("🏛️ Court Proceedings")
            st.info("Court information - Track legal proceedings")

        with tabs[8]:  # Conclusion
            st.subheader("📝 Conclusion")
            st.info("Case conclusion - Final findings and closure")

        with tabs[9]:  # Briefing Note
            st.subheader("📋 Briefing Note")
            st.info("Briefing note generation - Create formal BN25-XXX notes")

# ==================== PAGE: OFFICERS ====================
def render_officers():
    """Render officers page"""
    st.markdown('<h1 class="main-header">👥 Officer Management</h1>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])

    with col1:
        search = st.text_input("🔍 Search officers...", placeholder="Search by name or role...")

    with col2:
        if st.button("➕ Add New Officer", use_container_width=True):
            st.session_state.show_add_officer_form = True
            st.rerun()

    # Add officer form
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
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

                with col1:
                    st.markdown(f"**{officer['name']}**")
                    st.caption(officer['role'])

                with col2:
                    st.caption(f"📍 {officer.get('work_location', 'N/A')}")

                with col3:
                    st.caption(f"⏱️ {officer.get('experience', 'N/A')}")

                with col4:
                    if officer['active']:
                        st.success("Active")
                    else:
                        st.error("Inactive")

                st.markdown("---")
    else:
        st.info("No officers found.")

# ==================== PAGE: REPORTS ====================
def render_reports():
    """Render reports page"""
    st.markdown('<h1 class="main-header">📄 Reports & Export</h1>', unsafe_allow_html=True)

    st.subheader("📊 Generate Reports")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📄 NWT Report", use_container_width=True):
            st.info("Generating NWT Territory report...")

    with col2:
        if st.button("📄 Nunavut Report", use_container_width=True):
            st.info("Generating Nunavut Territory report...")

    with col3:
        if st.button("📄 Combined Report", use_container_width=True):
            st.info("Generating combined territory report...")

    st.markdown("---")

    st.subheader("💾 Data Export/Import")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Export Data:**")
        if st.button("📥 Export to JSON", use_container_width=True):
            data = db.export_to_json()
            st.download_button(
                label="⬇️ Download JSON",
                data=str(data),
                file_name=f"wscc_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

    with col2:
        st.markdown("**Import Data:**")
        uploaded_file = st.file_uploader("📤 Upload JSON file", type=['json'])
        if uploaded_file:
            st.info("Import feature - Upload JSON backup to restore data")

# ==================== PAGE: SETTINGS ====================
def render_settings():
    """Render settings page"""
    st.markdown('<h1 class="main-header">⚙️ Settings</h1>', unsafe_allow_html=True)

    st.subheader("📊 Database Information")

    stats = db.get_statistics()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Cases", stats.get('total_cases', 0))

    with col2:
        st.metric("Active Officers", stats.get('active_officers', 0))

    with col3:
        st.metric("Database Size", "SQLite")

    st.markdown("---")

    st.subheader("🗑️ Data Management")

    st.warning("⚠️ Danger Zone: These actions cannot be undone!")

    if st.button("🗑️ Clear All Demo Data"):
        st.error("This feature will clear all demo data. Implement with confirmation dialog.")

    st.markdown("---")

    st.subheader("ℹ️ About")
    st.info("""
    **WSCC Investigation Management System**
    Version 1.0 - Streamlit Edition

    Workers' Safety & Compensation Commission
    Northwest Territories & Nunavut

    Built with Streamlit + SQLite
    No server required - runs entirely locally
    """)

# ==================== MAIN ROUTING ====================
def main():
    """Main application router"""

    # Route to appropriate page
    if st.session_state.current_page == 'Dashboard':
        render_dashboard()
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
