"""
WSCC Investigation Disclosure Package Generator
Comprehensive court-ready disclosure with all investigation details
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

def generate_disclosure_package(case: Dict, db, exhibits: List[Dict] = None) -> str:
    """
    Generate comprehensive WSCC Investigation Disclosure Package

    Includes all 18 sections:
    1. Case Summary
    2. Primary Parties
    3. All Involved Parties
    4. Incident Details
    5. Statute of Limitations
    6. Timeline of Events
    7. Investigation Reports
    8. Communications Log
    9. External Reports
    10. Briefing Note
    11. Evidence Log
    12. Photographic Evidence
    13. Charges Filed
    14. Court Events Timeline
    15. Court Information
    16. Case Conclusion
    17. Investigation Tasks & Actions
    18. Disclosure Package Summary
    """

    # Get current timestamp
    now = datetime.now()
    package_id = f"DISC-{case['case_number']}-{now.strftime('%Y%m%d%H%M')}"

    # Get assigned officers
    officers = []
    if case.get('assigned_officers'):
        for officer_id in case['assigned_officers']:
            officer = db.get_officer_by_id(officer_id)
            if officer:
                officers.append(officer['name'])

    officers_str = ", ".join(officers) if officers else "Not assigned"

    # Calculate statute of limitations
    if case.get('incident_date'):
        try:
            incident_dt = datetime.fromisoformat(case['incident_date'])
            start_date = incident_dt.strftime('%B %d, %Y')
            deadline = incident_dt + timedelta(days=365)
            deadline_str = deadline.strftime('%B %d, %Y')
            days_elapsed = (now - incident_dt).days
            days_remaining = 365 - days_elapsed

            if days_remaining < 0:
                status_class = 'expired'
                status_text = 'EXPIRED'
            elif days_remaining < 30:
                status_class = 'danger'
                status_text = 'CRITICAL'
            elif days_remaining < 90:
                status_class = 'warning'
                status_text = 'WARNING'
            else:
                status_class = 'ok'
                status_text = 'OK'
        except:
            start_date = "N/A"
            deadline_str = "N/A"
            days_elapsed = 0
            days_remaining = 365
            status_class = 'ok'
            status_text = 'N/A'
    else:
        start_date = "N/A"
        deadline_str = "N/A"
        days_elapsed = 0
        days_remaining = 365
        status_class = 'ok'
        status_text = 'N/A'

    # Get exhibits if not provided
    if exhibits is None:
        exhibits = db.get_exhibits_by_case(case['id'])

    # Count statistics for summary
    stats = {
        'involved_parties': len(case.get('involved_parties', [])),
        'timeline_events': len(case.get('timelines', [])),
        'communications': len(case.get('communications', [])),
        'reports': len(case.get('reports', [])),
        'external_reports': len(case.get('external_reports', [])),
        'exhibits': len(exhibits),
        'photos': len(case.get('photos', [])),
        'charges': len(case.get('charges', [])),
        'court_events': len(case.get('court_events', [])),
        'tasks': len(case.get('tasks', []))
    }

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WSCC Investigation Disclosure Package - {case['case_number']}</title>
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

        .header .icon {{
            font-size: 36pt;
            margin-bottom: 0.5rem;
        }}

        .header p {{
            color: #666;
            font-size: 11pt;
            margin: 0.25rem 0;
        }}

        .package-meta {{
            background: #f8f9fa;
            border-left: 4px solid #2c5282;
            padding: 1rem;
            margin-bottom: 2rem;
        }}

        .package-meta p {{
            margin: 0.25rem 0;
            font-size: 10pt;
        }}

        .package-meta strong {{
            color: #2c5282;
        }}

        h2 {{
            color: #2c5282;
            font-size: 16pt;
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #2c5282;
            page-break-after: avoid;
        }}

        h3 {{
            color: #2c5282;
            font-size: 13pt;
            margin: 1.5rem 0 0.75rem 0;
            page-break-after: avoid;
        }}

        .section {{
            margin-bottom: 2rem;
            page-break-inside: avoid;
        }}

        .info-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin: 1rem 0;
        }}

        .info-item {{
            padding: 0.75rem;
            background: #f8f9fa;
            border-left: 3px solid #2c5282;
        }}

        .info-item label {{
            font-weight: 600;
            color: #2c5282;
            font-size: 9pt;
            text-transform: uppercase;
            display: block;
            margin-bottom: 0.25rem;
        }}

        .info-item value {{
            font-size: 11pt;
            color: #333;
        }}

        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 4px;
            font-size: 9pt;
            font-weight: 600;
            text-transform: uppercase;
        }}

        .badge-open {{ background: #4299e1; color: white; }}
        .badge-investigation {{ background: #ed8936; color: white; }}
        .badge-closed {{ background: #48bb78; color: white; }}
        .badge-physical {{ background: #805ad5; color: white; }}
        .badge-digital {{ background: #38b2ac; color: white; }}
        .badge-custody {{ background: #48bb78; color: white; }}
        .badge-returned {{ background: #4299e1; color: white; }}
        .badge-destroyed {{ background: #e53e3e; color: white; }}

        .statute-box {{
            background: #fff5f5;
            border: 2px solid #fc8181;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 8px;
        }}

        .statute-box.ok {{ background: #f0fff4; border-color: #9ae6b4; }}
        .statute-box.warning {{ background: #fffaf0; border-color: #fbd38d; }}
        .statute-box.danger {{ background: #fff5f5; border-color: #fc8181; }}
        .statute-box.expired {{ background: #000; border-color: #e53e3e; color: white; }}

        .statute-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-top: 1rem;
        }}

        .statute-item {{
            text-align: center;
        }}

        .statute-number {{
            font-size: 20pt;
            font-weight: 700;
            color: #2c5282;
        }}

        .statute-label {{
            font-size: 9pt;
            text-transform: uppercase;
            color: #666;
        }}

        .timeline {{
            position: relative;
            padding-left: 2rem;
            margin: 1rem 0;
        }}

        .timeline-item {{
            position: relative;
            padding-bottom: 1.5rem;
        }}

        .timeline-item::before {{
            content: '';
            position: absolute;
            left: -2rem;
            top: 0.5rem;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #2c5282;
            border: 3px solid white;
            box-shadow: 0 0 0 2px #2c5282;
        }}

        .timeline-item::after {{
            content: '';
            position: absolute;
            left: -26px;
            top: 1.5rem;
            width: 2px;
            height: calc(100% - 1rem);
            background: #cbd5e0;
        }}

        .timeline-item:last-child::after {{
            display: none;
        }}

        .timeline-date {{
            font-weight: 600;
            color: #2c5282;
            font-size: 10pt;
        }}

        .timeline-event {{
            margin-top: 0.25rem;
            font-size: 10pt;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 10pt;
            page-break-inside: auto;
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
            border-bottom: 1px solid #e2e8f0;
        }}

        tbody tr:nth-child(even) {{
            background: #f8f9fa;
        }}

        tbody tr {{
            page-break-inside: avoid;
        }}

        .party-card {{
            background: #f8f9fa;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #2c5282;
            padding: 1rem;
            margin-bottom: 1rem;
            page-break-inside: avoid;
        }}

        .party-type {{
            font-weight: 700;
            color: #2c5282;
            font-size: 11pt;
            margin-bottom: 0.5rem;
        }}

        .party-info {{
            font-size: 10pt;
            line-height: 1.8;
        }}

        .report-box {{
            background: white;
            border: 1px solid #e2e8f0;
            padding: 1rem;
            margin: 1rem 0;
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 9pt;
            page-break-inside: avoid;
        }}

        .external-report {{
            background: #fffaf0;
            border-left: 4px solid #ed8936;
            padding: 1rem;
            margin: 1rem 0;
            page-break-inside: avoid;
        }}

        .briefing-note {{
            background: #f0fff4;
            border: 2px solid #9ae6b4;
            padding: 1.5rem;
            margin: 1rem 0;
            page-break-inside: avoid;
        }}

        .briefing-header {{
            font-size: 14pt;
            font-weight: 700;
            color: #2c5282;
            margin-bottom: 1rem;
            text-align: center;
        }}

        .briefing-section {{
            margin: 1rem 0;
        }}

        .briefing-section h4 {{
            color: #2c5282;
            font-size: 11pt;
            margin-bottom: 0.5rem;
        }}

        .charge-box {{
            background: #fffaf0;
            border: 1px solid #fbd38d;
            border-left: 4px solid #ed8936;
            padding: 1rem;
            margin: 1rem 0;
            page-break-inside: avoid;
        }}

        .charge-number {{
            font-weight: 700;
            color: #2c5282;
            font-size: 11pt;
        }}

        .court-event {{
            background: #f8f9fa;
            border-left: 4px solid #2c5282;
            padding: 1rem;
            margin: 0.5rem 0;
            page-break-inside: avoid;
        }}

        .court-event-type {{
            font-weight: 700;
            color: #2c5282;
            font-size: 11pt;
        }}

        .conclusion-box {{
            background: #f0fff4;
            border: 2px solid #9ae6b4;
            padding: 1.5rem;
            margin: 1rem 0;
            page-break-inside: avoid;
        }}

        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 1rem;
            margin: 2rem 0;
        }}

        .summary-box {{
            background: #f8f9fa;
            border: 1px solid #e2e8f0;
            border-top: 3px solid #2c5282;
            padding: 1rem;
            text-align: center;
        }}

        .summary-number {{
            font-size: 24pt;
            font-weight: 700;
            color: #2c5282;
        }}

        .summary-label {{
            font-size: 9pt;
            color: #666;
            text-transform: uppercase;
            margin-top: 0.5rem;
        }}

        .footer {{
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 2px solid #2c5282;
            font-size: 9pt;
            color: #666;
            page-break-inside: avoid;
        }}

        .footer .warning {{
            background: #fff5f5;
            border-left: 4px solid #e53e3e;
            padding: 1rem;
            margin: 1rem 0;
        }}

        .footer .privilege {{
            background: #fffaf0;
            border-left: 4px solid #ed8936;
            padding: 1rem;
            margin: 1rem 0;
        }}

        .no-print {{
            position: fixed;
            bottom: 20px;
            right: 20px;
        }}

        @media print {{
            .no-print {{
                display: none;
            }}
        }}

        button {{
            background: #2c5282;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11pt;
            font-weight: 600;
        }}

        button:hover {{
            background: #1a365d;
        }}
    </style>
</head>
<body>
    <div class="no-print">
        <button onclick="window.print()">Print Disclosure Package</button>
    </div>

    <div class="header">
        <div class="icon">📁</div>
        <h1>WSCC Investigation Disclosure Package</h1>
        <p>Complete Investigation File for Legal and Administrative Review</p>
        <p>Workers' Safety & Compensation Commission</p>
        <p>Northwest Territories & Nunavut</p>
    </div>

    <div class="package-meta">
        <p><strong>Package ID:</strong> {package_id}</p>
        <p><strong>Case Number:</strong> {case['case_number']}</p>
        <p><strong>Generated:</strong> {now.strftime('%B %d, %Y at %I:%M %p')}</p>
        <p><strong>Territory:</strong> {case['territory']}</p>
        <p><strong>Package Type:</strong> Investigation Disclosure Package</p>
    </div>

    <!-- Section 1: Case Summary -->
    <div class="section">
        <h2>1. Case Summary</h2>
        <div class="info-grid">
            <div class="info-item">
                <label>Case Number (CAAPS)</label>
                <value>{case['case_number']}</value>
            </div>
            <div class="info-item">
                <label>Status</label>
                <value><span class="badge badge-{case['status'].lower().replace(' ', '-')}">{case['status']}</span></value>
            </div>
            <div class="info-item">
                <label>Territory</label>
                <value>{case['territory']}</value>
            </div>
            <div class="info-item">
                <label>Site Type</label>
                <value>{case.get('site_type', 'N/A')}</value>
            </div>
            <div class="info-item">
                <label>Location</label>
                <value>{case.get('location', 'N/A')}</value>
            </div>
            <div class="info-item">
                <label>Assigned Officers</label>
                <value>{officers_str}</value>
            </div>
        </div>
    </div>

    <!-- Section 2: Primary Parties -->
    <div class="section">
        <h2>2. Primary Parties</h2>
        <div class="info-grid">
            <div class="info-item">
                <label>Employer</label>
                <value>{case['employer']}</value>
            </div>
            <div class="info-item">
                <label>Worker / Injured Party</label>
                <value>{case['worker']}</value>
            </div>
        </div>
    </div>

    <!-- Section 3: All Involved Parties -->
    <div class="section">
        <h2>3. All Involved Parties</h2>
        {_render_involved_parties(case.get('involved_parties', []))}
    </div>

    <!-- Section 4: Incident Details -->
    <div class="section">
        <h2>4. Incident Details</h2>
        <div class="info-grid">
            <div class="info-item">
                <label>Incident Date</label>
                <value>{case.get('incident_date', 'N/A')}</value>
            </div>
            <div class="info-item">
                <label>Date Reported</label>
                <value>{case.get('reported_date', 'N/A')}</value>
            </div>
            <div class="info-item">
                <label>Reported to CSO</label>
                <value>{case.get('reported_to_cso_date', 'N/A')}</value>
            </div>
            <div class="info-item">
                <label>Incident Type</label>
                <value>{case.get('incident_type', 'N/A')}</value>
            </div>
        </div>
        <div style="margin-top: 1rem;">
            <h3>Description</h3>
            <p>{case.get('description', 'No description provided.')}</p>
        </div>
    </div>

    <!-- Section 5: Statute of Limitations -->
    <div class="section">
        <h2>5. Statute of Limitations</h2>
        <div class="statute-box {status_class}">
            <h3>Status: {status_text}</h3>
            <div class="statute-grid">
                <div class="statute-item">
                    <div class="statute-label">Start Date</div>
                    <div class="statute-number" style="font-size: 12pt;">{start_date}</div>
                </div>
                <div class="statute-item">
                    <div class="statute-label">Deadline (365 Days)</div>
                    <div class="statute-number" style="font-size: 12pt;">{deadline_str}</div>
                </div>
                <div class="statute-item">
                    <div class="statute-label">Days Elapsed</div>
                    <div class="statute-number">{days_elapsed}</div>
                </div>
                <div class="statute-item">
                    <div class="statute-label">Days Remaining</div>
                    <div class="statute-number">{max(0, days_remaining)}</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Section 6: Timeline of Events -->
    <div class="section">
        <h2>6. Timeline of Events</h2>
        {_render_timeline(case.get('timelines', []))}
    </div>

    <!-- Section 7: Investigation Reports -->
    <div class="section">
        <h2>7. Investigation Reports</h2>
        {_render_reports(case.get('reports', []))}
    </div>

    <!-- Section 8: Communications Log -->
    <div class="section">
        <h2>8. Communications Log</h2>
        {_render_communications(case.get('communications', []))}
    </div>

    <!-- Section 9: External Reports -->
    <div class="section">
        <h2>9. External Reports</h2>
        {_render_external_reports(case.get('external_reports', []))}
    </div>

    <!-- Section 10: Briefing Note -->
    <div class="section">
        <h2>10. Briefing Note</h2>
        {_render_briefing_note(case.get('briefing_note', ''))}
    </div>

    <!-- Section 11: Evidence Log -->
    <div class="section">
        <h2>11. Evidence Log</h2>
        {_render_exhibits(exhibits)}
    </div>

    <!-- Section 12: Photographic Evidence -->
    <div class="section">
        <h2>12. Photographic Evidence</h2>
        {_render_photos(case.get('photos', []))}
    </div>

    <!-- Section 13: Charges Filed -->
    <div class="section">
        <h2>13. Charges Filed</h2>
        {_render_charges(case.get('charges', []))}
    </div>

    <!-- Section 14: Court Events Timeline -->
    <div class="section">
        <h2>14. Court Events Timeline</h2>
        {_render_court_events(case.get('court_events', []))}
    </div>

    <!-- Section 15: Court Information -->
    <div class="section">
        <h2>15. Court Information</h2>
        {_render_court_info(case.get('court', {}))}
    </div>

    <!-- Section 16: Case Conclusion -->
    <div class="section">
        <h2>16. Case Conclusion</h2>
        {_render_conclusion(case.get('conclusion', {}))}
    </div>

    <!-- Section 17: Investigation Tasks & Actions -->
    <div class="section">
        <h2>17. Investigation Tasks & Actions</h2>
        {_render_tasks(case.get('tasks', []))}
    </div>

    <!-- Section 18: Disclosure Package Summary -->
    <div class="section">
        <h2>18. Disclosure Package Summary</h2>
        <div class="summary-grid">
            <div class="summary-box">
                <div class="summary-number">{stats['involved_parties']}</div>
                <div class="summary-label">Involved Parties</div>
            </div>
            <div class="summary-box">
                <div class="summary-number">{stats['timeline_events']}</div>
                <div class="summary-label">Timeline Events</div>
            </div>
            <div class="summary-box">
                <div class="summary-number">{stats['communications']}</div>
                <div class="summary-label">Communications</div>
            </div>
            <div class="summary-box">
                <div class="summary-number">{stats['reports']}</div>
                <div class="summary-label">Reports</div>
            </div>
            <div class="summary-box">
                <div class="summary-number">{stats['external_reports']}</div>
                <div class="summary-label">External Reports</div>
            </div>
            <div class="summary-box">
                <div class="summary-number">{stats['exhibits']}</div>
                <div class="summary-label">Evidence Items</div>
            </div>
            <div class="summary-box">
                <div class="summary-number">{stats['photos']}</div>
                <div class="summary-label">Photos</div>
            </div>
            <div class="summary-box">
                <div class="summary-number">{stats['charges']}</div>
                <div class="summary-label">Charges</div>
            </div>
            <div class="summary-box">
                <div class="summary-number">{stats['court_events']}</div>
                <div class="summary-label">Court Events</div>
            </div>
            <div class="summary-box">
                <div class="summary-number">{stats['tasks']}</div>
                <div class="summary-label">Tasks</div>
            </div>
        </div>
    </div>

    <div class="footer">
        <h3>Disclosure Package Metadata</h3>
        <div class="info-grid">
            <div class="info-item">
                <label>Package ID</label>
                <value>{package_id}</value>
            </div>
            <div class="info-item">
                <label>Generation Date</label>
                <value>{now.strftime('%B %d, %Y at %I:%M %p')}</value>
            </div>
            <div class="info-item">
                <label>Case Number</label>
                <value>{case['case_number']}</value>
            </div>
            <div class="info-item">
                <label>Territory</label>
                <value>{case['territory']}</value>
            </div>
            <div class="info-item">
                <label>Assigned Officers</label>
                <value>{officers_str}</value>
            </div>
            <div class="info-item">
                <label>Package Type</label>
                <value>Investigation Disclosure Package</value>
            </div>
        </div>

        <div class="warning">
            <strong>🔒 CONFIDENTIALITY NOTICE</strong><br>
            This disclosure package contains confidential and sensitive information related to a workplace safety investigation.
            It is intended solely for authorized legal and administrative review. Unauthorized disclosure, copying, or
            distribution of this material is strictly prohibited and may result in legal consequences.
        </div>

        <div class="privilege">
            <strong>⚖️ LEGAL PRIVILEGE</strong><br>
            This document may contain information subject to solicitor-client privilege, litigation privilege, or other legal
            protections. If you have received this disclosure package in error, please notify the Workers' Safety & Compensation
            Commission immediately and destroy all copies.
        </div>

        <p style="text-align: center; margin-top: 2rem;">
            <strong>Workers' Safety & Compensation Commission</strong><br>
            Northwest Territories & Nunavut<br>
            Generated: {now.strftime('%B %d, %Y at %I:%M %p')}
        </p>
    </div>
</body>
</html>
"""

    return html


