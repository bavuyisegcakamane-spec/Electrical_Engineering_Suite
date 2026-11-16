"""User-supplied, provenance-tracked reference cable ampacities.

No default cable ratings are shipped. A source must be verified independently
for its edition, installation method, insulation and conductor configuration.
"""
import math


class CableReferenceRepository:
    def __init__(self, database):
        if database.connection is None:
            raise RuntimeError("Initialize database first")
        self.db = database.connection
        self.db.execute("""CREATE TABLE IF NOT EXISTS cable_reference_ratings (
            id INTEGER PRIMARY KEY,
            source_title TEXT NOT NULL,
            source_edition TEXT NOT NULL,
            table_reference TEXT NOT NULL,
            installation_method TEXT NOT NULL,
            conductor_description TEXT NOT NULL,
            material TEXT NOT NULL CHECK(material IN ('Copper','Aluminium')),
            area_mm2 REAL NOT NULL CHECK(area_mm2 > 0),
            reference_ampacity_a REAL NOT NULL CHECK(reference_ampacity_a > 0),
            source_verified INTEGER NOT NULL DEFAULT 0 CHECK(source_verified IN (0,1)),
            notes TEXT NOT NULL DEFAULT '')""")
        self.db.commit()

    def add(self, *, source_title, source_edition, table_reference,
            installation_method, conductor_description, material,
            area_mm2, reference_ampacity_a, notes=""):
        strings = (source_title, source_edition, table_reference,
                   installation_method, conductor_description)
        if any(not isinstance(s, str) or not s.strip() for s in strings):
            raise ValueError("Complete source citation and installation details are required.")
        if material not in ("Copper", "Aluminium"):
            raise ValueError("Invalid conductor material.")
        for value in (area_mm2, reference_ampacity_a):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise ValueError("Area and ampacity must be positive finite numbers.")
        with self.db:
            cur = self.db.execute("""INSERT INTO cable_reference_ratings
                (source_title,source_edition,table_reference,installation_method,
                conductor_description,material,area_mm2,reference_ampacity_a,notes)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (*[s.strip() for s in strings], material, area_mm2, reference_ampacity_a, str(notes)))
        return cur.lastrowid

    def list_ratings(self):
        cursor = self.db.execute("""SELECT id,source_title,source_edition,table_reference,
            installation_method,conductor_description,material,area_mm2,
            reference_ampacity_a,source_verified,notes
            FROM cable_reference_ratings ORDER BY id""")
        return [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]

    def get(self, rating_id):
        return next((r for r in self.list_ratings() if r["id"] == rating_id), None)
