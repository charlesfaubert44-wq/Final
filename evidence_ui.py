"""
Evidence Management UI Components
Comprehensive evidence/exhibit management with chain of custody tracking
"""

import streamlit as st
import uuid
from datetime import datetime
import hashlib

def render_evidence_page(db):
    """Main evidence management page with tabs"""
    st.title("📦 Evidence Management")
    st.caption("Comprehensive evidence and exhibit tracking with chain of custody")

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "➕ Add Evidence", "📋 All Evidence", "🏢 Storage Locations"])

    with tab1:
        render_evidence_dashboard(db)

    with tab2:
        render_add_evidence_form(db)

    with tab3:
        render_evidence_list(db)

    with tab4:
        render_storage_locations(db)


def render_evidence_dashboard(db):
    """Evidence dashboard with statistics"""
    st.subheader("Evidence Overview")

    # Get statistics
    stats = db.get_evidence_statistics()
    all_exhibits = db.get_all_exhibits()

    # Statistics cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats.get('total_exhibits', 0)}</div>
            <div class="stat-label">Total Exhibits</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        custody_count = stats.get('by_status', {}).get('CUSTODY', 0)
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{custody_count}</div>
            <div class="stat-label">In Custody</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        physical_count = stats.get('by_type', {}).get('PHYSICAL', 0)
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{physical_count}</div>
            <div class="stat-label">Physical Evidence</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        digital_count = stats.get('by_type', {}).get('DIGITAL', 0)
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{digital_count}</div>
            <div class="stat-label">Digital Evidence</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Status breakdown
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 By Status")
        status_data = stats.get('by_status', {})
        if status_data:
            for status, count in status_data.items():
                st.metric(status, count)
        else:
            st.info("No exhibits yet")

    with col2:
        st.subheader("📦 By Category")
        category_data = stats.get('by_category', {})
        if category_data:
            for category, count in list(category_data.items())[:5]:  # Top 5
                st.metric(category, count)
        else:
            st.info("No exhibits yet")

    # Recent exhibits
    st.subheader("Recent Exhibits")
    if all_exhibits:
        recent = all_exhibits[:5]
        for exhibit in recent:
            with st.expander(f"{exhibit['exhibit_number']} - {exhibit['description'][:50]}..."):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Type:** {exhibit['exhibit_type']}")
                    st.write(f"**Category:** {exhibit['category']}")
                with col2:
                    st.write(f"**Status:** {exhibit['current_status']}")
                    st.write(f"**Location:** {exhibit['current_location']}")
                with col3:
                    st.write(f"**Seized:** {exhibit['seized_date']}")
                    st.write(f"**By:** {exhibit['seized_by']}")

                if st.button("View Details", key=f"view_{exhibit['exhibit_id']}"):
                    st.session_state.current_exhibit_id = exhibit['exhibit_id']
                    st.session_state.current_page = 'Evidence Detail'
                    st.rerun()
    else:
        st.info("No exhibits in the system yet. Use the 'Add Evidence' tab to create your first exhibit.")