def _render_involved_parties(parties: List[Dict]) -> str:
    """Render involved parties section"""
    if not parties:
        return "<p>No involved parties documented.</p>"

    html_parts = []
    party_type_icons = {
        'Person': '👤',
        'Company': '🏢',
        'Corporation': '🏛️',
        'Vehicle': '🚗',
        'Coroner': '⚖️',
        'Fire': '🚒',
        'Police': '🚓',
        'Address': '📍',
        'Other': '📋'
    }

    for party in parties:
        party_type = party.get('type', 'Other')
        icon = party_type_icons.get(party_type, '📋')

        html_parts.append(f"""
        <div class="party-card">
            <div class="party-type">{icon} {party_type}: {party.get('name', 'N/A')}</div>
            <div class="party-info">
                {f"<strong>Role:</strong> {party.get('role', 'N/A')}<br>" if party.get('role') else ''}
                {f"<strong>Phone:</strong> {party.get('phone', 'N/A')}<br>" if party.get('phone') else ''}
                {f"<strong>Email:</strong> {party.get('email', 'N/A')}<br>" if party.get('email') else ''}
                {f"<strong>Address:</strong> {party.get('address', 'N/A')}<br>" if party.get('address') else ''}
                {f"<strong>Details:</strong> {party.get('details', '')}" if party.get('details') else ''}
            </div>
        </div>
        """)

    return '\n'.join(html_parts)


