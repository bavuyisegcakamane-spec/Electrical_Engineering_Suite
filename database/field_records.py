"""SQLite measurement and troubleshooting event log, independent of project JSON files."""
import math
from datetime import datetime, timezone


class FieldRecords:
    def __init__(self, database):
        self.database = database
        self.database.execute("""CREATE TABLE IF NOT EXISTS field_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            record_type TEXT NOT NULL CHECK(record_type IN ('measurement', 'fault')),
            equipment TEXT NOT NULL,
            description TEXT NOT NULL,
            value REAL,
            unit TEXT NOT NULL DEFAULT ''
        )""")

    def add(self, record_type, equipment, description, value=None, unit=""):
        if record_type not in ("measurement", "fault"):
            raise ValueError("Invalid record type")
        if not isinstance(equipment, str) or not equipment.strip() or len(equipment) > 120:
            raise ValueError("Equipment name must be 1-120 characters")
        if not isinstance(description, str) or not description.strip() or len(description) > 2000:
            raise ValueError("Description must be 1-2000 characters")
        if not isinstance(unit, str) or len(unit) > 30:
            raise ValueError("Unit must be at most 30 characters")
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)):
            raise ValueError("Measurement must be a finite number")
        if record_type == 'measurement' and value is None:
            raise ValueError("Measurements require a numeric value")
        timestamp = datetime.now(timezone.utc).isoformat()
        return self.database.execute(
            "INSERT INTO field_records(created_at, record_type, equipment, description, value, unit) VALUES (?, ?, ?, ?, ?, ?)",
            (timestamp, record_type, equipment.strip(), description.strip(), value, unit)).lastrowid

    def recent(self, limit=100):
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
            raise ValueError("Limit must be 1-1000")
        return self.database.fetch_all(
            "SELECT id, created_at, record_type, equipment, description, value, unit FROM field_records ORDER BY id DESC LIMIT ?",
            (limit,))
