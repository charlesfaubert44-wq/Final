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
if 'editing_case' not in st.session_state:
    st.session_state.editing_case = False

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
    .timeline-event {
        border-left: 3px solid #5eead4;
        padding-left: 1rem;
        margin-bottom: 1rem;
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
                        <strong>{event['date']}</strong> - <span style="color: #5eead4;">{event['type']}</span><br>
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
    st.markdown('<h1 class="main-header">👥 Officer Management</h1>', unsafe_allow_html=True)

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
    st.markdown('<h1 class="main-header">📄 Reports & Export</h1>', unsafe_allow_html=True)

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
    """Generate HTML report for territory"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{territory} Investigation Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #5eead4; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #5eead4; color: white; }}
            .priority-high {{ color: #ef4444; font-weight: bold; }}
            .priority-medium {{ color: #f59e0b; font-weight: bold; }}
            .priority-low {{ color: #10b981; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>WSCC Investigation Report - {territory}</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
        <p><strong>Total Cases:</strong> {len(cases)}</p>

        <h2>Case Summary</h2>
        <table>
            <tr>
                <th>Case Number</th>
                <th>Employer</th>
                <th>Worker</th>
                <th>Incident Date</th>
                <th>Status</th>
                <th>Priority</th>
            </tr>
    """

    for case in cases:
        priority_class = f"priority-{case['priority'].lower()}"
        html += f"""
            <tr>
                <td>{case['case_number']}</td>
                <td>{case['employer']}</td>
                <td>{case['worker']}</td>
                <td>{case['incident_date']}</td>
                <td>{case['status']}</td>
                <td class="{priority_class}">{case['priority']}</td>
            </tr>
        """

    html += """
        </table>

        <h2>Case Details</h2>
    """

    for case in cases:
        html += f"""
        <div style="margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
            <h3>{case['case_number']} - {case['employer']}</h3>
            <p><strong>Worker:</strong> {case['worker']}</p>
            <p><strong>Incident Date:</strong> {case['incident_date']}</p>
            <p><strong>Status:</strong> {case['status']}</p>
            <p><strong>Priority:</strong> {case['priority']}</p>
            <p><strong>Description:</strong> {case['description']}</p>
        </div>
        """

    html += """
    </body>
    </html>
    """

    return html

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