def render_add_evidence_form(db):
    """Form to add new evidence"""
    st.subheader("Add New Evidence/Exhibit")

    # Get data for dropdowns
    all_cases = db.get_all_cases()
    all_officers = db.get_all_officers(active_only=True)
    storage_locations = db.get_all_storage_locations()

    if not all_cases:
        st.warning("No cases available. Please create a case first before adding evidence.")
        return

    with st.form("add_evidence_form"):
        # Case selection
        case_options = {f"{case['case_number']} - {case['employer']}": case['id'] for case in all_cases}
        selected_case = st.selectbox("Case", options=list(case_options.keys()), help="Select the case this evidence belongs to")
        case_id = case_options[selected_case]

        # Exhibit type
        exhibit_type = st.radio("Evidence Type", options=["PHYSICAL", "DIGITAL"], horizontal=True)

        # Category
        if exhibit_type == "PHYSICAL":
            categories = ["Document", "Equipment", "Tool", "Material", "Clothing/PPE", "Photograph (Physical)",
                         "Audio/Video Tape", "Substance", "Other"]
        else:
            categories = ["Digital Photo", "Video File", "Audio Recording", "Document (PDF/Word)",
                         "Email", "Database Export", "Screenshot", "Log File", "Other"]

        category = st.selectbox("Category", options=categories)

        # Description
        description = st.text_area("Description", help="Detailed description of the evidence", height=100)

        # Seizure information
        col1, col2 = st.columns(2)
        with col1:
            seized_date = st.date_input("Date Seized", value=datetime.now())
            seized_time = st.time_input("Time Seized", value=datetime.now().time())
        with col2:
            officer_options = {officer['name']: officer['name'] for officer in all_officers}
            seized_by = st.selectbox("Seized By (Officer)", options=list(officer_options.keys()))

        seized_location = st.text_input("Seized Location", help="Where the evidence was collected")

        # Current storage
        if storage_locations:
            location_options = {loc['location_name']: loc['location_name'] for loc in storage_locations}
            current_location = st.selectbox("Current Storage Location", options=list(location_options.keys()))
        else:
            current_location = st.text_input("Current Storage Location")

        # Additional details
        with st.expander("Additional Details"):
            col1, col2 = st.columns(2)
            with col1:
                quantity = st.number_input("Quantity", min_value=1, value=1)
                unit = st.text_input("Unit", value="item", help="e.g., item, kg, liters")
                weight = st.number_input("Weight (kg)", min_value=0.0, value=0.0, step=0.1)
            with col2:
                dimensions = st.text_input("Dimensions", help="e.g., 10x20x5 cm")
                serial_number = st.text_input("Serial Number")
                make_model = st.text_input("Make/Model")

            barcode = st.text_input("Barcode/ID")
            tags = st.text_input("Tags", help="Comma-separated tags for searching")

        condition_notes = st.text_area("Initial Condition Notes", help="Describe the condition when seized")

        # Photos
        uploaded_photos = st.file_uploader("Upload Photos", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

        # Digital files (for digital evidence)
        if exhibit_type == "DIGITAL":
            uploaded_files = st.file_uploader("Upload Digital Evidence Files", accept_multiple_files=True)

        # Submit
        submitted = st.form_submit_button("Create Exhibit", type="primary")

        if submitted:
            if not description:
                st.error("Description is required")
                return

            # Generate exhibit number
            exhibit_number = db.get_next_exhibit_number()
            exhibit_id = f"exhibit-{uuid.uuid4().hex[:8]}"

            # Combine date and time
            seized_datetime = datetime.combine(seized_date, seized_time).isoformat()

            # Create exhibit
            exhibit_data = {
                'exhibit_id': exhibit_id,
                'case_id': case_id,
                'exhibit_number': exhibit_number,
                'exhibit_type': exhibit_type,
                'category': category,
                'description': description,
                'seized_date': seized_datetime,
                'seized_by': seized_by,
                'seized_location': seized_location,
                'current_location': current_location,
                'current_status': 'CUSTODY',
                'barcode': barcode,
                'quantity': quantity,
                'unit': unit,
                'weight': weight if weight > 0 else None,
                'dimensions': dimensions,
                'serial_number': serial_number,
                'make_model': make_model,
                'condition_notes': condition_notes,
                'photo_path': '',  # TODO: Handle file uploads
                'digital_file_path': '',  # TODO: Handle file uploads
                'hash_value': '',  # TODO: Calculate hash for digital evidence
                'tags': tags,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

            try:
                # Add exhibit
                db.add_exhibit(exhibit_data)

                # Create initial chain of custody entry (CREATED)
                custody_entry = {
                    'custody_id': f"custody-{uuid.uuid4().hex[:8]}",
                    'exhibit_id': exhibit_id,
                    'action': 'CREATED',
                    'action_date': seized_datetime,
                    'performed_by': seized_by,
                    'to_location': current_location,
                    'reason': f'Evidence collected at scene: {seized_location}',
                    'condition_after': condition_notes,
                    'notes': f'Initial collection and documentation of evidence',
                    'created_at': datetime.now().isoformat()
                }
                db.add_custody_entry(custody_entry)

                st.success(f"✅ Exhibit {exhibit_number} created successfully!")
                st.info(f"Exhibit ID: {exhibit_id}")

                # Clear form by rerunning
                st.balloons()
                st.rerun()

            except Exception as e:
                st.error(f"Error creating exhibit: {str(e)}")


def render_evidence_list(db):
    """List all evidence with search and filters"""
    st.subheader("All Evidence")

    # Get all exhibits
    all_exhibits = db.get_all_exhibits()

    if not all_exhibits:
        st.info("No exhibits in the system yet. Use the 'Add Evidence' tab to create exhibits.")
        return

    # Search and filters
    col1, col2, col3 = st.columns(3)

    with col1:
        search_query = st.text_input("🔍 Search", placeholder="Exhibit number, description...")

    with col2:
        status_filter = st.selectbox("Status", options=["All", "CUSTODY", "RETURNED", "DESTROYED"])

    with col3:
        type_filter = st.selectbox("Type", options=["All", "PHYSICAL", "DIGITAL"])

    # Filter exhibits
    filtered_exhibits = all_exhibits

    if search_query:
        filtered_exhibits = [e for e in filtered_exhibits
                            if search_query.lower() in e['exhibit_number'].lower()
                            or search_query.lower() in e['description'].lower()]

    if status_filter != "All":
        filtered_exhibits = [e for e in filtered_exhibits if e['current_status'] == status_filter]

    if type_filter != "All":
        filtered_exhibits = [e for e in filtered_exhibits if e['exhibit_type'] == type_filter]

    # Display count
    st.write(f"Showing {len(filtered_exhibits)} of {len(all_exhibits)} exhibits")

    # Display exhibits
    for exhibit in filtered_exhibits:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

            with col1:
                st.markdown(f"**{exhibit['exhibit_number']}**")
                st.caption(f"{exhibit['description'][:80]}..." if len(exhibit['description']) > 80 else exhibit['description'])

            with col2:
                st.write(f"Type: {exhibit['exhibit_type']}")
                st.write(f"Category: {exhibit['category']}")

            with col3:
                # Status badge color
                status_color = {
                    'CUSTODY': '🟢',
                    'RETURNED': '🔵',
                    'DESTROYED': '🔴'
                }.get(exhibit['current_status'], '⚪')
                st.write(f"{status_color} {exhibit['current_status']}")
                st.write(f"📍 {exhibit['current_location']}")

            with col4:
                if st.button("View", key=f"view_list_{exhibit['exhibit_id']}"):
                    st.session_state.current_exhibit_id = exhibit['exhibit_id']
                    st.session_state.show_evidence_detail = True
                    st.rerun()

            st.markdown("---")

    # Show detail modal if requested
    if st.session_state.get('show_evidence_detail'):
        render_evidence_detail(db, st.session_state.current_exhibit_id)


def render_evidence_detail(db, exhibit_id):
    """Detail view for a single exhibit with chain of custody"""
    exhibit = db.get_exhibit_by_id(exhibit_id)

    if not exhibit:
        st.error("Exhibit not found")
        return

    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"📦 {exhibit['exhibit_number']}")
        st.caption(exhibit['description'])
    with col2:
        if st.button("← Back to List"):
            st.session_state.show_evidence_detail = False
            st.rerun()

    # Status badge
    status_colors = {
        'CUSTODY': ('🟢', 'green'),
        'RETURNED': ('🔵', 'blue'),
        'DESTROYED': ('🔴', 'red')
    }
    icon, color = status_colors.get(exhibit['current_status'], ('⚪', 'gray'))
    st.markdown(f"### {icon} Status: {exhibit['current_status']}")

    # Details
    st.subheader("Exhibit Details")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write(f"**Type:** {exhibit['exhibit_type']}")
        st.write(f"**Category:** {exhibit['category']}")
        st.write(f"**Seized Date:** {exhibit['seized_date']}")
        st.write(f"**Seized By:** {exhibit['seized_by']}")

    with col2:
        st.write(f"**Current Location:** {exhibit['current_location']}")
        st.write(f"**Quantity:** {exhibit['quantity']} {exhibit['unit']}")
        if exhibit['weight']:
            st.write(f"**Weight:** {exhibit['weight']} kg")
        if exhibit['serial_number']:
            st.write(f"**Serial:** {exhibit['serial_number']}")

    with col3:
        st.write(f"**Seized Location:** {exhibit['seized_location']}")
        if exhibit['barcode']:
            st.write(f"**Barcode:** {exhibit['barcode']}")
        if exhibit['make_model']:
            st.write(f"**Make/Model:** {exhibit['make_model']}")

    st.markdown("---")

    # Chain of Custody
    st.subheader("🔗 Chain of Custody")
    custody_chain = db.get_custody_chain(exhibit_id)

    if custody_chain:
        for entry in reversed(custody_chain):  # Newest first
            with st.expander(f"{entry['action']} - {entry['action_date']}", expanded=False):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Action:** {entry['action']}")
                    st.write(f"**Performed By:** {entry['performed_by']}")
                    if entry['received_by']:
                        st.write(f"**Received By:** {entry['received_by']}")
                    if entry['witness']:
                        st.write(f"**Witness:** {entry['witness']}")

                with col2:
                    if entry['from_location']:
                        st.write(f"**From:** {entry['from_location']}")
                    if entry['to_location']:
                        st.write(f"**To:** {entry['to_location']}")
                    if entry['authorized_by']:
                        st.write(f"**Authorized By:** {entry['authorized_by']}")
                    if entry['seal_number']:
                        st.write(f"**Seal #:** {entry['seal_number']}")

                st.write(f"**Reason:** {entry['reason']}")

                if entry['condition_before']:
                    st.write(f"**Condition Before:** {entry['condition_before']}")
                if entry['condition_after']:
                    st.write(f"**Condition After:** {entry['condition_after']}")
                if entry['notes']:
                    st.write(f"**Notes:** {entry['notes']}")
    else:
        st.info("No chain of custody entries yet")

    # Actions
    st.markdown("---")
    st.subheader("Actions")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📝 Log Action", use_container_width=True):
            st.session_state.show_log_action = True
            st.rerun()

    with col2:
        if st.button("📄 Print Chain of Custody", use_container_width=True):
            st.info("Report generation feature coming soon")

    with col3:
        if st.button("🏷️ Print Label", use_container_width=True):
            st.info("Label printing feature coming soon")


def render_storage_locations(db):
    """Manage storage locations"""
    st.subheader("Storage Locations")

    locations = db.get_all_storage_locations()

    if locations:
        for loc in locations:
            with st.expander(f"{loc['location_name']} ({loc['location_type']})"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Type:** {loc['location_type']}")
                    st.write(f"**Capacity:** {loc['capacity']}")
                    st.write(f"**Current Count:** {loc['current_count']}")

                with col2:
                    st.write(f"**Temperature Controlled:** {'Yes' if loc['temperature_controlled'] else 'No'}")
                    st.write(f"**Secure/Locked:** {'Yes' if loc['secure_locked'] else 'No'}")
                    if loc['access_level']:
                        st.write(f"**Access Level:** {loc['access_level']}")

                if loc['notes']:
                    st.write(f"**Notes:** {loc['notes']}")
    else:
        st.info("No storage locations defined yet")

    # Add new location
    with st.expander("➕ Add New Storage Location"):
        with st.form("add_storage_form"):
            location_name = st.text_input("Location Name", help="e.g., Evidence Room A, Locker 5")
            location_type = st.selectbox("Type", options=["ROOM", "LOCKER", "FREEZER", "SERVER", "CABINET", "VAULT", "OTHER"])

            col1, col2 = st.columns(2)
            with col1:
                capacity = st.number_input("Capacity", min_value=0, value=0, help="Maximum items/GB")
                access_level = st.text_input("Access Level", help="Who can access this location")

            with col2:
                temp_controlled = st.checkbox("Temperature Controlled")
                secure_locked = st.checkbox("Secure/Locked", value=True)

            notes = st.text_area("Notes")

            if st.form_submit_button("Add Location"):
                location_data = {
                    'storage_id': f"storage-{uuid.uuid4().hex[:8]}",
                    'location_name': location_name,
                    'location_type': location_type,
                    'capacity': capacity,
                    'current_count': 0,
                    'access_level': access_level,
                    'temperature_controlled': 1 if temp_controlled else 0,
                    'secure_locked': 1 if secure_locked else 0,
                    'notes': notes,
                    'created_at': datetime.now().isoformat()
                }

                try:
                    db.add_storage_location(location_data)
                    st.success(f"Storage location '{location_name}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding location: {str(e)}")
