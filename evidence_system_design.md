# Evidence Management System Design

## Overview
Comprehensive evidence/exhibit management system with full chain of custody tracking for court purposes.

---

## Core Requirements

### Evidence Types
1. **Physical Evidence**
   - Documents (paper)
   - Equipment/Tools
   - Materials/Substances
   - Clothing/PPE
   - Photographs (physical)
   - Audio/Video tapes
   - Other physical items

2. **Digital Evidence**
   - Digital photos
   - Videos
   - Audio recordings
   - Documents (PDF, Word, etc.)
   - Emails
   - Database exports
   - Screenshots
   - Log files

### Actions Tracked
1. **CREATED** - Evidence initially seized/collected
2. **MOVED** - Relocated to different storage
3. **TRANSFERRED** - Given to another person/agency
4. **EXAMINED** - Inspected/analyzed
5. **PHOTOGRAPHED** - Photos taken of evidence
6. **TESTED** - Lab testing/analysis
7. **RETURNED** - Returned to owner
8. **DESTROYED** - Properly disposed of
9. **SEALED** - Sealed for security
10. **UNSEALED** - Opened for examination

### Chain of Custody Elements
- **Who:** Officer/person taking action
- **What:** Evidence item affected
- **When:** Exact date/time (timestamp)
- **Where:** Location/storage
- **Why:** Reason for action
- **How:** Method/procedure
- **Witness:** Witnessing officer (if applicable)
- **Authorization:** Approving supervisor

---

## Database Schema

### exhibits table
```sql
CREATE TABLE exhibits (
    exhibit_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    exhibit_number TEXT NOT NULL,  -- E-2024-001, E-2024-002
    exhibit_type TEXT NOT NULL,     -- PHYSICAL or DIGITAL
    category TEXT NOT NULL,         -- Document, Equipment, etc.
    description TEXT NOT NULL,
    seized_date DATE NOT NULL,
    seized_by TEXT NOT NULL,        -- Officer name
    seized_location TEXT,
    current_location TEXT NOT NULL, -- Storage location
    current_status TEXT NOT NULL,   -- CUSTODY, RETURNED, DESTROYED
    barcode TEXT,                   -- Tracking barcode
    quantity INTEGER DEFAULT 1,
    unit TEXT DEFAULT 'item',       -- item, kg, liters, etc.
    weight REAL,
    dimensions TEXT,
    serial_number TEXT,
    make_model TEXT,
    condition_notes TEXT,
    photo_path TEXT,                -- Path to photo of evidence
    digital_file_path TEXT,         -- For digital evidence
    hash_value TEXT,                -- SHA-256 for digital evidence
    tags TEXT,                      -- Comma-separated tags
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(case_id)
);
```

### chain_of_custody table
```sql
CREATE TABLE chain_of_custody (
    custody_id TEXT PRIMARY KEY,
    exhibit_id TEXT NOT NULL,
    action TEXT NOT NULL,           -- CREATED, MOVED, TRANSFERRED, etc.
    action_date TIMESTAMP NOT NULL,
    performed_by TEXT NOT NULL,     -- Officer performing action
    received_by TEXT,               -- For TRANSFERRED
    from_location TEXT,
    to_location TEXT,
    reason TEXT NOT NULL,
    method TEXT,
    witness TEXT,                   -- Witnessing officer
    authorized_by TEXT,             -- Supervisor authorization
    temperature TEXT,               -- For temperature-sensitive items
    seal_number TEXT,               -- Evidence seal number
    condition_before TEXT,
    condition_after TEXT,
    notes TEXT,
    photo_path TEXT,                -- Photo of action
    signature_path TEXT,            -- Digital signature
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exhibit_id) REFERENCES exhibits(exhibit_id)
);
```