def _render_timeline(events: List[Dict]) -> str:
    """Render timeline of events"""
    if not events:
        return "<p>No timeline events documented.</p>"

    # Sort by date
    sorted_events = sorted(events, key=lambda x: x.get('date', ''))

    html_parts = ['<div class="timeline">']
    for event in sorted_events:
        html_parts.append(f"""
        <div class="timeline-item">
            <div class="timeline-date">{event.get('date', 'N/A')}</div>
            <div class="timeline-event"><strong>{event.get('event', 'Event')}</strong></div>
            {f'<div class="timeline-event">{event.get("details", "")}</div>' if event.get('details') else ''}
        </div>
        """)
    html_parts.append('</div>')

    return '\n'.join(html_parts)


def _render_reports(reports: List[Dict]) -> str:
    """Render investigation reports"""
    if not reports:
        return "<p>No investigation reports filed.</p>"

    html_parts = []
    for i, report in enumerate(reports, 1):
        report_type = report.get('type', 'Report')
        html_parts.append(f"""
        <h3>Report {i}: <span class="badge badge-investigation">{report_type}</span> - {report.get('title', 'Untitled')}</h3>
        <p><strong>Date:</strong> {report.get('date', 'N/A')}</p>
        <div class="report-box">{report.get('content', 'No content provided.')}</div>
        """)

    return '\n'.join(html_parts)


