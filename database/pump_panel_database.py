#  ____      ___        __  ____   _______ _____ ____
# |  _ \\    / \\ \\      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \\ \\ /\\ / /  |  _ \\    | |    | | \\___ \\
# |  _ <  / ___ \\ V  V /   | |_) |   | |    | |  ___) |
# |_| \\_\\/_/   \\_\\_/\\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Normalized, revision-friendly pump panel design BOM and component requirements.

This is a checklist and specification database, NOT an approved electrical design.
Component ratings and selected SKUs must be verified by a competent designer.
"""
import json
from datetime import datetime, timezone
from database.pump_panel_components import COMMON, BY_STARTER

EXTRA_COMMON = (
    ('Incoming cable termination', 'required'), ('Incoming surge coordination', 'review'),
    ('Main metering / CTs', 'optional'), ('Panel door interlock', 'review'),
    ('Phase loss / sequence monitor', 'review'), ('Under/overvoltage monitor', 'review'),
    ('PLC / pump controller', 'review'), ('HMI / local display', 'optional'),
    ('Automatic / manual selector', 'required'), ('Pump duty/standby alternation', 'review'),
    ('Pump start permissives', 'required'), ('Alarm annunciation', 'required'),
    ('Pressure transmitter', 'review'), ('Level switches / probes', 'review'),
    ('Flow switch / transmitter', 'review'), ('Control wiring / ferrules / labels', 'required'),
    ('Auxiliary relays / interface modules', 'review'), ('Door-mounted pilot lights', 'review'),
    ('Remote telemetry / communications', 'optional'), ('Panel heater / thermostat', 'review'),
    ('Cooling fan / filter', 'review'), ('Panel gland plate', 'required'),
    ('Cable duct / DIN rail', 'required'), ('Panel drawings / labels / schedule', 'required'),
    ('Factory testing and commissioning', 'required'), ('Earthing continuity / insulation tests', 'required'),
    ('Site short-circuit study', 'required'), ('Cable ampacity / voltage drop study', 'required'),
    ('Main / feeder protection coordination', 'required'), ('Supply harmonic / EMC assessment', 'review'),
)

STARTER_EXTRA = {
    'DOL': (('Contactor auxiliary contacts', 'required'), ('Local motor isolator', 'review')),
    'Star-delta': (('Open transition transient review', 'required'),
                   ('Contactor mechanical interlock', 'required'), ('Contactor electrical interlock', 'required'),
                   ('Motor winding delta-voltage compatibility', 'required')),
    'Soft starter': (('Soft starter duty / starts-per-hour check', 'required'),
                     ('Starter heat dissipation / enclosure check', 'required'),
                     ('Starter bypass scheme', 'review')),
    'VFD': (('VFD input protection coordination', 'required'),
            ('Drive output switching restrictions', 'required'),
            ('EMC cable / grounding plan', 'required'),
            ('Motor insulation / bearing protection review', 'review'),
            ('Drive thermal dissipation', 'required'), ('Drive bypass scheme', 'optional')),
}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


class PumpPanelDatabase:
    def __init__(self, database):
        if database.connection is None:
            raise RuntimeError('Initialize database first')
        from database.equipment_catalog import EquipmentCatalog
        EquipmentCatalog(database)  # Ensure referenced model catalogue exists first.
        self.db = database.connection
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS pump_component_types (
                id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE,
                scope TEXT NOT NULL CHECK(scope IN ('common','branch')),
                description TEXT NOT NULL DEFAULT '');
            CREATE TABLE IF NOT EXISTS pump_panel_designs (
                id INTEGER PRIMARY KEY, title TEXT NOT NULL,
                voltage_v REAL NOT NULL CHECK(voltage_v > 0),
                main_breaker_a REAL NOT NULL CHECK(main_breaker_a > 0),
                created_utc TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'draft'
                CHECK(status IN ('draft','reviewed')));
            CREATE TABLE IF NOT EXISTS pump_panel_motors (
                id INTEGER PRIMARY KEY, panel_id INTEGER NOT NULL REFERENCES pump_panel_designs(id) ON DELETE CASCADE,
                position INTEGER NOT NULL CHECK(position BETWEEN 1 AND 4),
                power_kw REAL NOT NULL CHECK(power_kw BETWEEN 2.2 AND 45),
                starter TEXT NOT NULL CHECK(starter IN ('DOL','Star-delta','Soft starter','VFD')),
                nameplate_current_a REAL CHECK(nameplate_current_a > 0),
                UNIQUE(panel_id, position));
            CREATE TABLE IF NOT EXISTS pump_panel_bom (
                id INTEGER PRIMARY KEY, panel_id INTEGER NOT NULL REFERENCES pump_panel_designs(id) ON DELETE CASCADE,
                motor_position INTEGER CHECK(motor_position BETWEEN 1 AND 4),
                component_type_id INTEGER NOT NULL REFERENCES pump_component_types(id),
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                requirement TEXT NOT NULL CHECK(requirement IN ('required','review','optional')),
                selected_catalog_id INTEGER REFERENCES equipment_catalog(id),
                sizing_notes TEXT NOT NULL DEFAULT '', verification_status TEXT NOT NULL DEFAULT 'unverified'
                CHECK(verification_status IN ('unverified','reviewed','approved')),
                UNIQUE(panel_id, motor_position, component_type_id));
            CREATE INDEX IF NOT EXISTS idx_pump_bom_panel ON pump_panel_bom(panel_id);
            CREATE INDEX IF NOT EXISTS idx_pump_motors_panel ON pump_panel_motors(panel_id);
        ''')
        self._seed_types()

    def _seed_types(self):
        common = {name:'review' for name in COMMON}
        common.update(EXTRA_COMMON)
        branch = {name:'review' for names in BY_STARTER.values() for name in names}
        branch.update({name:status for rows in STARTER_EXTRA.values() for name,status in rows})
        with self.db:
            for scope, items in (('common',common),('branch',branch)):
                for name in items:
                    self.db.execute('INSERT OR IGNORE INTO pump_component_types(name,scope) VALUES (?,?)', (name,scope))

    def create_panel(self, title, pumps, voltage_v=400, main_breaker_a=150):
        from calculations.pump_panel import study_panel
        study_panel(pumps, voltage_v=voltage_v, main_breaker_a=main_breaker_a)
        if not isinstance(title,str) or not title.strip() or len(title)>200:
            raise ValueError('Panel title is required (max 200 characters)')
        with self.db:
            cur = self.db.execute('INSERT INTO pump_panel_designs(title,voltage_v,main_breaker_a,created_utc) VALUES (?,?,?,?)',
                                  (title.strip(),voltage_v,main_breaker_a,utc_now()))
            panel_id = cur.lastrowid
            common = {name:'review' for name in COMMON}
            common.update(EXTRA_COMMON)
            for name,status in common.items():
                self._add_bom(panel_id,None,name,status)
            for index,pump in enumerate(pumps,1):
                self.db.execute('INSERT INTO pump_panel_motors(panel_id,position,power_kw,starter) VALUES (?,?,?,?)',
                                (panel_id,index,pump.power_kw,pump.starter))
                branch = {name:'review' for name in BY_STARTER[pump.starter]}
                branch.update(STARTER_EXTRA[pump.starter])
                for name,status in branch.items():
                    self._add_bom(panel_id,index,name,status)
        return panel_id

    def _add_bom(self, panel_id,position,name,status):
        component_id = self.db.execute('SELECT id FROM pump_component_types WHERE name=?', (name,)).fetchone()[0]
        self.db.execute('INSERT INTO pump_panel_bom(panel_id,motor_position,component_type_id,quantity,requirement) VALUES (?,?,?,?,?)',
                        (panel_id,position,component_id,1,status))

    def get_bom(self, panel_id):
        rows = self.db.execute('''SELECT b.motor_position,t.name,b.quantity,b.requirement,
            b.selected_catalog_id,b.verification_status,b.sizing_notes
            FROM pump_panel_bom b JOIN pump_component_types t ON t.id=b.component_type_id
            WHERE b.panel_id=? ORDER BY b.motor_position,t.name''',(panel_id,)).fetchall()
        return [dict(zip(('motor_position','component','quantity','requirement',
                          'selected_catalog_id','verification_status','sizing_notes'),row)) for row in rows]

    def assign_catalog_model(self, bom_id, catalog_id, sizing_notes=''):
        if not isinstance(sizing_notes,str) or len(sizing_notes)>5000:
            raise ValueError('Sizing notes must be text under 5000 characters')
        with self.db:
            cur = self.db.execute('UPDATE pump_panel_bom SET selected_catalog_id=?, sizing_notes=?, verification_status=? WHERE id=?',
                                  (catalog_id,sizing_notes,'unverified',bom_id))
            if cur.rowcount != 1:
                raise ValueError('BOM item not found')
