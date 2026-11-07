#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Provenance-first electrical equipment catalogue stored in the app SQLite DB.

Seed entries represent documented PRODUCT FAMILIES, not individual rated SKUs.
Never infer ratings or standards compliance from family descriptions.
"""
import json
from datetime import datetime, timezone
from urllib.parse import urlsplit

SEED = (
    ('Schneider Electric', 'Acti9', 'Circuit protection', 'MCBs, RCDs and modular distribution product family',
     'https://www.se.com/be/en/download/document/Acti9_A9XPH212_CAT/'),
    ('ABB', 'SACE Tmax XT', 'Moulded-case circuit breaker', 'Low-voltage MCCB product family',
     'https://www.abb.com/global/en/areas/electrification/low-voltage/circuit-breakers'),
    ('Siemens', 'SENTRON miniature circuit breakers', 'Miniature circuit breaker', 'Low-voltage circuit protection family',
     'https://www.siemens.com/en-us/products/sentron/miniature-circuit-breakers/'),
)


def _source(url):
    if not isinstance(url, str) or len(url) > 2000:
        raise ValueError('Source URL is required')
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Use a public HTTPS source URL without embedded credentials')
    return url


class EquipmentCatalog:
    def __init__(self, database):
        self.db = database
        if database.connection is None:
            raise RuntimeError('Initialize the database first')
        database.connection.executescript('''
            CREATE TABLE IF NOT EXISTS equipment_catalog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                manufacturer TEXT NOT NULL,
                model TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                source_url TEXT NOT NULL,
                source_type TEXT NOT NULL,
                verified_utc TEXT,
                captured_utc TEXT NOT NULL,
                specifications_json TEXT NOT NULL DEFAULT '{}',
                UNIQUE(manufacturer, model, source_url)
            );
            CREATE INDEX IF NOT EXISTS idx_equipment_manufacturer ON equipment_catalog(manufacturer);
            CREATE INDEX IF NOT EXISTS idx_equipment_category ON equipment_catalog(category);
        ''')
        database.connection.commit()

    def add(self, manufacturer, model, category, description, source_url,
            specifications=None, source_type='manufacturer webpage', verified_utc=None):
        fields = (manufacturer, model, category, description, source_type)
        if any(not isinstance(x, str) or not x.strip() or len(x) > 5000 for x in fields):
            raise ValueError('All equipment fields must be nonempty text')
        _source(source_url)
        if specifications is None:
            specifications = {}
        if not isinstance(specifications, dict):
            raise ValueError('Specifications must be a dictionary')
        if any(not isinstance(k, str) or not isinstance(v, (str, int, float, bool, type(None)))
               for k, v in specifications.items()):
            raise ValueError('Specifications must be flat named values')
        payload = json.dumps(specifications, allow_nan=False)
        if len(payload) > 100000:
            raise ValueError('Specifications exceed limit')
        now = datetime.now(timezone.utc).isoformat()
        self.db.execute('''INSERT INTO equipment_catalog
            (manufacturer,model,category,description,source_url,source_type,verified_utc,captured_utc,specifications_json)
            VALUES (?,?,?,?,?,?,?,?,?)
            ON CONFLICT(manufacturer,model,source_url) DO NOTHING''',
            (manufacturer.strip(),model.strip(),category.strip(),description.strip(),
             source_url,source_type.strip(),verified_utc,now,payload))

    def seed_official_sources(self):
        for manufacturer, model, category, description, url in SEED:
            self.add(manufacturer, model, category, description, url, {}, 'manufacturer product family')

    def search(self, query='', limit=100):
        if not isinstance(query, str) or len(query) > 200:
            raise ValueError('Search must be text up to 200 characters')
        if not isinstance(limit, int) or not 1 <= limit <= 500:
            raise ValueError('Limit must be 1 to 500')
        pattern = '%' + query.replace('\\','\\\\').replace('%','\\%').replace('_','\\_') + '%'
        rows = self.db.fetch_all('''SELECT id,manufacturer,model,category,description,source_url,
            source_type,verified_utc,captured_utc,specifications_json FROM equipment_catalog
            WHERE manufacturer LIKE ? ESCAPE '\\' OR model LIKE ? ESCAPE '\\'
               OR category LIKE ? ESCAPE '\\' OR description LIKE ? ESCAPE '\\'
            ORDER BY manufacturer,model LIMIT ?''', (pattern,pattern,pattern,pattern,limit))
        columns = ('id','manufacturer','model','category','description','source_url',
                   'source_type','verified_utc','captured_utc','specifications')
        return [{**dict(zip(columns,row[:-1])), 'specifications':json.loads(row[-1])} for row in rows]