def _render_communications(communications: List[Dict]) -> str:
    """Render communications log"""
    if not communications:
        return "<p>No communications documented.</p>"

    html_parts = ['<table><thead><tr>']
    html_parts.append('<th>Date & Time</th><th>Type</th><th>Direction</th><th>Contact</th><th>Organization</th><th>Subject</th><th>Summary</th><th>Attachments</th>')
    html_parts.append('</tr></thead><tbody>')

    for comm in communications:
        html_parts.append(f"""
        <tr>
            <td>{comm.get('date', 'N/A')} {comm.get('time', '')}</td>
            <td>{comm.get('type', 'N/A')}</td>
            <td>{comm.get('direction', 'N/A')}</td>
            <td>{comm.get('contact', 'N/A')}</td>
            <td>{comm.get('organization', 'N/A')}</td>
            <td>{comm.get('subject', 'N/A')}</td>
            <td>{comm.get('summary', 'N/A')}</td>
            <td>{comm.get('attachments', 'None')}</td>
        </tr>
        """)

    html_parts.append('</tbody></table>')
    return '\n'.join(html_parts)


def _render_external_reports(reports: List[Dict]) -> str:
    """Render external reports"""
    if not reports:
        return "<p>No external reports received.</p>"

    html_parts = []
    for report in reports:
        html_parts.append(f"""
        <div class="external-report">
            <h3>{report.get('source', 'External Agency')}: {report.get('title', 'Report')}</h3>
            <p><strong>Report Type:</strong> {report.get('report_type', 'N/A')}</p>
            <p><strong>Report Number:</strong> {report.get('report_number', 'N/A')}</p>
            <p><strong>Summary:</strong> {report.get('summary', 'No summary provided.')}</p>
            {f"<p><strong>Attachment:</strong> {report.get('attachment_path', 'N/A')}</p>" if report.get('attachment_path') else ''}
        </div>
        """)

    return '\n'.join(html_parts)