### evidence_storage table
```sql
CREATE TABLE evidence_storage (
    storage_id TEXT PRIMARY KEY,
    location_name TEXT NOT NULL,    -- Evidence Room A, Locker 5
    location_type TEXT NOT NULL,    -- ROOM, LOCKER, FREEZER, etc.
    capacity INTEGER,
    current_count INTEGER DEFAULT 0,
    access_level TEXT,              -- Who can access
    temperature_controlled BOOLEAN DEFAULT 0,
    secure_locked BOOLEAN DEFAULT 1,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## UI Components

### 1. Evidence Dashboard
- Total exhibits count
- Exhibits by status (In Custody, Returned, Destroyed)
- Exhibits by type (Physical, Digital)
- Storage locations summary
- Recent chain of custody events

### 2. Add New Evidence
**Form fields:**
- Case number (dropdown)
- Exhibit number (auto-generated)
- Type (Physical/Digital)
- Category (dropdown)
- Description (textarea)
- Seized date/time
- Seized by (officer dropdown)
- Seized location
- Current storage location
- Quantity & unit
- Barcode (optional)
- Photos (upload)
- Digital files (upload for digital evidence)
- Initial condition notes

### 3. Evidence Detail View
**Information displayed:**
- All exhibit details
- Current status banner
- Photos/files
- Complete chain of custody timeline
- Actions available:
  - Log new action
  - Move evidence
  - Transfer evidence
  - Return to owner
  - Mark for destruction
  - Print chain of custody report
  - Print evidence label

### 4. Chain of Custody Log Entry
**Form for logging action:**
- Action type (dropdown)
- Date/time (auto-filled, can adjust)
- Performed by (dropdown)
- Received by (for transfers)
- From location
- To location
- Reason (required)
- Method/procedure
- Witness (dropdown)
- Authorized by (dropdown)
- Seal number (if applicable)
- Condition before
- Condition after
- Photos (upload)
- Notes

### 5. Evidence Search
- Search by exhibit number
- Search by case number
- Search by description
- Filter by status
- Filter by type
- Filter by location
- Filter by date range

### 6. Reports for Court

**Chain of Custody Report:**
```
CHAIN OF CUSTODY REPORT
Workers' Safety & Compensation Commission

Case Number: WSCC-2024-001
Exhibit Number: E-2024-001
Description: Safety harness from incident scene

===========================================

[Complete timeline of every action taken]

Date/Time: 2024-10-15 14:30:00
Action: CREATED
Performed By: Officer John Smith
Location: Incident scene - 123 Main St
Reason: Evidence collection
Witness: Officer Jane Doe
Notes: Item photographed and sealed in evidence bag
Seal #: SEAL-001234

-------------------------------------------

Date/Time: 2024-10-15 16:45:00
Action: MOVED
Performed By: Evidence Custodian Sarah Johnson
From: Transport vehicle
To: Evidence Room A, Locker 5
Reason: Proper storage
Authorized By: Supervisor Mike Davis
Seal #: SEAL-001234 (verified intact)
Condition: Intact, no damage observed

-------------------------------------------

[Continues for every action...]

===========================================

CERTIFICATION

I certify that the above chain of custody is accurate and complete
to the best of my knowledge.

_____________________  _____________
Signature               Date

_____________________
Printed Name

Position: Evidence Custodian
```

**Evidence Summary Report:**
```
EVIDENCE SUMMARY
Case: WSCC-2024-001

Total Exhibits: 15
Physical: 12
Digital: 3

Status:
- In Custody: 13
- Returned: 1
- Destroyed: 1

