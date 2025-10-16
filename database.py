"""
WSCC Investigation Management System - Database Layer
SQLite database for portable data persistence (no server required)
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

class Database:
    """SQLite database manager for WSCC Investigation Management System"""

    def __init__(self, db_path: str = "wscc_data.db"):
        """Initialize database connection and create tables if needed"""
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """Create database tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Cases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id TEXT PRIMARY KEY,
                case_number TEXT UNIQUE NOT NULL,
                territory TEXT NOT NULL,
                employer TEXT NOT NULL,
                worker TEXT NOT NULL,
                incident_date TEXT,
                reported_date TEXT,
                status TEXT DEFAULT 'Open',
                priority TEXT DEFAULT 'Medium',
                description TEXT,
                assigned_officers TEXT,
                timelines TEXT,
                reports TEXT,
                tasks TEXT,
                evidence TEXT,
                photos TEXT,
                charges TEXT,
                court TEXT,
                conclusion TEXT,
                briefing_note TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        # Officers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS officers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                work_location TEXT,
                experience TEXT,
                specialization TEXT,
                contact TEXT,
                active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        conn.commit()
        conn.close()

        # Initialize with demo data if database is empty
        self.init_demo_data()

    def init_demo_data(self):
        """Initialize database with demo data if empty"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Check if we have any cases
        cursor.execute('SELECT COUNT(*) FROM cases')
        case_count = cursor.fetchone()[0]

        if case_count == 0:
            # Add demo officers
            demo_officers = [
                {
                    'id': 'officer-001',
                    'name': 'Sarah Johnson',
                    'role': 'Senior Investigator',
                    'work_location': 'Yellowknife',
                    'experience': '8 years',
                    'specialization': 'Workplace Safety',
                    'contact': 'sjohnson@wscc.nt.ca',
                    'active': 1,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                },
                {
                    'id': 'officer-002',
                    'name': 'Michael Chen',
                    'role': 'Investigator',
                    'work_location': 'Iqaluit',
                    'experience': '5 years',
                    'specialization': 'Industrial Accidents',
                    'contact': 'mchen@wscc.nt.ca',
                    'active': 1,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
            ]

            for officer in demo_officers:
                cursor.execute('''
                    INSERT INTO officers (id, name, role, work_location, experience,
                                        specialization, contact, active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (officer['id'], officer['name'], officer['role'], officer['work_location'],
                      officer['experience'], officer['specialization'], officer['contact'],
                      officer['active'], officer['created_at'], officer['updated_at']))

            # Add demo cases
            demo_cases = [
                {
                    'id': 'case-001',
                    'case_number': 'WSCC-2024-001',
                    'territory': 'Northwest Territories',
                    'employer': 'Northern Mining Corp',
                    'worker': 'John Smith',
                    'incident_date': '2024-01-15',
                    'reported_date': '2024-01-16',
                    'status': 'Under Investigation',
                    'priority': 'High',
                    'description': 'Worker injury during mining operations. Fall from height.',
                    'assigned_officers': json.dumps(['officer-001']),
                    'timelines': json.dumps([]),
                    'reports': json.dumps([]),
                    'tasks': json.dumps([]),
                    'evidence': json.dumps([]),
                    'photos': json.dumps([]),
                    'charges': json.dumps([]),
                    'court': json.dumps({}),
                    'conclusion': json.dumps({}),
                    'briefing_note': '',
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                },
                {
                    'id': 'case-002',
                    'case_number': 'WSCC-2024-002',
                    'territory': 'Nunavut',
                    'employer': 'Arctic Construction Ltd',
                    'worker': 'Jane Doe',
                    'incident_date': '2024-02-20',
                    'reported_date': '2024-02-20',
                    'status': 'Open',
                    'priority': 'Medium',
                    'description': 'Equipment malfunction leading to worker injury.',
                    'assigned_officers': json.dumps(['officer-002']),
                    'timelines': json.dumps([]),
                    'reports': json.dumps([]),
                    'tasks': json.dumps([]),
                    'evidence': json.dumps([]),
                    'photos': json.dumps([]),
                    'charges': json.dumps([]),
                    'court': json.dumps({}),
                    'conclusion': json.dumps({}),
                    'briefing_note': '',
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
            ]

            for case in demo_cases:
                cursor.execute('''
                    INSERT INTO cases (id, case_number, territory, employer, worker,
                                     incident_date, reported_date, status, priority, description,
                                     assigned_officers, timelines, reports, tasks, evidence,
                                     photos, charges, court, conclusion, briefing_note,
                                     created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (case['id'], case['case_number'], case['territory'], case['employer'],
                      case['worker'], case['incident_date'], case['reported_date'],
                      case['status'], case['priority'], case['description'],
                      case['assigned_officers'], case['timelines'], case['reports'],
                      case['tasks'], case['evidence'], case['photos'], case['charges'],
                      case['court'], case['conclusion'], case['briefing_note'],
                      case['created_at'], case['updated_at']))

            conn.commit()

        conn.close()

    # ==================== CASES ====================

    def get_all_cases(self) -> List[Dict]:
        """Get all cases"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cases ORDER BY updated_at DESC')

        columns = [desc[0] for desc in cursor.description]
        cases = []
        for row in cursor.fetchall():
            case = dict(zip(columns, row))
            # Parse JSON fields
            for field in ['assigned_officers', 'timelines', 'reports', 'tasks',
                         'evidence', 'photos', 'charges']:
                if case[field]:
                    case[field] = json.loads(case[field])
            for field in ['court', 'conclusion']:
                if case[field]:
                    case[field] = json.loads(case[field])
            cases.append(case)

        conn.close()
        return cases

    def get_case_by_id(self, case_id: str) -> Optional[Dict]:
        """Get case by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cases WHERE id = ?', (case_id,))

        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        columns = [desc[0] for desc in cursor.description]
        case = dict(zip(columns, row))

        # Parse JSON fields
        for field in ['assigned_officers', 'timelines', 'reports', 'tasks',
                     'evidence', 'photos', 'charges']:
            if case[field]:
                case[field] = json.loads(case[field])
        for field in ['court', 'conclusion']:
            if case[field]:
                case[field] = json.loads(case[field])

        conn.close()
        return case

    def add_case(self, case: Dict) -> bool:
        """Add new case"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Serialize JSON fields
            case_data = case.copy()
            for field in ['assigned_officers', 'timelines', 'reports', 'tasks',
                         'evidence', 'photos', 'charges', 'court', 'conclusion']:
                if field in case_data and case_data[field]:
                    case_data[field] = json.dumps(case_data[field])
                else:
                    case_data[field] = json.dumps([]) if field != 'court' and field != 'conclusion' else json.dumps({})

            cursor.execute('''
                INSERT INTO cases (id, case_number, territory, employer, worker,
                                 incident_date, reported_date, status, priority, description,
                                 assigned_officers, timelines, reports, tasks, evidence,
                                 photos, charges, court, conclusion, briefing_note,
                                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (case_data.get('id'), case_data.get('case_number'),
                  case_data.get('territory'), case_data.get('employer'),
                  case_data.get('worker'), case_data.get('incident_date'),
                  case_data.get('reported_date'), case_data.get('status', 'Open'),
                  case_data.get('priority', 'Medium'), case_data.get('description', ''),
                  case_data.get('assigned_officers', '[]'), case_data.get('timelines', '[]'),
                  case_data.get('reports', '[]'), case_data.get('tasks', '[]'),
                  case_data.get('evidence', '[]'), case_data.get('photos', '[]'),
                  case_data.get('charges', '[]'), case_data.get('court', '{}'),
                  case_data.get('conclusion', '{}'), case_data.get('briefing_note', ''),
                  case_data.get('created_at'), case_data.get('updated_at')))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e

    def update_case(self, case_id: str, updates: Dict) -> bool:
        """Update existing case"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Serialize JSON fields if present
            updates_copy = updates.copy()
            for field in ['assigned_officers', 'timelines', 'reports', 'tasks',
                         'evidence', 'photos', 'charges', 'court', 'conclusion']:
                if field in updates_copy and updates_copy[field] is not None:
                    updates_copy[field] = json.dumps(updates_copy[field])

            # Build update query dynamically
            updates_copy['updated_at'] = datetime.now().isoformat()
            set_clause = ', '.join([f"{k} = ?" for k in updates_copy.keys()])
            values = list(updates_copy.values()) + [case_id]

            cursor.execute(f'UPDATE cases SET {set_clause} WHERE id = ?', values)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e

    def delete_case(self, case_id: str) -> bool:
        """Delete case"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cases WHERE id = ?', (case_id,))
        conn.commit()
        conn.close()
        return True

    # ==================== OFFICERS ====================

    def get_all_officers(self, active_only: bool = False) -> List[Dict]:
        """Get all officers"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if active_only:
            cursor.execute('SELECT * FROM officers WHERE active = 1 ORDER BY name')
        else:
            cursor.execute('SELECT * FROM officers ORDER BY name')

        columns = [desc[0] for desc in cursor.description]
        officers = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return officers

    def get_officer_by_id(self, officer_id: str) -> Optional[Dict]:
        """Get officer by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM officers WHERE id = ?', (officer_id,))

        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        columns = [desc[0] for desc in cursor.description]
        officer = dict(zip(columns, row))

        conn.close()
        return officer

    def add_officer(self, officer: Dict) -> bool:
        """Add new officer"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO officers (id, name, role, work_location, experience,
                                    specialization, contact, active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (officer.get('id'), officer.get('name'), officer.get('role'),
                  officer.get('work_location', ''), officer.get('experience', ''),
                  officer.get('specialization', ''), officer.get('contact', ''),
                  officer.get('active', 1), officer.get('created_at'),
                  officer.get('updated_at')))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e

    def update_officer(self, officer_id: str, updates: Dict) -> bool:
        """Update existing officer"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            updates['updated_at'] = datetime.now().isoformat()
            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [officer_id]

            cursor.execute(f'UPDATE officers SET {set_clause} WHERE id = ?', values)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e

    def delete_officer(self, officer_id: str) -> bool:
        """Delete officer (or mark as inactive)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        # Mark as inactive instead of deleting
        cursor.execute('UPDATE officers SET active = 0, updated_at = ? WHERE id = ?',
                      (datetime.now().isoformat(), officer_id))
        conn.commit()
        conn.close()
        return True

    # ==================== STATISTICS ====================

    def get_statistics(self) -> Dict:
        """Get dashboard statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()

        stats = {}

        # Total cases
        cursor.execute('SELECT COUNT(*) FROM cases')
        stats['total_cases'] = cursor.fetchone()[0]

        # Cases by status
        cursor.execute('SELECT status, COUNT(*) FROM cases GROUP BY status')
        stats['by_status'] = dict(cursor.fetchall())

        # Cases by territory
        cursor.execute('SELECT territory, COUNT(*) FROM cases GROUP BY territory')
        stats['by_territory'] = dict(cursor.fetchall())

        # Cases by priority
        cursor.execute('SELECT priority, COUNT(*) FROM cases GROUP BY priority')
        stats['by_priority'] = dict(cursor.fetchall())

        # Active officers
        cursor.execute('SELECT COUNT(*) FROM officers WHERE active = 1')
        stats['active_officers'] = cursor.fetchone()[0]

        conn.close()
        return stats

    # ==================== EXPORT/IMPORT ====================

    def export_to_json(self) -> Dict:
        """Export all data to JSON"""
        return {
            'cases': self.get_all_cases(),
            'officers': self.get_all_officers(),
            'exported_at': datetime.now().isoformat(),
            'version': '1.0'
        }

    def import_from_json(self, data: Dict) -> bool:
        """Import data from JSON (merges with existing data)"""
        try:
            # Import officers
            if 'officers' in data:
                for officer in data['officers']:
                    existing = self.get_officer_by_id(officer['id'])
                    if existing:
                        self.update_officer(officer['id'], officer)
                    else:
                        self.add_officer(officer)

            # Import cases
            if 'cases' in data:
                for case in data['cases']:
                    existing = self.get_case_by_id(case['id'])
                    if existing:
                        self.update_case(case['id'], case)
                    else:
                        self.add_case(case)

            return True
        except Exception as e:
            raise e