def _render_briefing_note(briefing_note: str) -> str:
    """Render briefing note"""
    if not briefing_note:
        return "<p>No briefing note available.</p>"

    try:
        note = json.loads(briefing_note) if isinstance(briefing_note, str) else briefing_note
    except:
        return f"<div class='briefing-note'><pre>{briefing_note}</pre></div>"

    return f"""
    <div class="briefing-note">
        <div class="briefing-header">{note.get('title', 'BRIEFING NOTE')}</div>
        <div class="briefing-section">
            <h4>Issue</h4>
            <p>{note.get('issue', 'N/A')}</p>
        </div>
        <div class="briefing-section">
            <h4>Key Messages</h4>
            <ul>
            {"".join([f"<li>{msg}</li>" for msg in note.get('key_messages', [])])}
            </ul>
        </div>
        <div class="briefing-section">
            <h4>Current Status</h4>
            <p style="background: #fff5f5; padding: 0.5rem; border-left: 4px solid #e53e3e;">
                {note.get('current_status', 'N/A')}
            </p>
        </div>
        <div class="briefing-section">
            <h4>Background</h4>
            <p>{note.get('background', 'N/A')}</p>
        </div>
        <p style="text-align: right; margin-top: 1rem; font-size: 9pt; color: #666;">
            Generated by: {note.get('generated_by', 'N/A')} | Date: {note.get('date', 'N/A')}
        </p>
    </div>
    """


