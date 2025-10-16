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
                involved_parties TEXT,
                communications TEXT,
                external_reports TEXT,
                court_events TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        # Add new columns if they don't exist (for existing databases)
        try:
            cursor.execute("ALTER TABLE cases ADD COLUMN involved_parties TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists

        try:
            cursor.execute("ALTER TABLE cases ADD COLUMN communications TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists

        try:
            cursor.execute("ALTER TABLE cases ADD COLUMN external_reports TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists

        try:
            cursor.execute("ALTER TABLE cases ADD COLUMN court_events TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists

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

        # Exhibits table (Evidence Management)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exhibits (
                exhibit_id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                exhibit_number TEXT NOT NULL,
                exhibit_type TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                seized_date TEXT NOT NULL,
                seized_by TEXT NOT NULL,
                seized_location TEXT,
                current_location TEXT NOT NULL,
                current_status TEXT NOT NULL DEFAULT 'CUSTODY',
                barcode TEXT,
                quantity INTEGER DEFAULT 1,
                unit TEXT DEFAULT 'item',
                weight REAL,
                dimensions TEXT,
                serial_number TEXT,
                make_model TEXT,
                condition_notes TEXT,
                photo_path TEXT,
                digital_file_path TEXT,
                hash_value TEXT,
                tags TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (case_id) REFERENCES cases(id)
            )
        ''')

        # Chain of Custody table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chain_of_custody (
                custody_id TEXT PRIMARY KEY,
                exhibit_id TEXT NOT NULL,
                action TEXT NOT NULL,
                action_date TEXT NOT NULL,
                performed_by TEXT NOT NULL,
                received_by TEXT,
                from_location TEXT,
                to_location TEXT,
                reason TEXT NOT NULL,
                method TEXT,
                witness TEXT,
                authorized_by TEXT,
                temperature TEXT,
                seal_number TEXT,
                condition_before TEXT,
                condition_after TEXT,
                notes TEXT,
                photo_path TEXT,
                signature_path TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (exhibit_id) REFERENCES exhibits(exhibit_id)
            )
        ''')

        # Evidence Storage table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evidence_storage (
                storage_id TEXT PRIMARY KEY,
                location_name TEXT NOT NULL,
                location_type TEXT NOT NULL,
                capacity INTEGER,
                current_count INTEGER DEFAULT 0,
                access_level TEXT,
                temperature_controlled INTEGER DEFAULT 0,
                secure_locked INTEGER DEFAULT 1,
                notes TEXT,
                created_at TEXT NOT NULL
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
                    'involved_parties': json.dumps([]),
                    'communications': json.dumps([]),
                    'external_reports': json.dumps([]),
                    'court_events': json.dumps([]),
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
                    'involved_parties': json.dumps([]),
                    'communications': json.dumps([]),
                    'external_reports': json.dumps([]),
                    'court_events': json.dumps([]),
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
                                     involved_parties, communications, external_reports, court_events,
                                     created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (case['id'], case['case_number'], case['territory'], case['employer'],
                      case['worker'], case['incident_date'], case['reported_date'],
                      case['status'], case['priority'], case['description'],
                      case['assigned_officers'], case['timelines'], case['reports'],
                      case['tasks'], case['evidence'], case['photos'], case['charges'],
                      case['court'], case['conclusion'], case['briefing_note'],
                      case['involved_parties'], case['communications'], case['external_reports'],
                      case['court_events'], case['created_at'], case['updated_at']))

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
                         'evidence', 'photos', 'charges', 'involved_parties',
                         'communications', 'external_reports', 'court_events']:
                if case.get(field):
                    case[field] = json.loads(case[field])
                else:
                    case[field] = []
            for field in ['court', 'conclusion']:
                if case.get(field):
                    case[field] = json.loads(case[field])
                else:
                    case[field] = {}
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
                     'evidence', 'photos', 'charges', 'involved_parties',
                     'communications', 'external_reports', 'court_events']:
            if case.get(field):
                case[field] = json.loads(case[field])
            else:
                case[field] = []
        for field in ['court', 'conclusion']:
            if case.get(field):
                case[field] = json.loads(case[field])
            else:
                case[field] = {}

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
                         'evidence', 'photos', 'charges', 'involved_parties',
                         'communications', 'external_reports', 'court_events',
                         'court', 'conclusion']:
                if field in case_data and case_data[field]:
                    case_data[field] = json.dumps(case_data[field])
                else:
                    case_data[field] = json.dumps([]) if field not in ['court', 'conclusion'] else json.dumps({})

            cursor.execute('''
                INSERT INTO cases (id, case_number, territory, employer, worker,
                                 incident_date, reported_date, status, priority, description,
                                 assigned_officers, timelines, reports, tasks, evidence,
                                 photos, charges, court, conclusion, briefing_note,
                                 involved_parties, communications, external_reports, court_events,
                                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                  case_data.get('involved_parties', '[]'), case_data.get('communications', '[]'),
                  case_data.get('external_reports', '[]'), case_data.get('court_events', '[]'),
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
                         'evidence', 'photos', 'charges', 'court', 'conclusion',
                         'involved_parties', 'communications', 'external_reports', 'court_events']:
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

    # ==================== EVIDENCE MANAGEMENT ====================

    # EXHIBITS

    def get_next_exhibit_number(self, year: int = None) -> str:
        """Generate next exhibit number for the year"""
        if year is None:
            year = datetime.now().year

        conn = self.get_connection()
        cursor = conn.cursor()

        # Get count of exhibits for this year
        cursor.execute('''
            SELECT COUNT(*) FROM exhibits
            WHERE exhibit_number LIKE ?
        ''', (f'E-{year}-%',))

        count = cursor.fetchone()[0] + 1
        conn.close()

        return f'E-{year}-{count:03d}'

    def add_exhibit(self, exhibit: Dict) -> bool:
        """Add new exhibit"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO exhibits (exhibit_id, case_id, exhibit_number, exhibit_type,
                                    category, description, seized_date, seized_by, seized_location,
                                    current_location, current_status, barcode, quantity, unit,
                                    weight, dimensions, serial_number, make_model, condition_notes,
                                    photo_path, digital_file_path, hash_value, tags,
                                    created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                exhibit.get('exhibit_id'),
                exhibit.get('case_id'),
                exhibit.get('exhibit_number'),
                exhibit.get('exhibit_type'),
                exhibit.get('category'),
                exhibit.get('description'),
                exhibit.get('seized_date'),
                exhibit.get('seized_by'),
                exhibit.get('seized_location', ''),
                exhibit.get('current_location'),
                exhibit.get('current_status', 'CUSTODY'),
                exhibit.get('barcode', ''),
                exhibit.get('quantity', 1),
                exhibit.get('unit', 'item'),
                exhibit.get('weight'),
                exhibit.get('dimensions', ''),
                exhibit.get('serial_number', ''),
                exhibit.get('make_model', ''),
                exhibit.get('condition_notes', ''),
                exhibit.get('photo_path', ''),
                exhibit.get('digital_file_path', ''),
                exhibit.get('hash_value', ''),
                exhibit.get('tags', ''),
                exhibit.get('created_at'),
                exhibit.get('updated_at')
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e

    def get_exhibits_by_case(self, case_id: str) -> List[Dict]:
        """Get all exhibits for a case"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM exhibits WHERE case_id = ? ORDER BY exhibit_number', (case_id,))

        columns = [desc[0] for desc in cursor.description]
        exhibits = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return exhibits

    def get_exhibit_by_id(self, exhibit_id: str) -> Optional[Dict]:
        """Get exhibit by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM exhibits WHERE exhibit_id = ?', (exhibit_id,))

        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        columns = [desc[0] for desc in cursor.description]
        exhibit = dict(zip(columns, row))

        conn.close()
        return exhibit

    def update_exhibit(self, exhibit_id: str, updates: Dict) -> bool:
        """Update exhibit"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            updates['updated_at'] = datetime.now().isoformat()
            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [exhibit_id]

            cursor.execute(f'UPDATE exhibits SET {set_clause} WHERE exhibit_id = ?', values)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e

    def get_all_exhibits(self) -> List[Dict]:
        """Get all exhibits"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM exhibits ORDER BY created_at DESC')

        columns = [desc[0] for desc in cursor.description]
        exhibits = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return exhibits

    # CHAIN OF CUSTODY

    def add_custody_entry(self, entry: Dict) -> bool:
        """Add chain of custody entry"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO chain_of_custody (custody_id, exhibit_id, action, action_date,
                                            performed_by, received_by, from_location, to_location,
                                            reason, method, witness, authorized_by, temperature,
                                            seal_number, condition_before, condition_after, notes,
                                            photo_path, signature_path, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry.get('custody_id'),
                entry.get('exhibit_id'),
                entry.get('action'),
                entry.get('action_date'),
                entry.get('performed_by'),
                entry.get('received_by', ''),
                entry.get('from_location', ''),
                entry.get('to_location', ''),
                entry.get('reason'),
                entry.get('method', ''),
                entry.get('witness', ''),
                entry.get('authorized_by', ''),
                entry.get('temperature', ''),
                entry.get('seal_number', ''),
                entry.get('condition_before', ''),
                entry.get('condition_after', ''),
                entry.get('notes', ''),
                entry.get('photo_path', ''),
                entry.get('signature_path', ''),
                entry.get('created_at')
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e

    def get_custody_chain(self, exhibit_id: str) -> List[Dict]:
        """Get complete chain of custody for an exhibit"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM chain_of_custody
            WHERE exhibit_id = ?
            ORDER BY action_date ASC
        ''', (exhibit_id,))

        columns = [desc[0] for desc in cursor.description]
        chain = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return chain

    # EVIDENCE STORAGE

    def add_storage_location(self, location: Dict) -> bool:
        """Add evidence storage location"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO evidence_storage (storage_id, location_name, location_type,
                                            capacity, current_count, access_level,
                                            temperature_controlled, secure_locked, notes,
                                            created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                location.get('storage_id'),
                location.get('location_name'),
                location.get('location_type'),
                location.get('capacity', 0),
                location.get('current_count', 0),
                location.get('access_level', ''),
                location.get('temperature_controlled', 0),
                location.get('secure_locked', 1),
                location.get('notes', ''),
                location.get('created_at')
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e

    def get_all_storage_locations(self) -> List[Dict]:
        """Get all storage locations"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM evidence_storage ORDER BY location_name')

        columns = [desc[0] for desc in cursor.description]
        locations = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return locations

    def get_storage_location(self, storage_id: str) -> Optional[Dict]:
        """Get storage location by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM evidence_storage WHERE storage_id = ?', (storage_id,))

        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        columns = [desc[0] for desc in cursor.description]
        location = dict(zip(columns, row))

        conn.close()
        return location

    def update_storage_count(self, storage_id: str, count_change: int) -> bool:
        """Update storage location count"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE evidence_storage
                SET current_count = current_count + ?
                WHERE storage_id = ?
            ''', (count_change, storage_id))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e

    # EVIDENCE STATISTICS

    def get_evidence_statistics(self) -> Dict:
        """Get evidence statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()

        stats = {}

        # Total exhibits
        cursor.execute('SELECT COUNT(*) FROM exhibits')
        stats['total_exhibits'] = cursor.fetchone()[0]

        # By status
        cursor.execute('SELECT current_status, COUNT(*) FROM exhibits GROUP BY current_status')
        stats['by_status'] = dict(cursor.fetchall())

        # By type
        cursor.execute('SELECT exhibit_type, COUNT(*) FROM exhibits GROUP BY exhibit_type')
        stats['by_type'] = dict(cursor.fetchall())

        # By category
        cursor.execute('SELECT category, COUNT(*) FROM exhibits GROUP BY category')
        stats['by_category'] = dict(cursor.fetchall())

        # Storage locations
        cursor.execute('SELECT COUNT(*) FROM evidence_storage')
        stats['storage_locations'] = cursor.fetchone()[0]

        # Chain of custody entries
        cursor.execute('SELECT COUNT(*) FROM chain_of_custody')
        stats['custody_entries'] = cursor.fetchone()[0]

        conn.close()
        return stats