[Table of all exhibits with key details]
```

---

## Business Rules

### Evidence Numbering
Format: `E-YYYY-XXX`
- E = Exhibit
- YYYY = Year
- XXX = Sequential number

Example: E-2024-001, E-2024-002

### Destruction Process
1. Supervisor approval required
2. Minimum retention period must pass
3. Must log destruction action
4. Witness required
5. Photos of destruction
6. Final report generated

### Transfer Process
1. Receiving party must be identified
2. Date/time logged
3. Receiving signature required (or name recorded)
4. Reason documented
5. Both parties' names logged

### Storage Rules
- Maximum capacity enforced
- Access level restrictions
- Temperature-sensitive items flagged
- Regular inventory checks

---

## Security Features

### Access Control
- Only assigned officers can create/modify
- Supervisors can authorize actions
- Audit log of all views
- Role-based permissions

### Data Integrity
- SHA-256 hash for digital evidence
- Immutable chain of custody records
- Timestamps cannot be altered
- All actions logged

### Compliance
- Court-admissible reports
- Complete audit trail
- No gaps in custody
- Proper authorization tracking

---

## Integration with Existing System

### Case Integration
- Evidence tab in case details
- Evidence count shown on dashboard
- Evidence mentioned in reports
- Links between cases and exhibits

### Officer Integration
- Officers assigned to cases can manage evidence
- Evidence actions tracked by officer
- Officer workload includes evidence tasks

### Reports Integration
- Evidence summary in case reports
- Chain of custody exports
- Court-ready PDF generation

---

## Implementation Priority

### Phase 1 (Core Features)
1. Database tables (exhibits, chain_of_custody, evidence_storage)
2. Add evidence form
3. View evidence details
4. Basic chain of custody logging
5. Evidence list/search

### Phase 2 (Advanced Features)
6. Chain of custody report generation
7. Evidence transfer workflow
8. Storage location management
9. Photo uploads
10. Digital file uploads

### Phase 3 (Court Features)
11. Evidence labels/barcodes
12. Destruction workflow
13. Court-ready PDF reports
14. Signature capture
15. Bulk operations

---

## Example Workflows

### Workflow 1: Collecting Physical Evidence
1. Officer seizes evidence at scene
2. Officer creates exhibit entry in system
   - Assigns exhibit number
   - Takes photos
   - Notes condition
   - Applies evidence seal
3. System automatically creates first chain of custody entry (CREATED)
4. Officer transports to evidence room
5. Evidence custodian logs receipt (MOVED action)
6. Evidence stored in designated location

### Workflow 2: Transferring Evidence for Testing
1. Officer requests lab testing
2. Supervisor authorizes transfer
3. Officer logs TRANSFERRED action
   - Notes receiving lab/person
   - Photographs sealed evidence
   - Records seal number
4. Lab receives evidence
5. Lab logs RECEIVED action
6. Lab conducts test
7. Lab logs TESTED action with results
8. Lab returns evidence
9. Officer logs RETURNED action

### Workflow 3: Returning Evidence to Owner
1. Case concluded
2. Supervisor authorizes return
3. Officer contacts owner
4. Owner signs release form
5. Officer logs RETURNED action
   - Owner name/signature
   - Date returned
   - Photos of handoff
6. Evidence status updated to RETURNED

### Workflow 4: Destroying Evidence
1. Retention period expires
2. Supervisor reviews and approves
3. Officer logs DESTROYED action
   - Destruction method
   - Witness present
   - Photos/video of destruction
   - Supervisor authorization
4. Evidence status updated to DESTROYED

---

## Court Admissibility Checklist

Evidence management system ensures:
- ✅ Complete chain of custody from seizure to present
- ✅ No gaps in custody timeline
- ✅ Every person who handled evidence is documented
- ✅ Every location is documented
- ✅ Every action has reason and authorization
- ✅ Condition at each stage is documented
- ✅ Seals and security measures are tracked
- ✅ Timestamps are accurate and immutable
- ✅ Witnesses are documented
- ✅ Photos provide visual verification
- ✅ Reports are professional and complete

---

## Future Enhancements

1. **Barcode Scanning**
   - Generate QR codes for exhibits
   - Mobile scanning app
   - Quick check-in/check-out

2. **Digital Signatures**
   - Touch-screen signature capture
   - Cryptographic signatures
   - Certificate-based authentication

3. **Mobile App**
   - Field evidence collection
   - Photo upload from scene
   - Chain of custody on mobile

4. **Integration**
   - Lab systems integration
   - Court filing systems
   - Property management systems

5. **Advanced Analytics**
   - Evidence statistics
   - Processing time tracking
   - Storage utilization
   - Officer performance metrics

---

This design provides a court-admissible, professional evidence management system that meets legal requirements while being user-friendly for investigators.