def _render_exhibits(exhibits: List[Dict]) -> str:
    """Render evidence log"""
    if not exhibits:
        return "<p>No evidence items documented.</p>"

    html_parts = ['<table><thead><tr>']
    html_parts.append('<th>Exhibit #</th><th>Type</th><th>Category</th><th>Description</th><th>Seized Date</th><th>Seized By</th><th>Current Location</th><th>Status</th>')
    html_parts.append('</tr></thead><tbody>')

    for exhibit in exhibits:
        ex_type = exhibit.get('exhibit_type', 'N/A')
        status = exhibit.get('current_status', 'CUSTODY')

        html_parts.append(f"""
        <tr>
            <td><strong>{exhibit.get('exhibit_number', 'N/A')}</strong></td>
            <td><span class="badge badge-{ex_type.lower()}">{ex_type}</span></td>
            <td>{exhibit.get('category', 'N/A')}</td>
            <td>{exhibit.get('description', 'N/A')}</td>
            <td>{exhibit.get('seized_date', 'N/A')}</td>
            <td>{exhibit.get('seized_by', 'N/A')}</td>
            <td>{exhibit.get('current_location', 'N/A')}</td>
            <td><span class="badge badge-{status.lower()}">{status}</span></td>
        </tr>
        """)

    html_parts.append('</tbody></table>')
    return '\n'.join(html_parts)


def _render_photos(photos: List[Dict]) -> str:
    """Render photographic evidence"""
    if not photos:
        return "<p>No photographic evidence available.</p>"

    return f"<p><strong>Total Photos:</strong> {len(photos)}</p><p>Photo attachments are included in physical disclosure package.</p>"


def _render_charges(charges: List[Dict]) -> str:
    """Render charges filed"""
    if not charges:
        return "<p>No charges filed.</p>"

    html_parts = []
    for i, charge in enumerate(charges, 1):
        html_parts.append(f"""
        <div class="charge-box">
            <div class="charge-number">Charge {i}: {charge.get('violation', 'Violation')}</div>
            <p><strong>Description:</strong> {charge.get('description', 'N/A')}</p>
            <p><strong>Legislation:</strong> {charge.get('legislation', 'N/A')}</p>
            <p><strong>Section:</strong> {charge.get('section', 'N/A')}</p>
            <p><strong>Potential Penalty:</strong> {charge.get('penalty', 'N/A')}</p>
        </div>
        """)

    return '\n'.join(html_parts)


def _render_court_events(events: List[Dict]) -> str:
    """Render court events timeline"""
    if not events:
        return "<p>No court proceedings documented.</p>"

    # Sort by date
    sorted_events = sorted(events, key=lambda x: x.get('date', ''))

    html_parts = []
    event_type_icons = {
        'Sent to Crown': '📤',
        'Crown Review Complete': '✅',
        'Charges Approved': '⚖️',
        'First Appearance': '🏛️',
        'Subsequent Appearance': '🏛️',
        'Trial Date Set': '📅',
        'Trial': '⚖️',
        'Sentencing': '📜',
        'Conclusion': '✅',
        'Family Update': '👨‍👩‍👧‍👦'
    }

    for event in sorted_events:
        event_type = event.get('event_type', 'Event')
        icon = event_type_icons.get(event_type, '📋')

        html_parts.append(f"""
        <div class="court-event">
            <div class="court-event-type">{icon} {event_type}</div>
            <p><strong>Date:</strong> {event.get('date', 'N/A')}</p>
            <p><strong>Description:</strong> {event.get('description', 'N/A')}</p>
            {f"<p><strong>Court:</strong> {event.get('court_name', 'N/A')}</p>" if event.get('court_name') else ''}
            {f"<p><strong>Outcome:</strong> {event.get('outcome', 'N/A')}</p>" if event.get('outcome') else ''}
            {f"<p><strong>Verdict:</strong> {event.get('verdict', 'N/A')}</p>" if event.get('verdict') else ''}
            {f"<p><strong>Sentence:</strong> {event.get('sentence', 'N/A')}</p>" if event.get('sentence') else ''}
        </div>
        """)

    return '\n'.join(html_parts)


def _render_court_info(court: Dict) -> str:
    """Render court information"""
    if not court or not any(court.values()):
        return "<p>No court information available.</p>"

    return f"""
    <div class="info-grid">
        <div class="info-item">
            <label>Court Date</label>
            <value>{court.get('court_date', 'N/A')}</value>
        </div>
        <div class="info-item">
            <label>Court Location</label>
            <value>{court.get('court_location', 'N/A')}</value>
        </div>
        <div class="info-item">
            <label>Outcome</label>
            <value>{court.get('outcome', 'N/A')}</value>
        </div>
        <div class="info-item">
            <label>Judge Presiding</label>
            <value>{court.get('judge', 'N/A')}</value>
        </div>
        <div class="info-item">
            <label>Prosecutor</label>
            <value>{court.get('prosecutor', 'N/A')}</value>
        </div>
        <div class="info-item">
            <label>Defense Attorney</label>
            <value>{court.get('defense_attorney', 'N/A')}</value>
        </div>
    </div>
    {f'<div style="margin-top: 1rem;"><h3>Court Notes</h3><p>{court.get("notes", "")}</p></div>' if court.get('notes') else ''}
    """


def _render_conclusion(conclusion: Dict) -> str:
    """Render case conclusion"""
    if not conclusion or not any(conclusion.values()):
        return "<p>Case not yet concluded.</p>"

    return f"""
    <div class="conclusion-box">
        <div class="info-grid">
            <div class="info-item">
                <label>Conclusion Date</label>
                <value>{conclusion.get('conclusion_date', 'N/A')}</value>
            </div>
            <div class="info-item">
                <label>Outcome</label>
                <value>{conclusion.get('outcome', 'N/A')}</value>
            </div>
            <div class="info-item">
                <label>Closed By</label>
                <value>{conclusion.get('closed_by', 'N/A')}</value>
            </div>
        </div>
        {f'<div style="margin-top: 1rem;"><h3>Findings</h3><p>{conclusion.get("findings", "")}</p></div>' if conclusion.get('findings') else ''}
        {f'<div style="margin-top: 1rem;"><h3>Recommendations</h3><p>{conclusion.get("recommendations", "")}</p></div>' if conclusion.get('recommendations') else ''}
        {f'<div style="margin-top: 1rem;"><h3>Follow-up Required</h3><p>{conclusion.get("follow_up", "")}</p></div>' if conclusion.get('follow_up') else ''}
    </div>
    """


def _render_tasks(tasks: List[Dict]) -> str:
    """Render investigation tasks"""
    if not tasks:
        return "<p>No tasks documented.</p>"

    html_parts = ['<table><thead><tr>']
    html_parts.append('<th>Task</th><th>Assigned To</th><th>Due Date</th><th>Priority</th><th>Status</th><th>Notes</th>')
    html_parts.append('</tr></thead><tbody>')

    for task in tasks:
        priority = task.get('priority', 'Medium')
        status = task.get('status', 'Pending')

        html_parts.append(f"""
        <tr>
            <td><strong>{task.get('title', 'Task')}</strong></td>
            <td>{task.get('assigned_to', 'N/A')}</td>
            <td>{task.get('due_date', 'N/A')}</td>
            <td><span class="badge badge-{priority.lower()}">{priority}</span></td>
            <td><span class="badge badge-{status.lower()}">{status}</span></td>
            <td>{task.get('notes', 'N/A')}</td>
        </tr>
        """)

    html_parts.append('</tbody></table>')
    return '\n'.join(html_parts)
